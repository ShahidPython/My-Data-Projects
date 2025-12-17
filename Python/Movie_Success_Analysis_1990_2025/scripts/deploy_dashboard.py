#!/usr/bin/env python3
"""
Dashboard deployment script for Movie Success Analysis.
Launches an interactive dashboard with results.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import yaml
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import load_processed_data
from src.models.predictor import predict_success

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_dashboard_data():
    """Load data for dashboard."""
    logger.info("Loading dashboard data...")
    
    # Load processed data
    df = load_processed_data()
    if df is None:
        logger.error("No processed data found. Run pipeline first.")
        return None
    
    # Load predictions
    model_path = project_root / 'results' / 'model_performance.pkl'
    if model_path.exists():
        predictions = predict_success(df, str(model_path))
    else:
        predictions = df.copy()
        predictions['predicted_success'] = 0
        predictions['success_probability'] = 0.5
        predictions['success_category'] = 'Unknown'
    
    logger.info(f"Dashboard data loaded: {len(predictions):,} records")
    return predictions

def create_dashboard_app(df):
    """Create Dash dashboard application."""
    
    # Load configuration
    config_path = project_root / 'config' / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.DARKLY],
        title="Movie Success Analysis Dashboard",
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
    )
    
    # Calculate metrics for KPI cards
    total_movies = len(df)
    success_rate = (df['predicted_success'].mean() * 100) if 'predicted_success' in df.columns else 0
    avg_genres = df['genre_count'].mean() if 'genre_count' in df.columns else 0
    recent_movies = len(df[df['year'] >= 2020]) if 'year' in df.columns else 0
    
    # Layout
    app.layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("🎬 Movie Success Analysis Dashboard", className="text-center my-4"),
                html.P("Interactive analysis of movie production trends (1990-2025)", 
                      className="text-center text-muted mb-4")
            ], width=12)
        ]),
        
        # KPI Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{total_movies:,}", className="card-title"),
                        html.P("Total Movies", className="card-text")
                    ])
                ], className="text-center shadow")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{success_rate:.1f}%", className="card-title text-success"),
                        html.P("Predicted Success Rate", className="card-text")
                    ])
                ], className="text-center shadow")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{avg_genres:.1f}", className="card-title"),
                        html.P("Avg Genres per Movie", className="card-text")
                    ])
                ], className="text-center shadow")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{recent_movies:,}", className="card-title"),
                        html.P("Movies Since 2020", className="card-text")
                    ])
                ], className="text-center shadow")
            ], md=3)
        ], className="mb-4"),
        
        # Charts Row 1
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Movies Released by Year"),
                    dbc.CardBody([
                        dcc.Graph(id='year-trend-chart')
                    ])
                ], className="shadow")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Success Probability Distribution"),
                    dbc.CardBody([
                        dcc.Graph(id='success-distribution-chart')
                    ])
                ], className="shadow")
            ], md=6)
        ], className="mb-4"),
        
        # Charts Row 2
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Genre Analysis"),
                    dbc.CardBody([
                        dcc.Graph(id='genre-chart')
                    ])
                ], className="shadow")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Feature Correlation"),
                    dbc.CardBody([
                        dcc.Graph(id='correlation-chart')
                    ])
                ], className="shadow")
            ], md=6)
        ], className="mb-4"),
        
        # Data Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Movie Data Preview"),
                    dbc.CardBody([
                        html.Div(id='data-table-container')
                    ])
                ], className="shadow")
            ], width=12)
        ]),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P([
                    "Movie Success Analysis Dashboard v1.0 | ",
                    html.Small("Data: 1990-2025 | Last Updated: ", className="text-muted"),
                    html.Small(pd.Timestamp.now().strftime('%Y-%m-%d'), className="text-muted")
                ], className="text-center mt-4")
            ], width=12)
        ])
    ], fluid=True)
    
    # Callbacks
    @callback(
        Output('year-trend-chart', 'figure'),
        Input('year-trend-chart', 'id')
    )
    def update_year_trend(_):
        """Update year trend chart."""
        yearly_counts = df['year'].value_counts().sort_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=yearly_counts.index,
            y=yearly_counts.values,
            name='Movies',
            marker_color=config['visualization']['colors']['primary']
        ))
        fig.update_layout(
            title="Movie Releases Over Time",
            xaxis_title="Year",
            yaxis_title="Number of Movies",
            template="plotly_dark",
            hovermode='x unified'
        )
        return fig
    
    @callback(
        Output('success-distribution-chart', 'figure'),
        Input('success-distribution-chart', 'id')
    )
    def update_success_distribution(_):
        """Update success distribution chart."""
        if 'success_probability' in df.columns:
            fig = px.histogram(
                df, 
                x='success_probability',
                nbins=30,
                title="Distribution of Success Probability",
                labels={'success_probability': 'Success Probability'},
                color_discrete_sequence=[config['visualization']['colors']['secondary']]
            )
            fig.update_layout(template="plotly_dark")
            return fig
        return go.Figure()
    
    @callback(
        Output('genre-chart', 'figure'),
        Input('genre-chart', 'id')
    )
    def update_genre_chart(_):
        """Update genre analysis chart."""
        # Extract top genres
        genre_list = []
        for genres in df['genres'].dropna():
            genre_list.extend([g.strip() for g in str(genres).split(',')])
        
        genre_counts = pd.Series(genre_list).value_counts().head(15)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=genre_counts.index,
            x=genre_counts.values,
            orientation='h',
            marker_color=px.colors.qualitative.Set3,
            name='Genre Count'
        ))
        fig.update_layout(
            title="Top 15 Movie Genres",
            xaxis_title="Frequency",
            yaxis_title="Genre",
            template="plotly_dark",
            height=500
        )
        return fig
    
    @callback(
        Output('correlation-chart', 'figure'),
        Input('correlation-chart', 'id')
    )
    def update_correlation_chart(_):
        """Update correlation chart."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:8]
        if len(numeric_cols) > 2:
            corr_matrix = df[numeric_cols].corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.round(2).values,
                texttemplate='%{text}',
                hoverinfo='text'
            ))
            fig.update_layout(
                title="Feature Correlation Matrix",
                template="plotly_dark",
                height=500
            )
            return fig
        return go.Figure()
    
    @callback(
        Output('data-table-container', 'children'),
        Input('data-table-container', 'id')
    )
    def update_data_table(_):
        """Update data table."""
        display_cols = ['title', 'year', 'genres', 'cast_size']
        if 'success_category' in df.columns:
            display_cols.append('success_category')
        
        table_df = df[display_cols].head(10)
        
        return dbc.Table.from_dataframe(
            table_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="table-dark"
        )
    
    return app

def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("DEPLOYING MOVIE SUCCESS DASHBOARD")
    logger.info("=" * 60)
    
    # Load data
    df = load_dashboard_data()
    if df is None:
        print("❌ No data available. Please run the pipeline first.")
        print("   Run: python scripts/run_pipeline.py")
        sys.exit(1)
    
    # Create and run app
    app = create_dashboard_app(df)
    
    # Load configuration
    config_path = project_root / 'config' / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    host = config['dashboard']['host']
    port = config['dashboard']['port']
    debug = config['dashboard']['debug']
    
    logger.info(f"Dashboard will be available at: http://{host}:{port}")
    logger.info(f"Debug mode: {debug}")
    print(f"\n✅ Dashboard deployed successfully!")
    print(f"🌐 Open your browser and navigate to: http://{host}:{port}")
    print("🛑 Press CTRL+C to stop the server")
    
    # Run app
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main()