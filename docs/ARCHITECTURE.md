# SentAna-Kafka Architecture Overview

This document provides a detailed technical overview of the SentAna-Kafka real-time sentiment analysis system.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Reddit API    │───▶│   Producer   │───▶│     Kafka       │───▶│   Analyzer    │───▶│   Dashboard     │
│                 │    │              │    │                 │    │              │    │                 │
│ • Comments      │    │ • Stream     │    │ • raw-reddit-   │    │ • Sentiment   │    │ • Real-time     │
│ • Subreddits    │    │ • Filter     │    │   mentions      │    │   Analysis    │    │   Visualization │
│ • Real-time     │    │ • Publish    │    │ • analyzed-     │    │ • Enrich      │    │ • Web UI        │
│                 │    │              │    │   sentiment     │    │ • Publish     │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘    └─────────────────┘
```

## 📦 Components

### 1. Producer ([`producer.py`](../producer.py))

**Purpose**: Streams Reddit comments containing target keywords to Kafka topics.

**Key Responsibilities**:
- Authenticate with Reddit API using OAuth2
- Stream real-time comments from specified subreddits
- Filter comments based on target keywords
- Serialize and publish filtered comments to Kafka
- Implement resilient error handling and reconnection logic

**Configuration**:
- `TARGET_KEYWORD`: Keyword to search for in comments
- `TARGET_SUBREDDIT`: Subreddit to monitor (default: "all")
- `KAFKA_TOPIC`: Output topic for raw mentions
- `KAFKA_SERVER`: Kafka bootstrap server

**Data Flow**:
```
Reddit API → Comment Stream → Keyword Filter → JSON Serialization → Kafka Topic
```

**Message Format**:
```json
{
  "id": "comment_id",
  "author": "username",
  "text": "comment body",
  "url": "permalink",
  "created_utc": 1234567890.0
}
```

### 2. Analyzer ([`analyzer.py`](../analyzer.py))

**Purpose**: Consumes raw comments, performs sentiment analysis, and publishes enriched results.

**Key Responsibilities**:
- Consume messages from raw comments topic
- Perform sentiment analysis using VADER
- Classify sentiment (Positive, Negative, Neutral)
- Enrich messages with sentiment data
- Publish analyzed results to output topic
- Handle graceful shutdown

**Configuration**:
- `INPUT_KAFKA_TOPIC`: Source topic for raw comments
- `OUTPUT_KAFKA_TOPIC`: Destination topic for analyzed sentiment
- `KAFKA_SERVER`: Kafka bootstrap server

**Sentiment Analysis Logic**:
- Uses VADER sentiment analyzer
- Compound score classification:
  - ≥ 0.05: Positive
  - ≤ -0.05: Negative
  - Between: Neutral

**Data Flow**:
```
Kafka Consumer → VADER Analysis → Sentiment Classification → Enrichment → Kafka Producer
```

**Output Message Format**:
```json
{
  "id": "comment_id",
  "author": "username",
  "text": "comment body",
  "url": "https://reddit.com/permalink",
  "sentiment_class": "Positive|Negative|Neutral",
  "sentiment_score": 0.1234
}
```

### 3. Dashboard ([`dashboard.py`](../dashboard.py))

**Purpose**: Real-time web interface for visualizing sentiment analysis results.

**Key Responsibilities**:
- Consume analyzed sentiment messages from Kafka
- Maintain in-memory data store for visualization
- Display real-time sentiment distribution charts
- Show latest mentions with sentiment data
- Provide interactive web interface using Streamlit

**Configuration**:
- `KAFKA_TOPIC`: Input topic for analyzed sentiment
- `KAFKA_SERVER`: Kafka bootstrap server

**Visualization Components**:
- **Sentiment Distribution**: Bar chart showing count of each sentiment class
- **Latest Mentions**: Table displaying recent comments with sentiment scores
- **Real-time Updates**: Automatic refresh as new data arrives

**Data Flow**:
```
Kafka Consumer → Data Aggregation → Visualization Update → Web Interface
```

## 🔄 Data Flow Pipeline

### Stage 1: Data Collection
1. Producer authenticates with Reddit API
2. Establishes real-time comment stream
3. Filters comments for target keywords
4. Publishes matching comments to `raw-reddit-mentions` topic

### Stage 2: Data Processing
1. Analyzer consumes messages from `raw-reddit-mentions`
2. Applies VADER sentiment analysis
3. Classifies sentiment and calculates compound score
4. Enriches message with sentiment data
5. Publishes to `analyzed-sentiment` topic

### Stage 3: Data Visualization
1. Dashboard consumes from `analyzed-sentiment` topic
2. Aggregates data in memory
3. Updates visualizations in real-time
4. Displays sentiment distribution and latest mentions

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.7+**: Primary programming language
- **Apache Kafka**: Distributed streaming platform
- **Reddit API**: Source of real-time comment data

### Libraries & Frameworks
- **PRAW**: Python Reddit API Wrapper
- **kafka-python**: Kafka client for Python
- **VADER**: Sentiment analysis library
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis

### Data Formats
- **JSON**: Message serialization format
- **UTF-8**: Text encoding standard

## 🔧 Configuration Management

### Environment Variables
Sensitive configuration is managed through `.env` file:
- Reddit API credentials
- Authentication tokens
- Connection parameters

### Application Constants
Non-sensitive configuration is defined as constants:
- Kafka topic names
- Server addresses
- Target keywords and subreddits

## 🚀 Deployment Considerations

### Scaling
- **Producer**: Can be horizontally scaled for multiple keywords/subreddits
- **Analyzer**: Can be scaled with consumer groups for parallel processing
- **Dashboard**: Single instance sufficient for visualization

### Fault Tolerance
- **Producer**: Implements automatic reconnection and retry logic
- **Analyzer**: Handles graceful shutdown and resource cleanup
- **Kafka**: Provides built-in replication and fault tolerance

### Performance
- **Throughput**: Limited by Reddit API rate limits and Kafka capacity
- **Latency**: Near real-time processing with minimal delays
- **Storage**: Kafka topics can be configured for retention policies

## 🔒 Security Considerations

### API Security
- Reddit API credentials stored in environment variables
- OAuth2 authentication for Reddit API access
- User agent string for API identification

### Data Security
- No sensitive data stored in application code
- Environment variables excluded from version control
- Kafka topics can be secured with ACLs if needed

## 📊 Monitoring & Observability

### Logging
Each component provides console output for:
- Connection status
- Message processing
- Error conditions
- Performance metrics

### Metrics
Key performance indicators:
- Message throughput rate
- Sentiment distribution
- Error rates
- Processing latency

## 🔄 Message Flow Example

```
1. Reddit Comment: "I love my new iPhone camera!"
2. Producer → Kafka: {"id": "abc123", "author": "user1", "text": "I love my new iPhone camera!", ...}
3. Analyzer: sentiment_scores = {'compound': 0.6369, 'pos': 0.636, 'neg': 0.0, 'neu': 0.364}
4. Analyzer → Kafka: {"id": "abc123", ..., "sentiment_class": "Positive", "sentiment_score": 0.6369}
5. Dashboard: Updates charts with new positive sentiment
```

This architecture provides a scalable, resilient, and real-time solution for Reddit sentiment analysis with clear separation of concerns and modular design.