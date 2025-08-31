# Indian Stock Market Twitter Data Collection System

A production-ready Twitter scraper implementing enterprise-grade rate limiting, concurrent data processing, and multi-format output generation for Indian stock market sentiment analysis.

## System Overview

This application collects real-time Twitter data for Indian stock market analysis, processing tweets from key financial hashtags including #nifty50, #sensex, #banknifty, and #intraday. The system implements sequential processing with intelligent rate limiting to ensure API compliance while maintaining high data quality through comprehensive deduplication and validation.

## Technical Architecture

- **Sequential Processing**: Eliminates resource contention and simplifies error handling
- **Intelligent Rate Limiting**: Conservative 5-second delays ensure API compliance
- **Concurrent Data Processing**: Producer-consumer pattern with thread-safe queues
- **Multi-Format Output**: Dual Parquet/JSON export for diverse analytical requirements
- **Enterprise Error Handling**: Comprehensive retry logic and graceful degradation

## Technology Stack

### Core Dependencies
- **Python 3.7+**: Application runtime
- **pandas**: Data processing and transformation
- **requests**: HTTP client for API integration  
- **pyarrow**: Apache Parquet format support

### External Services
- **Twitter API v2**: Primary data source with bearer token authentication

## Installation and Configuration

### Environment Setup

```bash
pip install pandas requests pyarrow
```

### API Authentication Configuration

1. Access the Twitter Developer Portal
2. Create a new application with appropriate permissions
3. Generate a Bearer Token with read access
4. Update the configuration constant:

```python
BEARER_TOKEN = "your_actual_bearer_token_here"
```

### System Configuration

Key operational parameters can be adjusted in the configuration section:

```python
TRACKED_HASHTAGS = {"#nifty50", "#sensex", "#banknifty", "#intraday"}
TARGET_TWEETS = 2000                    # Collection target per execution
BATCH_FETCH_SIZE = 100                  # API request batch size
REQUEST_DELAY = 5                       # Rate limiting delay (seconds)
NUM_CONSUMERS = 2                       # Data processing threads
```

## Execution

### Standard Operation

```bash
python stockmarket.py
```

### Expected Runtime
- **Processing Time**: 3-8 minutes for standard configuration
- **API Requests**: Approximately 20-40 requests per execution
- **Output Generation**: Automatic upon completion

## Data Output Specifications

### Output Formats

The system generates two complementary data formats:

**Apache Parquet** (`results.parquet`)
- Optimized for analytical processing
- Columnar compression for storage efficiency  
- Native pandas integration for data science workflows

**JSON Lines** (`results.json`)
- Human-readable format for data validation
- Universal compatibility across programming languages
- Simplified integration with web applications

### Data Schema

Each tweet record contains the following structured fields:

```json
{
  "tweet_id": "1234567890123456789",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "content": "Tweet content text",
  "likes": 42,
  "retweets": 8,
  "replies": 3,
  "quotes": 1,
  "hashtags": ["nifty50", "trading"],
  "mentions": ["username1", "username2"],
  "source_hashtag": "#nifty50"
}
```

## API Rate Limiting and Compliance

### Twitter API Quotas

**Essential (Free) Tier**:
- Monthly limit: 500,000 tweets
- Rate limit: 300 requests per 15-minute window

**Basic ($100/month) Tier**:
- Monthly limit: 10 million tweets  
- Enhanced rate limits for production use

### Rate Limiting Implementation

The system implements conservative rate limiting to ensure compliance:
- 5-second delays between API requests
- Automatic 2-minute backoff for 429 responses
- Sequential processing eliminates quota competition
- Built-in quota protection mechanisms

## System Monitoring and Troubleshooting

### Common Issues and Resolutions

**Authentication Errors (401)**
- Verify bearer token validity in Twitter Developer Portal
- Confirm application has appropriate read permissions
- Check for token expiration or regeneration requirements

**Quota Exhaustion (Empty Results)**
- Monitor usage in Twitter Developer Portal
- Consider upgrading to Basic tier for production use
- Implement data collection scheduling to optimize quota usage

**Rate Limiting (429 Errors)**
- System automatically handles with exponential backoff
- Consider increasing REQUEST_DELAY for additional safety margin
- Monitor API response headers for quota information

### Performance Tuning

**Memory Optimization**
- Adjust BATCH_FETCH_SIZE for memory-constrained environments
- Modify QUEUE_MAXSIZE to control memory buffering

**Throughput Optimization**  
- Reduce REQUEST_DELAY (minimum recommended: 3 seconds)
- Increase NUM_CONSUMERS for faster data processing
- Consider parallel hashtag processing for Basic tier users

## System Architecture Details

### Processing Flow

```
Twitter API → Rate Limiter → Producer Threads → Queue → Consumer Threads → Output Files
```

### Thread Architecture
- **Main Thread**: Orchestrates execution and coordinates shutdown
- **Producer Threads**: Sequential API data collection per hashtag  
- **Consumer Threads**: Concurrent data processing and deduplication
- **Thread Communication**: Thread-safe queues with timeout handling

### Error Handling Strategy
- Graceful degradation for API failures
- Automatic retry with exponential backoff
- Comprehensive logging for operational monitoring
- Data integrity validation throughout pipeline

## Production Deployment Considerations

### Security
- Environment variable configuration for sensitive credentials
- API key rotation procedures
- Audit logging for compliance requirements

### Scalability
- Horizontal scaling through multiple application instances
- Queue-based architecture supports increased processing loads
- Configurable resource allocation for different deployment environments

### Monitoring
- Structured logging for operational visibility
- Performance metrics collection points
- Error rate monitoring and alerting integration points

## Data Quality and Integrity

### Deduplication Strategy
- Hash-based duplicate detection using tweet IDs
- Real-time processing prevents duplicate storage
- Cross-hashtag deduplication maintains data consistency

### Data Validation
- Schema validation for all collected fields
- Timestamp normalization to UTC format
- Content sanitization and encoding handling

## Legal and Compliance Considerations

### Terms of Service Compliance
- Adherence to Twitter API Terms of Service
- Rate limiting ensures respectful API usage
- Data collection limited to publicly available content

### Data Privacy
- No collection of private or protected tweet content
- Compliance with applicable data privacy regulations
- Transparent data usage and retention policies

## Future Enhancement Roadmap

### Technical Improvements
- Kubernetes deployment with auto-scaling capabilities
- Apache Kafka integration for real-time streaming
- GraphQL API development for flexible data access
- Machine learning pipeline integration for sentiment analysis

### Operational Enhancements
- Prometheus/Grafana monitoring stack integration
- Automated alerting for system anomalies  
- CI/CD pipeline implementation
- Comprehensive test suite development

## Contributing

This system demonstrates enterprise software development practices including API integration, concurrent programming, and production system design. The codebase serves as a reference implementation for scalable data collection architectures.

### Code Quality Standards
- Comprehensive error handling and logging
- Thread-safe concurrent programming patterns
- Configuration-driven operational parameters
- Production-ready reliability and monitoring

---

**Technical Contact**: For questions regarding system architecture, deployment, or integration requirements.