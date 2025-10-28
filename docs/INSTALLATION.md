# Installation & Setup Guide

This guide provides step-by-step instructions for setting up the SentAna-Kafka real-time sentiment analysis system.

## 📋 Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.7 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: Minimum 2GB free disk space
- **Network**: Internet connection for Reddit API access

### Software Dependencies

- **Apache Kafka**: Version 4.1.0 with KRaft mode
- **Java**: JDK 17 or higher (required for Kafka 4.1.0)
- **Git**: For cloning the repository
- **Python Package Manager**: pip (included with Python)

## 🚀 Installation Steps

### Step 1: Install Java (Required for Kafka)

#### Windows
1. Download OpenJDK 17 from [https://adoptium.net/](https://adoptium.net/)
2. Run the installer and follow the setup wizard
3. Verify installation:
   ```cmd
   java -version
   ```

#### macOS
```bash
# Using Homebrew
brew install openjdk@17

# Set JAVA_HOME
echo 'export JAVA_HOME=/usr/local/opt/openjdk@17' >> ~/.zshrc
source ~/.zshrc
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install openjdk-17-jdk -y
```

### Step 2: Install Apache Kafka 4.1.0 with KRaft Mode

#### Windows
1. Download Kafka 4.1.0 from [https://kafka.apache.org/downloads](https://kafka.apache.org/downloads)
2. Extract the ZIP file to `C:\kafka`
3. Add Kafka to PATH:
   ```cmd
   setx PATH "%PATH%;C:\kafka\bin\windows"
   ```

#### macOS
```bash
# Download Kafka 4.1.0
curl https://downloads.apache.org/kafka/4.1.0/kafka_2.13-4.1.0.tgz -o kafka.tgz
tar -xzf kafka.tgz
sudo mv kafka_2.13-4.1.0 /usr/local/kafka
```

#### Linux (Ubuntu/Debian)
```bash
# Download and extract Kafka 4.1.0
wget https://downloads.apache.org/kafka/4.1.0/kafka_2.13-4.1.0.tgz
tar -xzf kafka_2.13-4.1.0.tgz
sudo mv kafka_2.13-4.1.0 /usr/local/kafka

# Create Kafka user and set permissions
sudo useradd kafka -m
sudo chown -R kafka:kafka /usr/local/kafka
```

### Step 3: Configure and Start Kafka with KRaft Mode

#### Generate Cluster ID
```bash
# Navigate to Kafka directory
cd /usr/local/kafka  # Adjust path based on your installation

# Generate a unique cluster ID (one-time setup)
bin/kafka-storage.sh random-uuid
```

#### Format Storage Directories
```bash
# Replace <CLUSTER_ID> with the ID generated above
bin/kafka-storage.sh format -t <CLUSTER_ID> -c config/kraft/server.properties
```

#### Start Kafka Broker (KRaft Mode)
```bash
# Start Kafka broker without Zookeeper
bin/kafka-server-start.sh config/kraft/server.properties
```

**Note**: Kafka 4.1.0 with KRaft mode doesn't require Zookeeper. Keep this service running throughout the setup process.

### Step 4: Clone the Repository

```bash
# Clone the project
git clone <repository-url>
cd SentAna-Kafka

# Verify project structure
ls -la
```

### Step 5: Set Up Python Virtual Environment

#### Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### Verify Activation
You should see `(venv)` prefix in your terminal prompt.

### Step 6: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 7: Configure Reddit API Credentials

#### Create Reddit Application
1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - **Name**: SentAna-Kafka (or your preferred name)
   - **Select App Type**: Script
   - **About URL**: (optional)
   - **Redirect URI**: (optional)
4. Click "Create App"
5. Note down your credentials:
   - Client ID
   - Client Secret

#### Configure Environment Variables
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your credentials:
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=script:KafkaSentimentProject:v1.0 (by /u/your_reddit_username)
   REDDIT_USERNAME=your_reddit_username
   REDDIT_PASSWORD=your_reddit_password
   ```

3. **Security Note**: The `.env` file is already included in `.gitignore` to protect your credentials.

### Step 8: Create Kafka Topics

```bash
# Navigate to Kafka directory
cd /usr/local/kafka

# Create topic for raw Reddit mentions
bin/kafka-topics.sh --create --topic raw-reddit-mentions --bootstrap-server localhost:9092 --partitions 1

# Create topic for analyzed sentiment
bin/kafka-topics.sh --create --topic analyzed-sentiment --bootstrap-server localhost:9092 --partitions 1

# Verify topics were created
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Note**: In KRaft mode, the `--replication-factor` parameter is not required as it's managed by the KRaft controller.

### Step 9: Verify Installation

#### Test Kafka Connection
```bash
# Start a test consumer
bin/kafka-console-consumer.sh --topic raw-reddit-mentions --from-beginning --bootstrap-server localhost:9092
```

#### Test Python Components
```bash
# Test producer (should connect to Reddit and Kafka)
python -c "
import praw
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

load_dotenv()
print('Testing Reddit connection...')
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    username=os.getenv('REDDIT_USERNAME'),
    password=os.getenv('REDDIT_PASSWORD')
)
print(f'Reddit auth successful: {reddit.user.me()}')

print('Testing Kafka connection...')
producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('test-topic', {'test': 'message'})
producer.flush()
print('Kafka connection successful!')
"
```

## 🔧 Configuration Options

### Kafka Configuration

#### Server Properties (config/server.properties)
```properties
# Basic configuration
broker.id=0
listeners=PLAINTEXT://localhost:9092
log.dirs=/tmp/kafka-logs
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Performance tuning
num.partitions=1
num.recovery.threads.per.data.dir=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
log.retention.hours=168
log.retention.check.interval.ms=300000
```

#### Topic Configuration
```bash
# Create topics with custom retention
bin/kafka-topics.sh --create \
  --topic raw-reddit-mentions \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --config retention.ms=604800000  # 7 days

bin/kafka-topics.sh --create \
  --topic analyzed-sentiment \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --config retention.ms=604800000  # 7 days
```

### Python Application Configuration

#### Producer Customization ([`producer.py`](../producer.py))
```python
# Modify these constants as needed
TARGET_KEYWORD = "iPhone"              # Change to monitor different keywords
TARGET_SUBREDDIT = "all"               # Specific subreddit or "all"
KAFKA_TOPIC = "raw-reddit-mentions"     # Output topic name
KAFKA_SERVER = "localhost:9092"         # Kafka broker address

# Performance settings
REDDIT_TIMEOUT = 30                    # Reddit API timeout in seconds
```

#### Analyzer Customization ([`analyzer.py`](../analyzer.py))
```python
# Modify these constants as needed
INPUT_KAFKA_TOPIC = "raw-reddit-mentions"   # Input topic
OUTPUT_KAFKA_TOPIC = "analyzed-sentiment"   # Output topic
KAFKA_SERVER = "localhost:9092"              # Kafka broker address

# Sentiment analysis thresholds
POSITIVE_THRESHOLD = 0.05              # Minimum score for positive
NEGATIVE_THRESHOLD = -0.05             # Maximum score for negative
```

#### Dashboard Customization ([`dashboard.py`](../dashboard.py))
```python
# Modify these constants as needed
KAFKA_TOPIC = "analyzed-sentiment"    # Input topic
KAFKA_SERVER = "localhost:9092"        # Kafka broker address

# Display settings
MAX_DISPLAY_ROWS = 10                  # Maximum rows in data table
REFRESH_INTERVAL = 1000                # Auto-refresh interval in ms
```

## 🐛 Troubleshooting

### Common Installation Issues

#### Java/Kafka Issues
**Problem**: `java: command not found`
**Solution**: 
1. Verify Java installation: `java -version`
2. Check JAVA_HOME environment variable
3. Add Java to system PATH

**Problem**: Kafka fails to start
**Solution**:
1. Check if Zookeeper is running
2. Verify Kafka configuration files
3. Check port 9092 availability: `netstat -an | grep 9092`

#### Python Issues
**Problem**: Module import errors
**Solution**:
1. Activate virtual environment
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version compatibility

**Problem**: Reddit API authentication fails
**Solution**:
1. Verify Reddit app credentials
2. Check Reddit username/password
3. Ensure user agent string is properly formatted

#### Kafka Topic Issues
**Problem**: Topic creation fails
**Solution**:
1. Verify Kafka broker is running
2. Check broker connectivity: `telnet localhost 9092`
3. Create topics manually with correct parameters

### Performance Issues

#### High Memory Usage
**Solution**:
1. Adjust Kafka heap size in `kafka-server-start.sh`
2. Reduce number of partitions
3. Implement message batching

#### Slow Processing
**Solution**:
1. Increase Kafka producer batch size
2. Adjust consumer poll interval
3. Optimize sentiment analysis processing

### Network Issues

#### Connection Refused
**Solution**:
1. Check firewall settings
2. Verify Kafka broker address
3. Test network connectivity

#### Timeouts
**Solution**:
1. Increase timeout values in configuration
2. Check network latency
3. Verify system resources

## 🔄 Maintenance

### Regular Tasks

#### Kafka Maintenance
```bash
# Monitor topic sizes
bin/kafka-log-dirs.sh --describe --bootstrap-server localhost:9092

# Clean up old logs (if needed)
# Configure log.retention.hours in server.properties

# Monitor consumer groups
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

#### Application Monitoring
```bash
# Check process status
ps aux | grep python

# Monitor resource usage
htop  # or top

# Check logs for errors
tail -f /var/log/kafka/server.log
```

### Updates

#### Kafka Updates
1. Backup existing configuration
2. Download new Kafka version
3. Update configuration files
4. Restart services

#### Python Dependencies
```bash
# Update requirements
pip list --outdated

# Update specific packages
pip install --upgrade package-name

# Update all packages
pip-review --local --interactive
```

This installation guide should help you set up the SentAna-Kafka system successfully. If you encounter any issues not covered here, please refer to the [API Reference](API_REFERENCE.md) or [Architecture Overview](ARCHITECTURE.md) for additional technical details.