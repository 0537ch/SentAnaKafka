#!/usr/bin/env python3
"""
Database setup script for SentAna-Kafka
This script initializes the TimescaleDB database and creates the necessary tables.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import sys

load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sentana")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (without specifying database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"✅ Database '{DB_NAME}' created successfully!")
        else:
            print(f"✅ Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_tables():
    """Create tables and enable TimescaleDB extension"""
    try:
        # Connect to the specific database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Enable TimescaleDB extension
        print("Enabling TimescaleDB extension...")
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            print("✅ TimescaleDB extension enabled!")
        except Exception as e:
            print(f"⚠️  Warning: Could not enable TimescaleDB extension: {e}")
            print("   The system will work with regular PostgreSQL, but time-series optimizations won't be available.")
        
        # Create the reddit_mentions table
        print("Creating reddit_mentions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reddit_mentions (
                id VARCHAR(20) PRIMARY KEY,
                author VARCHAR(255),
                text TEXT,
                url TEXT,
                created_utc TIMESTAMP,
                sentiment_class VARCHAR(20),
                sentiment_score FLOAT,
                keyword VARCHAR(100),
                subreddit VARCHAR(100),
                processed_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Create indexes for better performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_utc ON reddit_mentions (created_utc);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_class ON reddit_mentions (sentiment_class);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_keyword ON reddit_mentions (keyword);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subreddit ON reddit_mentions (subreddit);")
        
        # Try to create TimescaleDB hypertable
        try:
            print("Creating TimescaleDB hypertable...")
            cursor.execute("SELECT create_hypertable('reddit_mentions', 'created_utc', if_not_exists => TRUE);")
            print("✅ TimescaleDB hypertable created successfully!")
        except Exception as e:
            print(f"⚠️  Warning: Could not create hypertable: {e}")
            print("   The table will work as a regular PostgreSQL table.")
        
        # Set up data retention policy (optional - keeps data for 1 year)
        try:
            print("Setting up data retention policy (1 year)...")
            cursor.execute("SELECT add_retention_policy('reddit_mentions', INTERVAL '1 year');")
            print("✅ Data retention policy set!")
        except Exception as e:
            print(f"⚠️  Warning: Could not set retention policy: {e}")
            print("   You may need to manually manage data cleanup.")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Database setup completed successfully!")
        print(f"   Database: {DB_NAME}")
        print(f"   Host: {DB_HOST}:{DB_PORT}")
        print(f"   User: {DB_USER}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"✅ Database connection successful!")
        print(f"   PostgreSQL version: {version[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    print("🚀 SentAna-Kafka Database Setup")
    print("=" * 40)
    
    # Test basic connection first
    print("\n1. Testing database connection...")
    if not test_connection():
        print("\n❌ Cannot connect to PostgreSQL server.")
        print("Please ensure:")
        print("- PostgreSQL/TimescaleDB is running")
        print("- Connection details in .env are correct")
        print("- Database server accepts connections")
        sys.exit(1)
    
    # Create database
    print("\n2. Setting up database...")
    if not create_database():
        sys.exit(1)
    
    # Setup tables
    print("\n3. Creating tables and extensions...")
    if not setup_tables():
        sys.exit(1)
    
    print("\n✅ Setup complete! You can now run the SentAna-Kafka system.")
    print("\nNext steps:")
    print("1. Start Kafka server")
    print("2. Run: python producer.py")
    print("3. Run: python analyzer.py")
    print("4. Run: streamlit run dashboard.py")

if __name__ == "__main__":
    main()