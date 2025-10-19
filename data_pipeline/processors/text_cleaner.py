import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import vader

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("vader_lexicon", quiet=True)

# Initialize VADER once at import time to avoid repeated setup costs
SENTIMENT_ANALYZER = vader.SentimentIntensityAnalyzer()

STOP_WORDS = set(stopwords.words("english"))

def clean_text(text: str) -> str:
    """Remove URLs, special chars, and extra spaces from Reddit text."""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

def extract_keywords(text: str, top_n: int = 5):
    """Extract top-N most common keywords from text."""
    tokens = word_tokenize(text)
    filtered = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    freq = Counter(filtered)
    return [w for w, _ in freq.most_common(top_n)]

def preprocess_posts(posts: list):
    """Clean and extract keywords for each post."""
    processed = []
    for post in posts:
        clean = clean_text(post["text"] or post["title"])
        keywords = extract_keywords(clean)
        sentiment = SENTIMENT_ANALYZER.polarity_scores(clean)
        processed.append({
            "id": post["id"],
            "title": post["title"],
            "score": post["score"],
            "text": post["text"],
            "clean_text": clean,
            "keywords": ", ".join(keywords),
            "sentiment_compound": sentiment.get("compound", 0.0),
            "sentiment_pos": sentiment.get("pos", 0.0),
            "sentiment_neu": sentiment.get("neu", 0.0),
            "sentiment_neg": sentiment.get("neg", 0.0),
            "scraped_at": post.get("scraped_at", "")
        })
    return processed
