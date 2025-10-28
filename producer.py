import praw
from praw.exceptions import PRAWException
from kafka import KafkaProducer
import json
import time
import os
from dotenv import load_dotenv


load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = "script:KafkaSentimentProject:v1.0 (by /u/Working-Minute-1495)"
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

# --- Configuration ---
TARGET_KEYWORD = "iPhone"
TARGET_SUBREDDIT = "all"
KAFKA_TOPIC = "raw-reddit-mentions"
KAFKA_SERVER = "localhost:9092"

print("🚀 Producer starting...")

# --- Main Resilient Loop ---
while True:
    try:
        # --- Step 1: Authenticate with Reddit ---
        print("Authenticating with Reddit...")
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            timeout=30 
        )
        authenticated_user = reddit.user.me()
        print(f"✅ Authentication successful! Logged in as: {authenticated_user}")

        # --- Step 2: Initialize Kafka Producer ---
        print("Initializing Kafka producer...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka producer initialized.")

        # --- Step 3: Start Streaming Loop ---
        print(f"Streaming comments from r/{TARGET_SUBREDDIT} for keyword '{TARGET_KEYWORD}'...")
        for comment in reddit.subreddit(TARGET_SUBREDDIT).stream.comments(skip_existing=True):
            if TARGET_KEYWORD.lower() in comment.body.lower():
                payload = {
                    'id': comment.id,
                    'author': str(comment.author),
                    'text': comment.body,
                    'url': comment.permalink,
                    'created_utc': comment.created_utc
                }
                producer.send(KAFKA_TOPIC, payload)
                print(f"-> Sent mention: {comment.id}")

    except PRAWException as e:
        print(f"🔌 A network error occurred: {e}")
        print("Retrying in 15 seconds...")
        time.sleep(15)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        print("Retrying in 15 seconds...")
        time.sleep(15)