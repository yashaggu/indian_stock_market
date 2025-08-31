Threaded Twitter Scraper

A multi-threaded Twitter scraper built with Python, using the Twitter API v2.
The program collects tweets related to the Indian stock market (for example: #nifty50, #sensex, #banknifty, #intraday) in batches, while handling rate limits, deduplication, and saving results in Parquet and JSON formats.


############################################
Features
############################################

Producers and consumers:
Producers fetch tweets in batches (100 at a time). Consumers deduplicate and store results.

Target tweet limit: Stops automatically after collecting 2000 unique tweets.

Threaded pipeline: Queue-based producer-consumer model for scalable processing.

Rate limiting: Global lock and retry with exponential backoff for safe API usage.

Progress tracking: Logs updates on tweets fetched and target progress.

Storage formats: Saves output to both Parquet (results.parquet) and JSON (results.json).


############################################
Requirements
############################################

Python 3.9 or later

Install dependencies:

pip install requests pandas pyarrow


############################################
Setup Instructions
############################################

Get a Twitter API key.

Sign up for a Twitter Developer Account at https://developer.twitter.com/

Create a project and app.

Generate a Bearer Token for Twitter API v2.

Configure the program.

Open the Python file.

Replace the placeholder with your Bearer Token:

BEARER_TOKEN = "YOUR_TWITTER_BEARER_TOKEN"


############################################
Optional adjustments:
############################################

TARGET_TWEETS = number of tweets to collect (default: 2000).

TRACKED_HASHTAGS = hashtags to scrape.

HOURS_LOOKBACK = how many hours back to search (default: 24).

############################################
Run the program:
############################################

python twitter_scraper.py


############################################
Output
############################################

After running, results will be stored in:

tweet_threaded_out/results.parquet

tweet_threaded_out/results.json

############################################
Each record contains:
############################################

Tweet ID

Timestamp

Tweet content

Engagement metrics (likes, retweets, replies, quotes)

Extracted hashtags and mentions

Source hashtag

############################################
Example Run (Logs)
############################################
Starting Twitter scraper
Target: 2000 tweets from 4 hashtags
Processing: One hashtag at a time to respect API limits
--------------------------------------------------
Starting producer 1/4 for #nifty50
[#nifty50] Found 100 tweets
Progress: 200/2000 unique tweets
...
Target reached! 2000 unique tweets collected
Done. Collected 2000 unique tweets.

############################################
Notes
############################################

By default, hashtags are processed sequentially to avoid hitting API rate limits.

Parallel round-robin producers can be enabled for speed, but may cause "429 Too Many Requests" errors.

Twitter API quotas:

Recent Search endpoint allows 300 requests per 15 minutes.

Each request fetches up to 100 tweets.