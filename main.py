from data_pipeline.scrapers.reddit import fetch_reddit_posts
from data_pipeline.processors.text_cleaner import preprocess_posts
from data_pipeline.storage.saver import save_to_csv
import nltk

#Auto-download required NLTK tokenizers if missing
def ensure_nltk_data():
    required_resources = ['punkt', 'punkt_tab']
    for resource in required_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"[INFO] Downloading missing NLTK resource: {resource}")
            nltk.download(resource, quiet=True)





def run_pipeline():
    subreddit = "stocks"
    posts = fetch_reddit_posts(subreddit, limit=100)
    processed = preprocess_posts(posts)
    save_to_csv(processed, f"reddit_{subreddit}")

if __name__ == "__main__":
    ensure_nltk_data()
    run_pipeline()
