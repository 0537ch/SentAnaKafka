import streamlit as st
from kafka import KafkaConsumer
import json
import pandas as pd
from collections import Counter
from database import init_db, get_mentions_by_time_range, get_sentiment_counts, get_db
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- Configuration ---
KAFKA_TOPIC = "analyzed-sentiment"
KAFKA_SERVER = "localhost:9092"

# --- Initialize Database ---
init_db()

# --- Streamlit Page Setup ---
st.set_page_config(layout="wide")
st.title("📊 Reddit Sentiment Analysis Dashboard")

# --- Sidebar Configuration ---
st.sidebar.header("Dashboard Configuration")

# Time range selection for historical data
time_range = st.sidebar.selectbox(
    "Select Time Range for Historical Data:",
    ["Last 1 Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
)

# Convert time range to hours
time_mapping = {
    "Last 1 Hour": 1,
    "Last 6 Hours": 6,
    "Last 24 Hours": 24,
    "Last 7 Days": 24 * 7,
    "Last 30 Days": 24 * 30
}
selected_hours = time_mapping[time_range]

# View mode selection
view_mode = st.sidebar.radio(
    "View Mode:",
    ["Real-time + Historical", "Historical Only", "Real-time Only"]
)

# --- Initialize Kafka Consumer (only if needed) ---
if view_mode in ["Real-time + Historical", "Real-time Only"]:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='latest' # Only get new messages
    )

# --- Load Historical Data ---
def load_historical_data():
    """Load historical data from database"""
    try:
        db_session = next(get_db())
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=selected_hours)
        
        historical_mentions = get_mentions_by_time_range(db_session, start_time, end_time, limit=1000)
        sentiment_counts = get_sentiment_counts(db_session, selected_hours)
        
        db_session.close()
        return historical_mentions, sentiment_counts
    except Exception as e:
        st.error(f"Error loading historical data: {e}")
        return [], {}

# --- Dashboard Layout ---
if view_mode in ["Real-time + Historical", "Historical Only"]:
    st.header("📈 Historical Analysis")
    
    with st.spinner("Loading historical data..."):
        historical_data, hist_sentiment_counts = load_historical_data()
    
    if historical_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sentiment Distribution")
            if hist_sentiment_counts:
                hist_df = pd.DataFrame(list(hist_sentiment_counts.items()), columns=['Sentiment', 'Count'])
                fig = px.bar(hist_df, x='Sentiment', y='Count', title=f"Sentiment Distribution - {time_range}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No historical data available")
        
        with col2:
            st.subheader("Sentiment Timeline")
            if historical_data:
                hist_df = pd.DataFrame(historical_data)
                hist_df['created_utc'] = pd.to_datetime(hist_df['created_utc'])
                
                # Create hourly sentiment counts
                hist_df['hour'] = hist_df['created_utc'].dt.floor('H')
                timeline_data = hist_df.groupby(['hour', 'sentiment_class']).size().reset_index(name='count')
                
                fig = px.line(timeline_data, x='hour', y='count', color='sentiment_class',
                             title="Sentiment Timeline")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No timeline data available")
        

        st.subheader("Historical Mentions")
        hist_df = pd.DataFrame(historical_data)
        if not hist_df.empty:
            hist_df['created_utc'] = pd.to_datetime(hist_df['created_utc']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(hist_df[['sentiment_class', 'sentiment_score', 'author', 'text', 'created_utc']].head(20))
        else:
            st.write("No historical mentions found")
    else:
        st.info("No historical data available for the selected time range")

# --- Real-time Section ---
if view_mode in ["Real-time + Historical", "Real-time Only"]:
    st.header("🔄 Real-time Analysis")
    
    # Dashboard Placeholders for real-time data
    real_time_pie_placeholder = st.empty()
    real_time_table_placeholder = st.empty()
    

    real_time_data = []
    real_time_sentiment_counts = Counter()
    

    print("📊 Real-time dashboard started! Waiting for data...")
    
    try:
        for message in consumer:
            data = message.value
            real_time_data.append(data)
            
            # Update sentiment counts
            real_time_sentiment_counts[data['sentiment_class']] += 1
            
            # Update Pie Chart
            df_counts = pd.DataFrame.from_dict(real_time_sentiment_counts, orient='index').reset_index()
            df_counts.columns = ['Sentiment', 'Count']
            
            with real_time_pie_placeholder.container():
                st.subheader("Real-time Sentiment Distribution")
                if not df_counts.empty:
                    fig = px.bar(df_counts, x='Sentiment', y='Count', title="Live Sentiment Distribution")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Update Data Table
            with real_time_table_placeholder.container():
                st.subheader("Latest Real-time Mentions")
                # Show latest 10 mentions, with the newest on top
                df_display = pd.DataFrame(real_time_data).iloc[::-1].head(10)
                if not df_display.empty:
                    st.dataframe(df_display[['sentiment_class', 'sentiment_score', 'author', 'text']])
            
            # Limit real-time data to prevent memory issues
            if len(real_time_data) > 100:
                real_time_data = real_time_data[-100:]
    
    except KeyboardInterrupt:
        print("Real-time dashboard stopped by user.")
    except Exception as e:
        st.error(f"Error in real-time dashboard: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
            print("Real-time consumer closed.")

else:
    st.info("Real-time monitoring is disabled. Select 'Real-time + Historical' or 'Real-time Only' to enable live updates.")
