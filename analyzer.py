from kafka import KafkaConsumer, KafkaProducer
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database import init_db, store_mention, get_db

# --- Configuration ---
INPUT_KAFKA_TOPIC = "raw-reddit-mentions"
OUTPUT_KAFKA_TOPIC = "analyzed-sentiment"
KAFKA_SERVER = "localhost:9092"

# --- Initialize Kafka Consumer and Producer ---
consumer = KafkaConsumer(
    INPUT_KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# --- Initialize Database ---
print("Initializing database...")
init_db()

# --- Initialize Sentiment Analyzer ---
analyzer = SentimentIntensityAnalyzer()

print("🧠 Analyzer started! Waiting for messages...")

# --- Main Processing Loop ---
try:
    # Get database session
    db_session = next(get_db())
    
    for message in consumer:
        # Get the raw data from the message
        data = message.value
        text = data['text']
        
        # Perform sentiment analysis
        sentiment_scores = analyzer.polarity_scores(text)
        compound_score = sentiment_scores['compound']
        
        # Classify sentiment based on the compound score
        if compound_score >= 0.05:
            sentiment_class = "Positive"
        elif compound_score <= -0.05:
            sentiment_class = "Negative"
        else:
            sentiment_class = "Neutral"
            
        # Create the enriched payload
        enriched_data = {
            'id': data['id'],
            'author': data['author'],
            'text': text,
            'url': f"https://reddit.com{data['url']}",
            'sentiment_class': sentiment_class,
            'sentiment_score': compound_score,
            'created_utc': data['created_utc']
        }
        
        # Store in database
        db_success = store_mention(db_session, enriched_data)
        
        # Send the data to the output topic
        producer.send(OUTPUT_KAFKA_TOPIC, enriched_data)
        
        # Print to console for feedback
        db_status = "✅ DB" if db_success else "❌ DB"
        print(f"Processed mention {data['id']} -> Sentiment: {sentiment_class} ({compound_score}) [{db_status}]")

except Exception as e:
    print(f"❌ An error occurred: {e}")
finally:
    consumer.close()
    producer.close()
    if 'db_session' in locals():
        db_session.close()
    print("Analyzer closed.")