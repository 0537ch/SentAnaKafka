# SentAna-Kafka: Real-Time Reddit Sentiment Analysis System with Database Integration

A distributed real-time sentiment analysis system that monitors Reddit comments for specific keywords, performs sentiment analysis using VADER, stores results in a TimescaleDB database, and visualizes the results through an enhanced web dashboard with historical analysis capabilities.

## 🏗️ Architecture Overview

This system consists of four main components:

1. **Producer** ([`producer.py`](producer.py)) - Streams Reddit comments containing target keywords to Kafka
2. **Analyzer** ([`analyzer.py`](analyzer.py)) - Consumes raw comments, performs sentiment analysis, stores in database, and publishes results
3. **Database** ([`database.py`](database.py)) - TimescaleDB integration for persistent storage and historical analysis
4. **Dashboard** ([`dashboard.py`](dashboard.py)) - Enhanced web interface with real-time and historical sentiment analysis

### System Flow

```
Reddit API → Producer → Kafka (raw-reddit-mentions) → Analyzer → Database + Kafka (analyzed-sentiment) → Dashboard
```

## ✨ Features

- **Real-time Processing**: Continuously monitors Reddit for new comments
- **Sentiment Analysis**: Uses VADER sentiment analyzer for accurate sentiment classification
- **Database Persistence**: TimescaleDB integration for historical data storage and analysis
- **Enhanced Dashboard**: Real-time and historical sentiment visualization with time-range filtering
- **Historical Analysis**: Track sentiment trends over hours, days, or weeks
- **Resilient Architecture**: Automatic error recovery and reconnection handling
- **Interactive Charts**: Plotly-powered visualizations with sentiment timelines
- **Configurable**: Easily modify target keywords, subreddits, and Kafka settings

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Docker and Docker Compose (recommended)
- Reddit API credentials (create a Reddit app at https://www.reddit.com/prefs/apps)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SentAna-Kafka
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Reddit API credentials and database settings
   ```

4. Start the infrastructure services:
   ```bash
   # Start Kafka and TimescaleDB using Docker Compose
   docker-compose up -d
   
   # Initialize the database
   python setup_database.py
   ```

### Running the System

1. Start the producer:
   ```bash
   python producer.py
   ```

2. In a new terminal, start the analyzer:
   ```bash
   python analyzer.py
   ```

3. In another terminal, start the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

4. Open your browser to `http://localhost:8501` to view the enhanced dashboard

### Dashboard Features

The enhanced dashboard includes:
- **View Mode Selection**: Choose between Real-time, Historical, or Combined views
- **Time Range Filtering**: Analyze sentiment over different time periods
- **Sentiment Distribution**: Bar charts showing sentiment breakdown
- **Timeline Visualization**: Track sentiment trends over time
- **Historical Data Table**: Browse and search through past mentions

## 📁 Project Structure

```
SentAna-Kafka/
├── producer.py          # Reddit comment producer
├── analyzer.py          # Sentiment analysis processor with database storage
├── dashboard.py         # Enhanced Streamlit web dashboard
├── database.py          # TimescaleDB integration and models
├── setup_database.py    # Database initialization script
├── docker-compose.yml   # Infrastructure services (Kafka + TimescaleDB)
├── .env                 # Environment variables (Reddit + DB credentials)
├── .env.example         # Example environment configuration
├── .gitignore           # Git ignore file
├── requirements.txt     # Python dependencies (updated with DB libraries)
├── README.md           # This file
└── docs/               # Documentation directory
    ├── DATABASE_SETUP.md    # Database setup guide
    ├── ARCHITECTURE.md      # Technical architecture details
    └── ...                 # Other documentation files
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

### Application Settings

Modify the following constants in the respective Python files:

**Producer ([`producer.py`](producer.py:18-22)):**
- `TARGET_KEYWORD`: Keyword to search for (default: "iPhone")
- `TARGET_SUBREDDIT`: Subreddit to monitor (default: "all")
- `KAFKA_TOPIC`: Output topic for raw comments (default: "raw-reddit-mentions")
- `KAFKA_SERVER`: Kafka server address (default: "localhost:9092")

**Analyzer ([`analyzer.py`](analyzer.py:5-8)):**
- `INPUT_KAFKA_TOPIC`: Input topic for raw comments (default: "raw-reddit-mentions")
- `OUTPUT_KAFKA_TOPIC`: Output topic for analyzed sentiment (default: "analyzed-sentiment")
- `KAFKA_SERVER`: Kafka server address (default: "localhost:9092")

**Dashboard ([`dashboard.py`](dashboard.py:11-13)):**
- `KAFKA_TOPIC`: Input topic for analyzed sentiment (default: "analyzed-sentiment")
- `KAFKA_SERVER`: Kafka server address (default: "localhost:9092")

**Database ([`database.py`](database.py)):**
- `DB_HOST`: Database server host (default: "localhost")
- `DB_PORT`: Database server port (default: "5432")
- `DB_NAME`: Database name (default: "sentana")
- `DB_USER`: Database username (default: "postgres")
- `DB_PASSWORD`: Database password (default: "password")

## 📊 Sentiment Analysis

The system uses VADER (Valence Aware Dictionary and sEntiment Reasoner) for sentiment analysis:

- **Positive**: Compound score ≥ 0.05
- **Negative**: Compound score ≤ -0.05
- **Neutral**: Compound score between -0.05 and 0.05

## 🔧 Troubleshooting

### Common Issues

1. **Infrastructure Services**
   - Ensure Docker services are running: `docker-compose ps`
   - Start services if needed: `docker-compose up -d`
   - Check database initialization: `python setup_database.py`

2. **Kafka Connection Errors**
   - Ensure Kafka server is running on `localhost:9092`
   - Check if the required topics exist or can be auto-created

3. **Database Connection Issues**
   - Verify TimescaleDB is running and accessible
   - Check database credentials in `.env`
   - Run setup script if tables don't exist

4. **Reddit API Authentication**
   - Verify your Reddit API credentials in `.env`
   - Ensure your Reddit app has the correct permissions

5. **Dashboard Not Updating**
   - Check if the analyzer is running and processing messages
   - Verify Kafka topic names match across components
   - Ensure database is receiving data from analyzer

### Logs

Each component provides console output for monitoring:
- Producer: Shows authentication status and sent messages
- Analyzer: Displays processed comments, sentiment results, and database storage status
- Dashboard: Shows data reception status and database queries
- Database: Setup script provides detailed initialization feedback

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [PRAW](https://praw.readthedocs.io/) - Python Reddit API Wrapper
- [Apache Kafka](https://kafka.apache.org/) - Distributed streaming platform
- [TimescaleDB](https://www.timescale.com/) - Time-series database built on PostgreSQL
- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment) - Sentiment analysis tool
- [Streamlit](https://streamlit.io/) - Data app framework
- [Plotly](https://plotly.com/) - Interactive visualization library
