# Database Setup Guide

This guide explains how to set up the database layer for SentAna-Kafka using TimescaleDB.

## Overview

The enhanced SentAna-Kafka system includes a persistent database layer that:
- Stores all analyzed sentiment data
- Enables historical analysis and trend tracking
- Provides data persistence across system restarts
- Supports advanced analytics and reporting

## Prerequisites

- Docker and Docker Compose (recommended)
- OR PostgreSQL/TimescaleDB installed locally
- Python 3.7+ with updated requirements.txt dependencies

## Option 1: Docker Setup (Recommended)

### 1. Start the Services

```bash
# Start Kafka and TimescaleDB
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 2. Initialize the Database

```bash
# Run the database setup script
python setup_database.py
```

This script will:
- Create the database if it doesn't exist
- Enable TimescaleDB extensions
- Create the reddit_mentions table
- Set up indexes for performance
- Configure data retention policies

## Option 2: Manual Setup

### 1. Install TimescaleDB

Follow the official TimescaleDB installation guide for your operating system:
https://docs.timescale.com/install/latest/

### 2. Create Database

```sql
-- Connect to PostgreSQL and create database
CREATE DATABASE sentana;
```

### 3. Run Setup Script

```bash
python setup_database.py
```

## Database Schema

The system uses a single table `reddit_mentions` with the following structure:

```sql
CREATE TABLE reddit_mentions (
    id VARCHAR(20) PRIMARY KEY,           -- Reddit comment ID
    author VARCHAR(255),                   -- Reddit username
    text TEXT,                             -- Comment content
    url TEXT,                              -- Reddit comment URL
    created_utc TIMESTAMP,                 -- Original comment timestamp
    sentiment_class VARCHAR(20),           -- Positive/Negative/Neutral
    sentiment_score FLOAT,                 -- VADER compound score
    keyword VARCHAR(100),                  -- Target keyword (e.g., "iPhone")
    subreddit VARCHAR(100),                -- Source subreddit
    processed_at TIMESTAMP DEFAULT NOW()   -- Processing timestamp
);
```

## Configuration

Update your `.env` file with database configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sentana
DB_USER=postgres
DB_PASSWORD=password
```

## Data Flow

```
Reddit → Producer → Kafka → Analyzer → Database → Dashboard
                                    ↓
                              Kafka (for real-time)
```

1. **Analyzer** stores processed sentiment data in the database
2. **Dashboard** queries database for historical analysis
3. **Kafka** continues to provide real-time streaming

## Features Enabled by Database

### Historical Analysis
- Sentiment trends over time
- Keyword popularity tracking
- Subreddit sentiment comparison
- Time-based filtering

### Advanced Queries
- Moving averages
- Sentiment velocity
- Anomaly detection
- Custom date ranges

### Data Export
- CSV export for external analysis
- API endpoints for integration
- Backup and restore capabilities

## Performance Considerations

### Indexes
The system automatically creates indexes on:
- `created_utc` (time-based queries)
- `sentiment_class` (filtering by sentiment)
- `keyword` (keyword-based analysis)
- `subreddit` (subreddit analysis)

### Data Retention
TimescaleDB automatically manages data retention:
- Default: 1 year retention
- Configurable based on storage needs
- Automatic cleanup of old data

### Scaling
- TimescaleDB supports horizontal scaling
- Partitioning by time for efficient queries
- Compression for historical data

## Troubleshooting

### Connection Issues
```bash
# Test database connection
python -c "from database import init_db; init_db(); print('Database connection successful')"
```

### Common Errors

1. **Connection refused**: Ensure TimescaleDB is running
2. **Authentication failed**: Check .env credentials
3. **Database doesn't exist**: Run setup script
4. **Permission denied**: Ensure user has necessary privileges

### Manual Database Reset

```bash
# Drop and recreate database
docker exec -it sentana-timescaledb psql -U postgres -c "DROP DATABASE IF EXISTS sentana;"
docker exec -it sentana-timescaledb psql -U postgres -c "CREATE DATABASE sentana;"

# Re-run setup
python setup_database.py
```

## Migration from Original System

If upgrading from the original system without database:

1. **Backup current configuration**
2. **Install new dependencies**: `pip install -r requirements.txt`
3. **Set up database**: Follow this guide
4. **Update .env**: Add database configuration
5. **Restart services**: All components work with new database layer

The system maintains backward compatibility - Kafka streaming continues to work as before, with database as an additional persistence layer.