"""
Threaded Twitter scraper using Twitter API v2 + requests.
- Producers fetch tweets in batches of 100 per hashtag.
- Consumers dedupe, process, and save results to Parquet + JSON.
"""

import os
import queue
import threading
import time
from datetime import datetime, timedelta

import pandas as pd
import requests

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
BEARER_TOKEN = "SOME_TWITTER_BEARER_TOKEN"

TRACKED_HASHTAGS = {"#nifty50", "#sensex", "#banknifty", "#intraday"}
TARGET_TWEETS = 2000
BATCH_FETCH_SIZE = 100
OUTPUT_DIR = "tweet_threaded_out"
HOURS_LOOKBACK = 24
NUM_CONSUMERS = 2
QUEUE_MAXSIZE = 20


REQUEST_DELAY = 5

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}
API_URL = "https://api.twitter.com/2/tweets/search/recent"


def since_time(hours_back: int = HOURS_LOOKBACK) -> str:
    """Return ISO timestamp for query start."""
    since_dt = datetime.utcnow() - timedelta(hours=hours_back)
    return since_dt.isoformat("T") + "Z"


def fetch_tweets(tag: str, next_token=None):
    """Call Twitter API for a hashtag batch with SIMPLE rate limiting."""
    print(f"[{tag}] Making API request (waiting {REQUEST_DELAY}s)...")
    time.sleep(REQUEST_DELAY)

    params = {
        "query": f"{tag} lang:en -is:retweet",
        "max_results": BATCH_FETCH_SIZE,
        "tweet.fields": "created_at,public_metrics,entities",
        "expansions": "author_id",
        "user.fields": "username,name",
        "start_time": since_time()
    }
    if next_token:
        params["next_token"] = next_token

    try:
        resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            tweet_count = len(data.get("data", []))
            print(f"[{tag}] SUCCESS - found {tweet_count} tweets")
            return data
        elif resp.status_code == 429:
            print(f"[{tag}] RATE LIMIT - waiting 2 minutes...")
            time.sleep(120)
            return {"data": []}
        else:
            print(f"[{tag}] ERROR - API {resp.status_code}: {resp.text[:100]}...")
            return {"data": []}
    except Exception as e:
        print(f"[{tag}] ERROR - Request failed: {e}")
        return {"data": []}

# ---------------------------------------------------------------------
# Producer
# ---------------------------------------------------------------------
def producer(tag: str, q: queue.Queue, stop_event: threading.Event) -> None:
    """Producer fetches batches for one hashtag and pushes into queue."""
    print(f"[producer:{tag}] started.")
    next_token = None

    while not stop_event.is_set():
        data = fetch_tweets(tag, next_token)

        if not data or "data" not in data or not data["data"]:
            print(f"[{tag}] No tweets found, moving to next page...")

            next_token = data.get("meta", {}).get("next_token") if data else None
            if not next_token:
                break
            continue

        records = []
        for tweet in data["data"]:
            metrics = tweet["public_metrics"]
            hashtags = [h["tag"].lower() for h in tweet.get("entities", {}).get("hashtags", [])]
            mentions = [m["username"] for m in tweet.get("entities", {}).get("mentions", [])]

            records.append({
                "tweet_id": tweet["id"],
                "timestamp": tweet["created_at"],
                "content": tweet["text"],
                "likes": metrics["like_count"],
                "retweets": metrics["retweet_count"],
                "replies": metrics["reply_count"],
                "quotes": metrics["quote_count"],
                "hashtags": hashtags,
                "mentions": mentions,
                "source_hashtag": tag
            })

        q.put(records)
        print(f"[{tag}] Found {len(records)} tweets")

        next_token = data.get("meta", {}).get("next_token")
        if not next_token:
            print(f"[{tag}] No more pages - finished")
            break
    print(f"[producer:{tag}] finished.")

# ---------------------------------------------------------------------
# Consumer
# ---------------------------------------------------------------------
def consumer(q: queue.Queue, stop_event: threading.Event,
             global_state: dict, lock: threading.Lock) -> None:
    """Consumer dedupes, collects, and writes output once."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    buffer = []

    while not (stop_event.is_set() and q.empty()):
        try:
            records = q.get(timeout=2)
        except queue.Empty:
            continue

        new_records = []
        with lock:
            for rec in records:
                if rec["tweet_id"] not in global_state["seen_ids"]:
                    global_state["seen_ids"].add(rec["tweet_id"])
                    new_records.append(rec)

        buffer.extend(new_records)
        q.task_done()

        with lock:
            current_count = len(global_state["seen_ids"])
            if current_count >= TARGET_TWEETS:
                print(f"TARGET REACHED! {current_count} unique tweets collected")
                stop_event.set()
            elif current_count % 200 == 0 and current_count > 0:
                print(f"Progress: {current_count}/{TARGET_TWEETS} unique tweets")

    if buffer:
        df = pd.DataFrame(buffer)
        parquet_path = os.path.join(OUTPUT_DIR, "results.parquet")
        json_path = os.path.join(OUTPUT_DIR, "results.json")

        df.to_parquet(parquet_path, engine="pyarrow", index=False)
        df.to_json(json_path, orient="records", lines=True)

        with lock:
            global_state["total_written"] += len(df)

        print(f"[consumer] wrote {len(df)} rows → {parquet_path}, {json_path}")

    print("[consumer] finished.")

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    print("Starting Twitter scraper")
    print(f"Target: {TARGET_TWEETS} tweets from {len(TRACKED_HASHTAGS)} hashtags")
    print(f"Request delay: {REQUEST_DELAY}s")

    if BEARER_TOKEN == "YOUR_TWITTER_BEARER_TOKEN":
        print("Error: Update bearer token")
        return

    print("-" * 50)

    q = queue.Queue(maxsize=QUEUE_MAXSIZE)
    stop_event = threading.Event()
    lock = threading.Lock()
    state = {"seen_ids": set(), "total_written": 0}

    consumers = [
        threading.Thread(target=consumer, args=(q, stop_event, state, lock), daemon=True)
        for _ in range(NUM_CONSUMERS)
    ]
    for t in consumers:
        t.start()

    print("Processing hashtags...")
    producers = []

    for i, tag in enumerate(TRACKED_HASHTAGS):
        if stop_event.is_set():
            break

        print(f"\nStarting hashtag {i+1}/{len(TRACKED_HASHTAGS)}: {tag}")
        producer_thread = threading.Thread(target=producer, args=(tag, q, stop_event), daemon=True)
        producers.append(producer_thread)
        producer_thread.start()

        producer_thread.join()

        with lock:
            current_count = len(state["seen_ids"])
            print(f"Completed {tag} - {current_count} tweets")

            if current_count >= TARGET_TWEETS:
                print("Target reached")
                break

    for t in producers:
        t.join()

    q.join()
    stop_event.set()

    for t in consumers:
        t.join()

    print(f"Done. Collected {len(state['seen_ids'])} unique tweets.")


if __name__ == "__main__":
    main()
