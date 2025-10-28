# Usage Guide

This guide provides comprehensive instructions for using the SentAna-Kafka real-time sentiment analysis system.

## 🚀 Getting Started

### Prerequisites

Before using the system, ensure you have:
- Completed the [installation](INSTALLATION.md) process
- Kafka 4.1.0 running with KRaft mode
- Reddit API credentials configured in `.env` file
- All Python dependencies installed

### Starting the System

The SentAna-Kafka system consists of three components that must be started in order:

#### 1. Start Kafka (if not already running)

```bash
# Navigate to Kafka directory
cd /usr/local/kafka

# Start Kafka with KRaft mode
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

#### 2. Start the Producer

```bash
# Navigate to project directory
cd SentAna-Kafka

# Activate virtual environment (if not already active)
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Start the producer
python producer.py
```

**Expected Output**:
```
🚀 Producer starting...
Authenticating with Reddit...
✅ Authentication successful! Logged in as: your_username
Initializing Kafka producer...
Kafka producer initialized.
Streaming comments from r/all for keyword 'iPhone'...
-> Sent mention: t1_abc123
-> Sent mention: t1_def456
```

#### 3. Start the Analyzer

Open a new terminal and run:

```bash
# Navigate to project directory
cd SentAna-Kafka

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Start the analyzer
python analyzer.py
```

**Expected Output**:
```
🧠 Analyzer started! Waiting for messages...
Processed mention t1_abc123 -> Sentiment: Positive (0.6369)
Processed mention t1_def456 -> Sentiment: Negative (-0.3421)
```

#### 4. Start the Dashboard

Open a third terminal and run:

```bash
# Navigate to project directory
cd SentAna-Kafka

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Start the dashboard
python -m streamlit run dashboard.py
```

**Expected Output**:
```
📊 Dashboard started! Waiting for data...
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

Open your web browser and navigate to `http://localhost:8501` to view the dashboard.

## 📊 Dashboard Usage

### Main Interface

The dashboard provides two main visualization components:

#### 1. Sentiment Distribution Chart
- **Purpose**: Shows the real-time distribution of sentiment classes
- **Chart Type**: Bar chart
- **Data**: Count of Positive, Negative, and Neutral sentiments
- **Updates**: Automatically refreshes as new data arrives

#### 2. Latest Mentions Table
- **Purpose**: Displays the most recent analyzed comments
- **Columns**:
  - `sentiment_class`: Classified sentiment (Positive/Negative/Neutral)
  - `sentiment_score`: VADER compound score (-1.0 to 1.0)
  - `author`: Reddit username of comment author
  - `text`: Full text of the comment
- **Sorting**: Newest comments appear at the top
- **Limit**: Shows latest 10 mentions

### Interpreting Sentiment Scores

The VADER sentiment analyzer provides compound scores ranging from -1.0 to 1.0:

- **0.05 to 1.0**: Positive sentiment
  - 0.05-0.2: Mildly positive
  - 0.2-0.5: Moderately positive
  - 0.5-1.0: Strongly positive

- **-0.05 to 0.05**: Neutral sentiment
  - Near 0: Truly neutral or mixed sentiment

- **-1.0 to -0.05**: Negative sentiment
  - -0.05 to -0.2: Mildly negative
  - -0.2 to -0.5: Moderately negative
  - -0.5 to -1.0: Strongly negative

### Dashboard Features

#### Real-time Updates
- The dashboard automatically updates as new sentiment-analyzed comments arrive
- No manual refresh required
- Updates typically appear within seconds of comment processing

#### Responsive Design
- The dashboard adapts to different screen sizes
- Wide layout optimized for desktop viewing
- Mobile-friendly interface

#### Data Persistence
- Data is maintained in memory during the dashboard session
- Restarting the dashboard clears the accumulated data
- Historical data is retained in Kafka topics based on retention settings

## ⚙️ Configuration Options

### Customizing Keywords and Subreddits

#### Changing Target Keyword
Edit [`producer.py`](../producer.py) and modify:
```python
TARGET_KEYWORD = "iPhone"  # Change to your desired keyword
```

#### Monitoring Specific Subreddits
Edit [`producer.py`](../producer.py) and modify:
```python
TARGET_SUBREDDIT = "technology"  # Change from "all" to specific subreddit
```

**Popular subreddit options**:
- `all`: Monitor all subreddits
- `technology`: Technology discussions
- `apple`: Apple-related discussions
- `gadgets`: Gadget discussions
- `news`: News discussions

### Adjusting Sentiment Thresholds

Edit [`analyzer.py`](../analyzer.py) to modify sentiment classification:

```python
# Current thresholds
POSITIVE_THRESHOLD = 0.05   # Minimum score for positive classification
NEGATIVE_THRESHOLD = -0.05  # Maximum score for negative classification

# Example: More sensitive positive detection
POSITIVE_THRESHOLD = 0.01

# Example: More strict classification
POSITIVE_THRESHOLD = 0.1
NEGATIVE_THRESHOLD = -0.1
```

### Kafka Configuration

#### Changing Topic Names
You can customize Kafka topic names by updating the constants in each component:

**Producer** ([`producer.py`](../producer.py)):
```python
KAFKA_TOPIC = "custom-raw-mentions"
```

**Analyzer** ([`analyzer.py`](../analyzer.py)):
```python
INPUT_KAFKA_TOPIC = "custom-raw-mentions"
OUTPUT_KAFKA_TOPIC = "custom-analyzed-sentiment"
```

**Dashboard** ([`dashboard.py`](../dashboard.py)):
```python
KAFKA_TOPIC = "custom-analyzed-sentiment"
```

