from data_pipeline.scrapers.reddit import fetch_reddit_posts
from data_pipeline.processors.text_cleaner import preprocess_posts
from data_pipeline.storage.saver import save_to_csv

def run_pipeline():
    subreddit = "stocks"
    posts = fetch_reddit_posts(subreddit, limit=100)
    processed = preprocess_posts(posts)
    save_to_csv(processed, f"reddit_{subreddit}")

if __name__ == "__main__":
    run_pipeline()
