import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob
import os
from datetime import datetime
import sys

# Add the project root to Python path
sys.path.append('/Users/dylanacosta/Desktop/Projects/market-sentiment')

# Import analysis functions using importlib
import importlib.util
spec = importlib.util.spec_from_file_location("analyze", "main-pipeline/analyze.py")
analyze_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_module)

# Import functions
load_latest_csv = analyze_module.load_latest_csv
load_csv_by_name = analyze_module.load_csv_by_name
calculate_sentiment_summary = analyze_module.calculate_sentiment_summary
extract_keyword_sentiment = analyze_module.extract_keyword_sentiment
get_top_posts = analyze_module.get_top_posts
get_bottom_posts = analyze_module.get_bottom_posts
filter_posts = analyze_module.filter_posts
generate_summary_report = analyze_module.generate_summary_report

# Page configuration
st.set_page_config(
    page_title="Market Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.positive { color: #28a745; }
.negative { color: #dc3545; }
.neutral { color: #6c757d; }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📊 Market Sentiment Dashboard")
    st.markdown("Analyze Reddit sentiment data with interactive visualizations and filtering")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Data Selection")
        
        # File selector
        csv_files = glob.glob("share/outputs/*.csv")
        if not csv_files:
            st.error("No CSV files found in share/outputs/")
            st.stop()
        
        # Sort files by modification time (newest first)
        csv_files.sort(key=os.path.getmtime, reverse=True)
        file_options = [os.path.basename(f) for f in csv_files]
        
        selected_file = st.selectbox(
            "Select CSV file:",
            file_options,
            help="Choose which dataset to analyze"
        )
        
        # Load data
        try:
            df = load_csv_by_name(selected_file)
            st.success(f"✅ Loaded {len(df)} posts")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()
        
        st.header("🔍 Filters")
        
        # Sentiment range filter
        st.subheader("Sentiment Range")
        sentiment_range = st.slider(
            "Compound Sentiment Score",
            min_value=-1.0,
            max_value=1.0,
            value=(-1.0, 1.0),
            step=0.01,
            help="Filter posts by sentiment compound score"
        )
        
        # Keyword filter
        st.subheader("Keyword Search")
        keyword_filter = st.text_input(
            "Search in text:",
            placeholder="Enter keywords to filter posts...",
            help="Filter posts containing specific keywords"
        )
        
        # Score filter
        st.subheader("Reddit Score")
        if 'score' in df.columns:
            score_range = st.slider(
                "Minimum Reddit Score",
                min_value=int(df['score'].min()),
                max_value=int(df['score'].max()),
                value=int(df['score'].min()),
                help="Filter posts by minimum Reddit upvotes"
            )
        else:
            score_range = 0
        
        # Apply filters
        filtered_df = filter_posts(
            df,
            sentiment_min=sentiment_range[0],
            sentiment_max=sentiment_range[1],
            keyword_filter=keyword_filter,
            score_min=score_range
        )
        
        st.info(f"📊 Showing {len(filtered_df)} of {len(df)} posts")
    
    # Main content
    if len(filtered_df) == 0:
        st.warning("No posts match the current filters. Try adjusting your criteria.")
        return
    
    # Calculate summary statistics
    try:
        sentiment_stats = calculate_sentiment_summary(filtered_df)
        keyword_analysis = extract_keyword_sentiment(filtered_df, top_n=15)
    except Exception as e:
        st.error(f"Error calculating statistics: {e}")
        return
    
    # Metrics row
    st.header("📈 Summary Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Posts",
            f"{sentiment_stats['total_posts']:,}",
            help="Number of posts in filtered dataset"
        )
    
    with col2:
        avg_sentiment = sentiment_stats['avg_compound']
        sentiment_color = "positive" if avg_sentiment > 0.05 else "negative" if avg_sentiment < -0.05 else "neutral"
        st.metric(
            "Avg Sentiment",
            f"{avg_sentiment:.3f}",
            delta=f"{sentiment_stats['std_compound']:.3f} std",
            help="Average compound sentiment score (-1 to +1)"
        )
    
    with col3:
        st.metric(
            "Positive Posts",
            f"{sentiment_stats['positive_count']} ({sentiment_stats['positive_pct']:.1f}%)",
            help="Posts with positive sentiment (>0.05)"
        )
    
    with col4:
        st.metric(
            "Neutral Posts",
            f"{sentiment_stats['neutral_count']} ({sentiment_stats['neutral_pct']:.1f}%)",
            help="Posts with neutral sentiment (-0.05 to 0.05)"
        )
    
    with col5:
        st.metric(
            "Negative Posts",
            f"{sentiment_stats['negative_count']} ({sentiment_stats['negative_pct']:.1f}%)",
            help="Posts with negative sentiment (<-0.05)"
        )
    
    # Visualizations
    st.header("📊 Visualizations")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Sentiment Distribution", "Score vs Sentiment", "Keywords", "Top Posts"])
    
    with tab1:
        st.subheader("Sentiment Distribution")
        
        # Histogram of sentiment scores
        fig_hist = px.histogram(
            filtered_df,
            x='sentiment_compound',
            nbins=30,
            title="Distribution of Sentiment Scores",
            labels={'sentiment_compound': 'Compound Sentiment Score', 'count': 'Number of Posts'}
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Neutral")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Sentiment categories pie chart
        sentiment_categories = pd.DataFrame({
            'Category': ['Positive', 'Neutral', 'Negative'],
            'Count': [sentiment_stats['positive_count'], sentiment_stats['neutral_count'], sentiment_stats['negative_count']]
        })
        
        fig_pie = px.pie(
            sentiment_categories,
            values='Count',
            names='Category',
            title="Sentiment Categories Distribution",
            color_discrete_map={'Positive': '#28a745', 'Neutral': '#6c757d', 'Negative': '#dc3545'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.subheader("Reddit Score vs Sentiment")
        
        if 'score' in filtered_df.columns:
            fig_scatter = px.scatter(
                filtered_df,
                x='sentiment_compound',
                y='score',
                title="Reddit Score vs Sentiment Score",
                labels={'sentiment_compound': 'Compound Sentiment Score', 'score': 'Reddit Score (Upvotes)'},
                hover_data=['title'] if 'title' in filtered_df.columns else None
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Correlation info
            correlation = filtered_df['score'].corr(filtered_df['sentiment_compound'])
            st.info(f"📊 Correlation between Reddit score and sentiment: {correlation:.3f}")
        else:
            st.warning("Reddit score data not available for this dataset")
    
    with tab3:
        st.subheader("Keyword Analysis")
        
        if keyword_analysis['top_positive'] or keyword_analysis['top_negative']:
            col_pos, col_neg = st.columns(2)
            
            with col_pos:
                st.subheader("🔝 Most Positive Keywords")
                if keyword_analysis['top_positive']:
                    pos_keywords = pd.DataFrame([
                        {'keyword': k, 'avg_sentiment': v['avg_sentiment'], 'frequency': v['frequency']}
                        for k, v in keyword_analysis['top_positive'].items()
                    ])
                    fig_pos = px.bar(
                        pos_keywords.head(10),
                        x='avg_sentiment',
                        y='keyword',
                        orientation='h',
                        title="Top 10 Positive Keywords",
                        labels={'avg_sentiment': 'Average Sentiment Score', 'keyword': 'Keyword'}
                    )
                    st.plotly_chart(fig_pos, use_container_width=True)
                else:
                    st.info("No positive keywords found")
            
            with col_neg:
                st.subheader("🔻 Most Negative Keywords")
                if keyword_analysis['top_negative']:
                    neg_keywords = pd.DataFrame([
                        {'keyword': k, 'avg_sentiment': v['avg_sentiment'], 'frequency': v['frequency']}
                        for k, v in keyword_analysis['top_negative'].items()
                    ])
                    fig_neg = px.bar(
                        neg_keywords.head(10),
                        x='avg_sentiment',
                        y='keyword',
                        orientation='h',
                        title="Top 10 Negative Keywords",
                        labels={'avg_sentiment': 'Average Sentiment Score', 'keyword': 'Keyword'}
                    )
                    st.plotly_chart(fig_neg, use_container_width=True)
                else:
                    st.info("No negative keywords found")
        else:
            st.warning("No keyword analysis available for this dataset")
    
    with tab4:
        st.subheader("Top Posts by Sentiment")
        
        col_pos_posts, col_neg_posts = st.columns(2)
        
        with col_pos_posts:
            st.subheader("🔝 Most Positive Posts")
            try:
                top_positive = get_top_posts(filtered_df, 'compound', 5)
                for idx, row in top_positive.iterrows():
                    with st.expander(f"Score: {row['sentiment_compound']:.3f} | Reddit: {row.get('score', 'N/A')}"):
                        st.write(f"**Title:** {row['title']}")
                        st.write(f"**Text:** {row['clean_text'][:200]}...")
            except Exception as e:
                st.error(f"Error loading positive posts: {e}")
        
        with col_neg_posts:
            st.subheader("🔻 Most Negative Posts")
            try:
                top_negative = get_bottom_posts(filtered_df, 'compound', 5)
                for idx, row in top_negative.iterrows():
                    with st.expander(f"Score: {row['sentiment_compound']:.3f} | Reddit: {row.get('score', 'N/A')}"):
                        st.write(f"**Title:** {row['title']}")
                        st.write(f"**Text:** {row['clean_text'][:200]}...")
            except Exception as e:
                st.error(f"Error loading negative posts: {e}")
    
    # Data table
    st.header("📋 Data Table")
    
    # Show/hide columns
    available_columns = ['id', 'title', 'clean_text', 'sentiment_compound', 'sentiment_pos', 'sentiment_neu', 'sentiment_neg', 'score', 'keywords']
    existing_columns = [col for col in available_columns if col in filtered_df.columns]
    
    selected_columns = st.multiselect(
        "Select columns to display:",
        existing_columns,
        default=['title', 'sentiment_compound', 'score'] if all(col in filtered_df.columns for col in ['title', 'sentiment_compound', 'score']) else existing_columns[:5]
    )
    
    if selected_columns:
        display_df = filtered_df[selected_columns].copy()
        
        # Pagination
        page_size = st.selectbox("Posts per page:", [10, 25, 50, 100], index=1)
        
        total_pages = len(display_df) // page_size + (1 if len(display_df) % page_size > 0 else 0)
        page = st.selectbox("Page:", range(1, total_pages + 1), index=0)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        st.dataframe(
            display_df.iloc[start_idx:end_idx],
            use_container_width=True,
            height=400
        )
        
        st.info(f"Showing posts {start_idx + 1}-{min(end_idx, len(display_df))} of {len(display_df)}")
    else:
        st.warning("No columns selected for display")
    
    # Footer
    st.markdown("---")
    st.markdown("**Market Sentiment Dashboard** | Generated at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
