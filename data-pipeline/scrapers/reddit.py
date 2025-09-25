import os
import praw
from dotenv import load_dotenv
load_dotenv()


def get_reddit_posts(subreddit_name="stocks", limit=10):
    """
    Fetch recent posts from a given subreddit.
    
    Args:
        subreddit_name (str): The subreddit to scrape (default: 'stocks')
        limit (int): Number of posts to fetch; Capped at 1000 by Reddit API
        
    
    Returns:
        list of dict: Each dict contains post title and score
        Score: Number of upvotes minus downvotes
    """
    reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            redirect_uri=os.getenv("REDDIT_REDIRECT_URI"),
        )
    

    posts = []
    for post in reddit.subreddit(subreddit_name).hot(limit=limit):
        posts.append({
            "title": post.title,
            "score": post.score
        })
    
    return posts, 


if __name__ == "__main__":
    data = get_reddit_posts("stocks", 5)
    for d in data:
        print(d)
