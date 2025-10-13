import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

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
        processed.append({
            "id": post["id"],
            "title": post["title"],
            "score": post["score"],
            "text": post["text"],
            "clean_text": clean,
            "keywords": ", ".join(keywords)
        })
    return processed
