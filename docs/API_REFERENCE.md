# API Reference & Technical Documentation

This document provides detailed technical documentation for each component of the SentAna-Kafka system.

## 📋 Table of Contents

- [Producer Module](#producer-module)
- [Analyzer Module](#analyzer-module)
- [Dashboard Module](#dashboard-module)
- [Kafka Message Formats](#kafka-message-formats)
- [Configuration Reference](#configuration-reference)

---

## Producer Module

### File: [`producer.py`](../producer.py)

The producer module handles Reddit API integration and streams comments to Kafka.

#### Dependencies

```python
import praw                           # Reddit API wrapper
from praw.exceptions import PRAWException  # Reddit API exceptions
from kafka import KafkaProducer       # Kafka producer client
import json                           # JSON serialization
import time                           # Time utilities
import os                             # Environment variables
from dotenv import load_dotenv        # Environment variable loading
```

#### Configuration Constants

| Constant | Type | Default | Description |
|----------|------|---------|-------------|
| `TARGET_KEYWORD` | str | "iPhone" | Keyword to search for in comments |
| `TARGET_SUBREDDIT` | str | "all" | Subreddit to monitor |
| `KAFKA_TOPIC` | str | "raw-reddit-mentions" | Output Kafka topic |
| `KAFKA_SERVER` | str | "localhost:9092" | Kafka bootstrap server |

#### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `REDDIT_CLIENT_ID` | Yes | Reddit API client ID |
| `REDDIT_CLIENT_SECRET` | Yes | Reddit API client secret |
| `REDDIT_USER_AGENT` | Yes | Reddit API user agent string |
| `REDDIT_USERNAME` | Yes | Reddit username |
| `REDDIT_PASSWORD` | Yes | Reddit password |

#### Core Functions

##### Reddit Authentication

```python
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    timeout=30 
)
```

**Purpose**: Establishes OAuth2 authentication with Reddit API.

**Parameters**:
- `client_id`: Reddit application client ID
- `client_secret`: Reddit application client secret
- `user_agent`: Application identifier for API requests
- `username`: Reddit account username
- `password`: Reddit account password
- `timeout`: Connection timeout in seconds

**Returns**: Authenticated Reddit instance

**Exceptions**: `PRAWException` on authentication failure

##### Kafka Producer Initialization

```python
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
```

**Purpose**: Creates Kafka producer instance with JSON serialization.

**Parameters**:
- `bootstrap_servers`: Kafka broker addresses
- `value_serializer`: Function to serialize message values

**Returns**: Configured KafkaProducer instance

##### Message Processing Loop

```python
for comment in reddit.subreddit(TARGET_SUBREDDIT).stream.comments(skip_existing=True):
    if TARGET_KEYWORD.lower() in comment.body.lower():
        # Process and send message
```

**Purpose**: Streams real-time comments and filters by keyword.

**Parameters**:
- `skip_existing=True`: Only process new comments

**Message Structure**:
```python
payload = {
    'id': comment.id,                    # Reddit comment ID
    'author': str(comment.author),        # Comment author username
    'text': comment.body,                 # Comment text content
    'url': comment.permalink,             # Comment permalink
    'created_utc': comment.created_utc    # Creation timestamp (UTC)
}
```

#### Error Handling

The producer implements resilient error handling with automatic retry:

```python
except PRAWException as e:
    print(f"🔌 A network error occurred: {e}")
    print("Retrying in 15 seconds...")
    time.sleep(15)
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
    print("Retrying in 15 seconds...")
    time.sleep(15)
```

---

## Analyzer Module

### File: [`analyzer.py`](../analyzer.py)

The analyzer module consumes raw comments, performs sentiment analysis, and publishes enriched results.

#### Dependencies

```python
from kafka import KafkaConsumer, KafkaProducer  # Kafka clients
import json                                    # JSON handling
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # Sentiment analysis
```

#### Configuration Constants

| Constant | Type | Default | Description |
|----------|------|---------|-------------|
| `INPUT_KAFKA_TOPIC` | str | "raw-reddit-mentions" | Source topic for raw comments |
| `OUTPUT_KAFKA_TOPIC` | str | "analyzed-sentiment" | Destination topic for analyzed sentiment |
| `KAFKA_SERVER` | str | "localhost:9092" | Kafka bootstrap server |

#### Core Components

##### Kafka Consumer Setup

```python
consumer = KafkaConsumer(
    INPUT_KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)
```

**Purpose**: Configures consumer to deserialize JSON messages from Kafka.

**Parameters**:
- `value_deserializer`: Function to decode and parse JSON messages

##### Kafka Producer Setup

```python
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
```

**Purpose**: Configures producer to serialize messages as JSON.

##### Sentiment Analyzer Initialization

```python
analyzer = SentimentIntensityAnalyzer()
```

**Purpose**: Creates VADER sentiment analysis instance.

#### Sentiment Analysis Process

##### Polarity Score Calculation

```python
sentiment_scores = analyzer.polarity_scores(text)
compound_score = sentiment_scores['compound']
```

**Returns**: Dictionary with sentiment scores:
- `compound`: Normalized compound score (-1 to 1)
- `pos`: Positive sentiment score
- `neg`: Negative sentiment score
- `neu`: Neutral sentiment score

##### Sentiment Classification

```python
if compound_score >= 0.05:
    sentiment_class = "Positive"
elif compound_score <= -0.05:
    sentiment_class = "Negative"
else:
    sentiment_class = "Neutral"
```

**Classification Rules**:
- **Positive**: compound score ≥ 0.05
- **Negative**: compound score ≤ -0.05
- **Neutral**: -0.05 < compound score < 0.05

##### Message Enrichment

```python
enriched_data = {
    'id': data['id'],                           # Original comment ID
    'author': data['author'],                   # Comment author
    'text': text,                               # Comment text
    'url': f"https://reddit.com{data['url']}",  # Full Reddit URL
    'sentiment_class': sentiment_class,          # Classified sentiment
    'sentiment_score': compound_score           # Compound score
}
```

#### Processing Loop

```python
for message in consumer:
    data = message.value
    text = data['text']
    
    # Perform sentiment analysis
    sentiment_scores = analyzer.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    
    # Classify and enrich
    # ...
    
    # Send to output topic
    producer.send(OUTPUT_KAFKA_TOPIC, enriched_data)
```

#### Resource Management

The analyzer implements proper resource cleanup:

```python
try:
    # Processing loop
    pass
except Exception as e:
    print(f"❌ An error occurred: {e}")
finally:
    consumer.close()
    producer.close()
    print("Analyzer closed.")
```

---

## Dashboard Module

### File: [`dashboard.py`](../dashboard.py)

The dashboard module provides a real-time web interface for visualizing sentiment analysis results.

#### Dependencies

```python
import streamlit as st              # Web app framework
from kafka import KafkaConsumer     # Kafka consumer
import json                         # JSON handling
import pandas as pd                 # Data manipulation
from collections import Counter     # Counting utilities
```

#### Configuration Constants

| Constant | Type | Default | Description |
|----------|------|---------|-------------|
| `KAFKA_TOPIC` | str | "analyzed-sentiment" | Input topic for analyzed sentiment |
| `KAFKA_SERVER` | str | "localhost:9092" | Kafka bootstrap server |

#### Streamlit Configuration

```python
st.set_page_config(layout="wide")
st.title("📊 Real-Time Reddit Sentiment Dashboard")
```

**Purpose**: Configures Streamlit page settings and title.

#### Kafka Consumer Setup

```python
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest'  # Start from beginning of topic
)
```

**Parameters**:
- `auto_offset_reset='earliest'`: Read from oldest available messages

#### Dashboard Components

##### Placeholders for Dynamic Content

```python
pie_chart_placeholder = st.empty()
data_frame_placeholder = st.empty()
```

**Purpose**: Creates empty containers that will be updated with content.

##### Data Storage

```python
all_data = []                    # Store all received messages
sentiment_counts = Counter()     # Track sentiment distribution
```

##### Visualization Updates

**Sentiment Distribution Chart**:
```python
df_counts = pd.DataFrame.from_dict(sentiment_counts, orient='index').reset_index()
df_counts.columns = ['Sentiment', 'Count']

with pie_chart_placeholder.container():
    st.markdown("### Sentiment Distribution")
    st.bar_chart(df_counts.set_index('Sentiment'))
```

**Latest Mentions Table**:
```python
with data_frame_placeholder.container():
    st.markdown("### Latest Mentions")
    df_display = pd.DataFrame(all_data).iloc[::-1].head(10)
    st.dataframe(df_display[['sentiment_class', 'sentiment_score', 'author', 'text']])
```

#### Main Processing Loop

```python
for message in consumer:
    data = message.value
    all_data.append(data)
    
    # Update sentiment counts
    sentiment_counts[data['sentiment_class']] += 1
    
    # Update visualizations
    # ...
```

---

## Kafka Message Formats

### Raw Reddit Mentions (Topic: `raw-reddit-mentions`)

```json
{
  "id": "t1_abc123",
  "author": "reddit_user",
  "text": "I really love my new iPhone camera!",
  "url": "/r/apple/comments/xyz789/comment/abc123/",
  "created_utc": 1634567890.0
}
```

**Field Descriptions**:
- `id`: Unique Reddit comment identifier
- `author`: Username of comment author
- `text`: Full text content of the comment
- `url`: Relative permalink to the comment
- `created_utc`: Unix timestamp in UTC

### Analyzed Sentiment (Topic: `analyzed-sentiment`)

```json
{
  "id": "t1_abc123",
  "author": "reddit_user",
  "text": "I really love my new iPhone camera!",
  "url": "https://reddit.com/r/apple/comments/xyz789/comment/abc123/",
  "sentiment_class": "Positive",
  "sentiment_score": 0.6369
}
```

**Field Descriptions**:
- `id`: Original Reddit comment identifier
- `author`: Username of comment author
- `text`: Full text content of the comment
- `url`: Full Reddit URL to the comment
- `sentiment_class`: Classified sentiment ("Positive", "Negative", "Neutral")
- `sentiment_score`: VADER compound score (-1.0 to 1.0)

---

## Configuration Reference

### Environment Variables (.env)

```env
# Reddit API Configuration
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=script:KafkaSentimentProject:v1.0 (by /u/your_username)
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### Application Configuration

#### Producer Configuration
```python
TARGET_KEYWORD = "iPhone"              # Keyword to monitor
TARGET_SUBREDDIT = "all"               # Subreddit to watch
KAFKA_TOPIC = "raw-reddit-mentions"     # Output topic
KAFKA_SERVER = "localhost:9092"         # Kafka broker
```

#### Analyzer Configuration
```python
INPUT_KAFKA_TOPIC = "raw-reddit-mentions"   # Source topic
OUTPUT_KAFKA_TOPIC = "analyzed-sentiment"   # Destination topic
KAFKA_SERVER = "localhost:9092"              # Kafka broker
```

#### Dashboard Configuration
```python
KAFKA_TOPIC = "analyzed-sentiment"    # Input topic
KAFKA_SERVER = "localhost:9092"        # Kafka broker
```

### Kafka Topic Configuration

#### Topic: `raw-reddit-mentions`
- **Purpose**: Store raw Reddit comments
- **Key**: None (null key)
- **Value**: JSON-serialized comment data
- **Retention**: Default (typically 7 days)
- **Partitions**: 1 (default)

#### Topic: `analyzed-sentiment`
- **Purpose**: Store sentiment-analyzed comments
- **Key**: None (null key)
- **Value**: JSON-serialized analyzed data
- **Retention**: Default (typically 7 days)
- **Partitions**: 1 (default)

### Performance Tuning Parameters

#### Kafka Producer Settings
```python
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    # Optional performance settings:
    # batch_size=16384,
    # linger_ms=10,
    # compression_type='gzip'
)
```

#### Kafka Consumer Settings
```python
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    # Optional performance settings:
    # auto_offset_reset='latest',
    # enable_auto_commit=True,
    # group_id='sentiment-analyzer-group'
)
```

This API reference provides comprehensive technical documentation for implementing, configuring, and extending the SentAna-Kafka system components.