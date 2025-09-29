# main.py
import argparse
import os
from datetime import date
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

from data_pipeline.scrapers.reddit import get_reddit_posts

def run_pipeline(subreddit: str, limit: int, out_template: str) -> str:
    """
    Scrape -> sentiment -> CSV.
    Returns the output path.
    """
    load_dotenv()  # loads Reddit API credentials if needed

    # 1) Scrape
    posts = get_reddit_posts(subreddit, limit=limit)

    # 2) Sentiment
    analyzer = SentimentIntensityAnalyzer()
    rows = []
    for p in posts:
        text = p.get("title", "")
        sent = analyzer.polarity_scores(text)
        rows.append({
            "subreddit": subreddit,
            "title": text, # post title
            "score": p.get("score", None), # upvotes - downvotes
            "sent_neg": sent["neg"], # negative sentiment score
            "sent_neu": sent["neu"], # neutral sentiment score
            "sent_pos": sent["pos"], # positive sentiment score
            "sent_compound": sent["compound"], # compound sentiment score
        })

    df = pd.DataFrame(rows)

    # 3) Save to CSV
    out_path = out_template.format(date=date.today().isoformat())
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)

    # Show preview
    print(f"Wrote {len(df)} rows → {out_path}")
    if not df.empty:
        print(df.head(5).to_string(index=False))

    return out_path

def parse_args():
    parser = argparse.ArgumentParser(description="Reddit sentiment pipeline")
    parser.add_argument("--subreddit", default="stocks", help="Subreddit to scrape")
    parser.add_argument("--limit", type=int, default=50, help="Number of posts")
    parser.add_argument(
        "--out",
        default="share/outputs/reddit_{date}.csv",
        help="Output CSV path (supports {date})"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.subreddit, args.limit, args.out)