#### Multiple Keywords
To monitor multiple keywords, you can modify the producer:

```python
# In producer.py
TARGET_KEYWORDS = ["iPhone", "Android", "Samsung"]  # List of keywords

# In the streaming loop:
for comment in reddit.subreddit(TARGET_SUBREDDIT).stream.comments(skip_existing=True):
    if any(keyword.lower() in comment.body.lower() for keyword in TARGET_KEYWORDS):
        # Process comment
```

## 🔍 Monitoring and Debugging

### Checking System Status

#### Producer Status
- **Authentication**: Look for "✅ Authentication successful" message
- **Kafka Connection**: Check for "Kafka producer initialized" message
- **Streaming**: Monitor "-> Sent mention:" messages for activity

#### Analyzer Status
- **Kafka Consumer**: Look for "🧠 Analyzer started!" message
- **Processing**: Monitor "Processed mention" messages for activity
- **Sentiment Results**: Check sentiment classifications in output

#### Dashboard Status
- **Kafka Connection**: Look for "📊 Dashboard started!" message
- **Data Reception**: Monitor browser for chart updates
- **Error Messages**: Check terminal for any error output

### Common Issues and Solutions

#### No Data in Dashboard
**Symptoms**: Dashboard shows no data or charts are empty

**Troubleshooting Steps**:
1. Verify producer is running and sending messages
2. Check analyzer is processing messages
3. Confirm Kafka topics exist and have data
4. Check dashboard consumer connection

```bash
# Verify Kafka topics have data
cd /usr/local/kafka
bin/kafka-console-consumer.sh --topic analyzed-sentiment --from-beginning --bootstrap-server localhost:9092
```

#### Reddit API Errors
**Symptoms**: Authentication failures or rate limiting

**Solutions**:
1. Verify Reddit API credentials in `.env`
2. Check Reddit app has correct permissions
3. Monitor for rate limiting messages
4. Ensure user agent string is properly formatted

#### Kafka Connection Issues
**Symptoms**: Connection refused or timeout errors

**Solutions**:
1. Verify Kafka broker is running
2. Check port 9092 availability
3. Confirm correct broker address in configuration
4. Test Kafka connectivity manually

### Performance Monitoring

#### Monitoring Throughput
```bash
# Check Kafka topic message rates
bin/kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic raw-reddit-mentions

# Monitor consumer lag
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group <group-id>
```

#### System Resource Monitoring
```bash
# Monitor CPU and memory usage
htop

# Monitor disk usage for Kafka logs
df -h /tmp/kafka-logs

# Monitor network connections
netstat -an | grep 9092
```

## 📈 Advanced Usage

### Data Export

#### Exporting Sentiment Data
You can modify the analyzer to export data to files:

```python
# Add to analyzer.py
import csv
from datetime import datetime

# In the processing loop
with open(f'sentiment_data_{datetime.now().strftime("%Y%m%d")}.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        data['id'],
        data['author'],
        sentiment_class,
        compound_score,
        datetime.now().isoformat()
    ])
```

#### Database Integration
For persistent storage, consider adding database integration:

```python
# Example with SQLite
import sqlite3

conn = sqlite3.connect('sentiment_data.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sentiments (
        id TEXT PRIMARY KEY,
        author TEXT,
        text TEXT,
        sentiment_class TEXT,
        sentiment_score REAL,
        timestamp REAL
    )
''')

# Insert data
cursor.execute('''
    INSERT INTO sentiments VALUES (?, ?, ?, ?, ?, ?)
''', (data['id'], data['author'], text, sentiment_class, compound_score, time.time()))
conn.commit()
```

### Scaling the System

#### Multiple Producers
Run multiple producer instances with different configurations:

```bash
# Terminal 1: Monitor "iPhone" in "technology"
TARGET_KEYWORD=iPhone TARGET_SUBREDDIT=technology python producer.py

# Terminal 2: Monitor "Android" in "gadgets"
TARGET_KEYWORD=Android TARGET_SUBREDDIT=gadgets python producer.py
```

#### Consumer Groups
Scale analyzer processing with consumer groups:

```python
# In analyzer.py
consumer = KafkaConsumer(
    INPUT_KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    group_id='sentiment-analyzer-group'  # Same group ID for load balancing
)
```

### Custom Sentiment Analysis

#### Using Different Sentiment Libraries
Replace VADER with other sentiment analysis libraries:

```python
# Example with TextBlob
from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity
```

#### Machine Learning Models
Integrate custom ML models for sentiment analysis:

```python
# Example with scikit-learn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Load pre-trained model
model = joblib.load('sentiment_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

def ml_sentiment_analysis(text):
    features = vectorizer.transform([text])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0].max()
    
    return prediction, probability
```

## 🛑 Stopping the System

### Graceful Shutdown

#### Stop Components in Reverse Order
1. **Dashboard**: Close browser tab or press Ctrl+C in terminal
2. **Analyzer**: Press Ctrl+C in analyzer terminal
3. **Producer**: Press Ctrl+C in producer terminal
4. **Kafka**: Press Ctrl+C in Kafka terminal (if needed)

#### Verify Clean Shutdown
```bash
# Check for remaining processes
ps aux | grep python
ps aux | grep kafka

# Check Kafka topics are intact
cd /usr/local/kafka
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Data Persistence
- **Kafka Topics**: Data persists according to retention policy
- **Dashboard**: In-memory data is lost on shutdown
- **Logs**: Check application logs for processing history

This usage guide should help you effectively operate and customize the SentAna-Kafka system for your specific needs. For additional technical details, refer to the [API Reference](API_REFERENCE.md) and [Architecture Overview](ARCHITECTURE.md).