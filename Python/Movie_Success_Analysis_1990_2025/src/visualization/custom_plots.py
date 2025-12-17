import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')

def plot_year_trend(df, save_path=None):
    """
    Plot movie release trends by year with moving average.
    
    Parameters:
    df (pd.DataFrame): Movie dataset with 'year' column
    save_path (str): Path to save the figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar plot
    yearly_counts = df['year'].value_counts().sort_index()
    ax1.bar(yearly_counts.index, yearly_counts.values, 
            color='steelblue', edgecolor='black', alpha=0.7)
    ax1.set_xlabel('Release Year', fontsize=12)
    ax1.set_ylabel('Number of Movies', fontsize=12)
    ax1.set_title('Movie Releases by Year (1990-2025)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Line plot with moving average
    moving_avg = yearly_counts.rolling(window=3, center=True).mean()
    ax2.plot(yearly_counts.index, yearly_counts.values, 
             'o-', alpha=0.5, label='Annual Count', color='gray')
    ax2.plot(moving_avg.index, moving_avg.values, 
             'r-', linewidth=3, label='3-Year Moving Avg')
    ax2.fill_between(moving_avg.index, 0, moving_avg.values, alpha=0.2, color='red')
    ax2.set_xlabel('Release Year', fontsize=12)
    ax2.set_ylabel('Number of Movies', fontsize=12)
    ax2.set_title('Release Trends with Moving Average', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_genre_distribution(df, top_n=15, save_path=None):
    """
    Plot horizontal bar chart of top movie genres.
    
    Parameters:
    df (pd.DataFrame): Movie dataset with 'genres' column
    top_n (int): Number of top genres to display
    save_path (str): Path to save the figure
    """
    # Extract and count genres
    genre_list = []
    for genres in df['genres'].dropna():
        genre_list.extend([g.strip() for g in str(genres).split(',')])
    
    genre_counts = pd.Series(genre_list).value_counts().head(top_n)
    
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, top_n))
    bars = plt.barh(range(len(genre_counts)), genre_counts.values, color=colors)
    
    # Add value labels
    for i, (genre, count) in enumerate(zip(genre_counts.index, genre_counts.values)):
        plt.text(count + max(genre_counts.values)*0.01, i, 
                f'{count:,}', va='center', fontsize=10)
    
    plt.yticks(range(len(genre_counts)), genre_counts.index, fontsize=11)
    plt.xlabel('Frequency', fontsize=12)
    plt.title(f'Top {top_n} Movie Genres (1990-2025)', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(True, alpha=0.3, axis='x')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_feature_correlation(df, features=None, save_path=None):
    """
    Plot correlation heatmap for selected features.
    
    Parameters:
    df (pd.DataFrame): Dataset with numerical features
    features (list): List of feature names to include
    save_path (str): Path to save the figure
    """
    if features is None:
        # Select numeric columns automatically
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        features = [col for col in numeric_cols if df[col].nunique() > 1][:10]
    
    corr_matrix = df[features].corr()
    
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = LinearSegmentedColormap.from_list('custom', ['#2E86AB', '#F6F5F5', '#A23B72'])
    
    sns.heatmap(corr_matrix, 
                mask=mask,
                annot=True, 
                fmt='.2f',
                cmap=cmap,
                center=0,
                square=True,
                linewidths=1,
                cbar_kws={'shrink': 0.8})
    
    plt.title('Feature Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(fontsize=11)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_model_importance(feature_names, importances, save_path=None):
    """
    Plot feature importance from machine learning model.
    
    Parameters:
    feature_names (list): Names of features
    importances (list): Importance scores
    save_path (str): Path to save the figure
    """
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=True)
    
    plt.figure(figsize=(10, 8))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(importance_df)))
    bars = plt.barh(range(len(importance_df)), importance_df['importance'], color=colors)
    
    # Add value labels
    for i, (_, row) in enumerate(importance_df.iterrows()):
        plt.text(row['importance'] + max(importances)*0.01, i, 
                f'{row["importance"]:.3f}', va='center', fontsize=10)
    
    plt.yticks(range(len(importance_df)), importance_df['feature'], fontsize=11)
    plt.xlabel('Importance Score', fontsize=12)
    plt.title('Feature Importance Analysis', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='x')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def create_dashboard_figures(df, output_dir='../results/figures/'):
    """
    Generate all standard visualization figures for dashboard.
    
    Parameters:
    df (pd.DataFrame): Complete movie dataset
    output_dir (str): Directory to save all figures
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    plot_year_trend(df, save_path=os.path.join(output_dir, 'year_trend.png'))
    plot_genre_distribution(df, save_path=os.path.join(output_dir, 'genre_dist.png'))
    
    # Select numeric features for correlation
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()[:8]
    if len(numeric_features) > 3:
        plot_feature_correlation(df[numeric_features], 
                                save_path=os.path.join(output_dir, 'correlation_heatmap.png'))
    
    print(f"✓ Dashboard figures saved to {output_dir}")