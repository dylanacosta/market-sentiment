import praw

def get_reddit_posts(subreddit_name="stocks", limit=10):
    """
    Fetch recent posts from a given subreddit.
    
    Args:
        subreddit_name (str): The subreddit to scrape (default: 'stocks')
        limit (int): Number of posts to fetch
    
    Returns:
        list of dict: Each dict contains post title and score
    """
    reddit = praw.Reddit(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        user_agent="market-sentiment-bot"
    )
    
    posts = []
    for post in reddit.subreddit(subreddit_name).hot(limit=limit):
        posts.append({
            "title": post.title,
            "score": post.score
        })
    
    return posts


if __name__ == "__main__":
    data = get_reddit_posts("stocks", 5)
    for d in data:
        print(d)
