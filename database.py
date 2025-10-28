import os
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sentana")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create base class for models
Base = declarative_base()

# Define Reddit mention model
class RedditMention(Base):
    __tablename__ = 'reddit_mentions'
    
    id = Column(String(20), primary_key=True)
    author = Column(String(255))
    text = Column(Text)
    url = Column(Text)
    created_utc = Column(DateTime)
    sentiment_class = Column(String(20))
    sentiment_score = Column(Float)
    keyword = Column(String(100))
    subreddit = Column(String(100))
    processed_at = Column(DateTime, default=datetime.utcnow)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)
    
    try:
        with engine.connect() as conn:
            conn.execute("SELECT create_hypertable('reddit_mentions', 'created_utc')")
            conn.commit()
        print("✅ TimescaleDB hypertable created successfully")
    except Exception as e:
        print(f"⚠️  Note: TimescaleDB hypertable creation failed (might already exist or not using TimescaleDB): {e}")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def store_mention(db_session, mention_data):
    """Store a Reddit mention in the database"""
    try:
        mention = RedditMention(
            id=mention_data['id'],
            author=mention_data['author'],
            text=mention_data['text'],
            url=mention_data['url'],
            created_utc=datetime.fromtimestamp(mention_data['created_utc']),
            sentiment_class=mention_data['sentiment_class'],
            sentiment_score=mention_data['sentiment_score'],
            keyword=mention_data.get('keyword', 'iPhone'),  # Default keyword
            subreddit=mention_data.get('subreddit', 'unknown')
        )
        db_session.add(mention)
        db_session.commit()
        return True
    except Exception as e:
        print(f"❌ Error storing mention in database: {e}")
        db_session.rollback()
        return False

def get_mentions_by_time_range(db_session, start_time, end_time, limit=100):
    """Get mentions within a time range"""
    try:
        mentions = db_session.query(RedditMention).filter(
            RedditMention.created_utc >= start_time,
            RedditMention.created_utc <= end_time
        ).order_by(RedditMention.created_utc.desc()).limit(limit).all()
        
        return [{
            'id': m.id,
            'author': m.author,
            'text': m.text,
            'url': m.url,
            'sentiment_class': m.sentiment_class,
            'sentiment_score': m.sentiment_score,
            'created_utc': m.created_utc
        } for m in mentions]
    except Exception as e:
        print(f"❌ Error fetching mentions: {e}")
        return []

def get_sentiment_counts(db_session, hours=24):
    """Get sentiment counts for the last N hours"""
    try:
        from datetime import timedelta
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        from sqlalchemy import func
        counts = db_session.query(
            RedditMention.sentiment_class,
            func.count(RedditMention.id).label('count')
        ).filter(
            RedditMention.created_utc >= start_time
        ).group_by(RedditMention.sentiment_class).all()
        
        return {sentiment: count for sentiment, count in counts}
    except Exception as e:
        print(f"❌ Error fetching sentiment counts: {e}")
        return {}