# File used for analyzing processed data and generating insights related to market sentiment

import pandas as pd
import numpy as np
import glob
import os
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def load_latest_csv(folder: str = "share/outputs") -> pd.DataFrame:
    """Load the most recent CSV file from the outputs folder."""
    csv_files = glob.glob(os.path.join(folder, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder}")
    
    # Sort by modification time and get the latest
    latest_file = max(csv_files, key=os.path.getmtime)
    return pd.read_csv(latest_file)

def load_csv_by_name(filename: str, folder: str = "share/outputs") -> pd.DataFrame:
    """Load a specific CSV file by name."""
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath)

def calculate_sentiment_summary(df: pd.DataFrame) -> Dict:
    """Calculate comprehensive sentiment statistics."""
    if 'sentiment_compound' not in df.columns:
        raise ValueError("DataFrame must contain 'sentiment_compound' column")
    
    # Basic statistics
    compound_scores = df['sentiment_compound'].dropna()
    
    # Categorize sentiment
    positive = (compound_scores > 0.05).sum()
    neutral = ((compound_scores >= -0.05) & (compound_scores <= 0.05)).sum()
    negative = (compound_scores < -0.05).sum()
    
    # Score statistics
    stats = {
        'total_posts': len(df),
        'avg_compound': compound_scores.mean(),
        'std_compound': compound_scores.std(),
        'median_compound': compound_scores.median(),
        'min_compound': compound_scores.min(),
        'max_compound': compound_scores.max(),
        'positive_count': positive,
        'neutral_count': neutral,
        'negative_count': negative,
        'positive_pct': (positive / len(compound_scores)) * 100,
        'neutral_pct': (neutral / len(compound_scores)) * 100,
        'negative_pct': (negative / len(compound_scores)) * 100,
    }
    
    # Reddit score correlation if available
    if 'score' in df.columns:
        score_sentiment_corr = df['score'].corr(df['sentiment_compound'])
        stats['score_sentiment_correlation'] = score_sentiment_corr
    
    return stats

def extract_keyword_sentiment(df: pd.DataFrame, top_n: int = 20) -> Dict:
    """Extract keywords and their associated sentiment scores."""
    if 'keywords' not in df.columns or 'sentiment_compound' not in df.columns:
        raise ValueError("DataFrame must contain 'keywords' and 'sentiment_compound' columns")
    
    # Flatten keywords and associate with sentiment
    keyword_sentiments = []
    
    for idx, row in df.iterrows():
        if pd.notna(row['keywords']) and pd.notna(row['sentiment_compound']):
            keywords = [k.strip() for k in str(row['keywords']).split(',') if k.strip()]
            for keyword in keywords:
                keyword_sentiments.append({
                    'keyword': keyword,
                    'sentiment': row['sentiment_compound'],
                    'score': row.get('score', 0)
                })
    
    if not keyword_sentiments:
        return {'top_positive': [], 'top_negative': [], 'keyword_stats': {}}
    
    keyword_df = pd.DataFrame(keyword_sentiments)
    
    # Group by keyword and calculate stats
    keyword_stats = keyword_df.groupby('keyword').agg({
        'sentiment': ['mean', 'count', 'std'],
        'score': 'mean'
    }).round(3)
    
    keyword_stats.columns = ['avg_sentiment', 'frequency', 'sentiment_std', 'avg_score']
    keyword_stats = keyword_stats.sort_values('avg_sentiment', ascending=False)
    
    # Top positive and negative keywords
    top_positive = keyword_stats.head(top_n).to_dict('index')
    top_negative = keyword_stats.tail(top_n).to_dict('index')
    
    return {
        'top_positive': top_positive,
        'top_negative': top_negative,
        'keyword_stats': keyword_stats.to_dict('index')
    }

def get_top_posts(df: pd.DataFrame, by: str = 'compound', n: int = 10) -> pd.DataFrame:
    """Get top N posts by sentiment score."""
    if by == 'compound':
        col = 'sentiment_compound'
    elif by == 'positive':
        col = 'sentiment_pos'
    elif by == 'negative':
        col = 'sentiment_neg'
    else:
        raise ValueError("'by' must be 'compound', 'positive', or 'negative'")
    
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")
    
    # Get top posts
    top_posts = df.nlargest(n, col)[['title', 'clean_text', col, 'score']].copy()
    top_posts = top_posts.round(3)
    
    return top_posts

def get_bottom_posts(df: pd.DataFrame, by: str = 'compound', n: int = 10) -> pd.DataFrame:
    """Get bottom N posts by sentiment score."""
    if by == 'compound':
        col = 'sentiment_compound'
    elif by == 'positive':
        col = 'sentiment_pos'
    elif by == 'negative':
        col = 'sentiment_neg'
    else:
        raise ValueError("'by' must be 'compound', 'positive', or 'negative'")
    
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")
    
    # Get bottom posts
    bottom_posts = df.nsmallest(n, col)[['title', 'clean_text', col, 'score']].copy()
    bottom_posts = bottom_posts.round(3)
    
    return bottom_posts

def generate_summary_report(csv_path: str) -> Dict:
    """Generate a comprehensive sentiment analysis report."""
    df = pd.read_csv(csv_path)
    
    # Basic sentiment stats
    sentiment_stats = calculate_sentiment_summary(df)
    
    # Keyword analysis
    keyword_analysis = extract_keyword_sentiment(df)
    
    # Top posts
    top_positive_posts = get_top_posts(df, 'compound', 5)
    top_negative_posts = get_bottom_posts(df, 'compound', 5)
    
    # Time analysis if timestamp available
    time_analysis = {}
    if 'scraped_at' in df.columns:
        df['scraped_at'] = pd.to_datetime(df['scraped_at'])
        time_analysis = {
            'date_range': {
                'start': df['scraped_at'].min().strftime('%Y-%m-%d %H:%M'),
                'end': df['scraped_at'].max().strftime('%Y-%m-%d %H:%M')
            },
            'posts_per_hour': len(df) / ((df['scraped_at'].max() - df['scraped_at'].min()).total_seconds() / 3600)
        }
    
    return {
        'file_info': {
            'path': csv_path,
            'total_posts': len(df),
            'columns': list(df.columns)
        },
        'sentiment_stats': sentiment_stats,
        'keyword_analysis': keyword_analysis,
        'top_positive_posts': top_positive_posts.to_dict('records'),
        'top_negative_posts': top_negative_posts.to_dict('records'),
        'time_analysis': time_analysis,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def filter_posts(df: pd.DataFrame, 
                 sentiment_min: float = -1.0, 
                 sentiment_max: float = 1.0,
                 keyword_filter: str = "",
                 score_min: int = 0) -> pd.DataFrame:
    """Filter posts based on various criteria."""
    filtered_df = df.copy()
    
    # Sentiment range filter
    if 'sentiment_compound' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['sentiment_compound'] >= sentiment_min) & 
            (filtered_df['sentiment_compound'] <= sentiment_max)
        ]
    
    # Keyword filter
    if keyword_filter and 'clean_text' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['clean_text'].str.contains(keyword_filter, case=False, na=False)
        ]
    
    # Score filter
    if 'score' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['score'] >= score_min]
    
    return filtered_df