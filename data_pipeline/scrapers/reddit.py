import praw
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def fetch_reddit_posts(subreddit_name: str, limit: int = 50):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    for post in subreddit.hot(limit=limit):
        posts.append({
            "id": post.id,
            "title": post.title,
            "score": post.score,
            "text": post.selftext,
            "url": post.url,
            "scraped_at": datetime.now().isoformat()
        })

    print(f"Scraped {len(posts)} posts from r/{subreddit_name}")
    return posts
