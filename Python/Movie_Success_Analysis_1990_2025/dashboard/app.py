import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.data.loader import load_processed_data
    from src.models.predictor import predict_success
    data_loaded = True
except ImportError:
    data_loaded = False
    print("Warning: Could not import project modules. Using sample data.")

# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Load or create sample data
if data_loaded:
    try:
        df = load_processed_data()
        if df is not None:
            model_path = Path(__file__).parent.parent / 'results' / 'model_performance.pkl'
            if model_path.exists():
                df = predict_success(df, str(model_path))
            else:
                df['success_probability'] = 0.5
                df['success_category'] = 'Unknown'
    except:
        df = None
        data_loaded = False

if not data_loaded or df is None:
    # Create sample data for dashboard demonstration
    np.random.seed(42)
    n_samples = 500
    df = pd.DataFrame({
        'title': [f'Movie_{i}' for i in range(n_samples)],
        'year': np.random.choice(range(1990, 2024), n_samples),
        'genres': np.random.choice(['Action,Drama', 'Comedy,Romance', 'Thriller,Horror', 'Sci-Fi,Adventure'], n_samples),
        'success_probability': np.random.beta(2, 5, n_samples),
        'genre_count': np.random.randint(1, 4, n_samples),
        'cast_size': np.random.randint(2, 8, n_samples)
    })
    df['success_category'] = pd.cut(df['success_probability'], 
                                     bins=[0, 0.3, 0.7, 1],
                                     labels=['Low', 'Medium', 'High'])

# Calculate metrics
total_movies = len(df)
avg_success_prob = df['success_probability'].mean() * 100
successful_movies = len(df[df['success_probability'] > 0.6])
success_rate = (successful_movies / total_movies * 100) if total_movies > 0 else 0

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🎬 Movie Success Analytics Dashboard", 
                   className="text-center my-4 text-primary"),
            html.P("Interactive analysis of movie trends and success predictions (1990-2025)",
                  className="text-center text-muted mb-4 lead")
        ], width=12)
    ]),
    
    # KPI Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"{total_movies:,}", className="card-title text-center"),
                    html.P("Total Movies Analyzed", className="card-text text-center text-muted")
                ])
            ], className="shadow border-0")
        ], md=3, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"{avg_success_prob:.1f}%", className="card-title text-center text-success"),
                    html.P("Average Success Probability", className="card-text text-center text-muted")
                ])
            ], className="shadow border-0")
        ], md=3, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"{success_rate:.1f}%", className="card-title text-center text-warning"),
                    html.P("Success Rate (Prob > 60%)", className="card-text text-center text-muted")
                ])
            ], className="shadow border-0")
        ], md=3, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2(f"{df['year'].max()}", className="card-title text-center text-info"),
                    html.P("Latest Year in Data", className="card-text text-center text-muted")
                ])
            ], className="shadow border-0")
        ], md=3, className="mb-4")
    ], className="mb-5"),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("📈 Movie Releases by Year", className="mb-0")
                ], className="bg-dark"),
                dbc.CardBody([
                    dcc.Graph(id='year-trend-chart')
                ])
            ], className="shadow")
        ], lg=6, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("📊 Success Probability Distribution", className="mb-0")
                ], className="bg-dark"),
                dbc.CardBody([
                    dcc.Graph(id='success-dist-chart')
                ])
            ], className="shadow")
        ], lg=6, className="mb-4")
    ]),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("🎭 Genre Analysis", className="mb-0")
                ], className="bg-dark"),
                dbc.CardBody([
                    dcc.Graph(id='genre-chart')
                ])
            ], className="shadow")
        ], lg=6, className="mb-4"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("🔗 Feature Relationships", className="mb-0")
                ], className="bg-dark"),
                dbc.CardBody([
                    dcc.Graph(id='scatter-chart')
                ])
            ], className="shadow")
        ], lg=6, className="mb-4")
    ]),
    
    # Data Table and Filters
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("🎥 Movie Data Explorer", className="mb-0 d-inline"),
                    html.Small(" (Top 50 movies)", className="text-muted ml-2")
                ], className="bg-dark"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Filter by Year Range:", className="font-weight-bold"),
                            dcc.RangeSlider(
                                id='year-slider',
                                min=df['year'].min(),
                                max=df['year'].max(),
                                step=1,
                                marks={year: str(year) for year in range(df['year'].min(), df['year'].max()+1, 5)},
                                value=[df['year'].min(), df['year'].max()],
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], md=6),
                        
                        dbc.Col([
                            html.Label("Filter by Success Category:", className="font-weight-bold"),
                            dcc.Dropdown(
                                id='category-filter',
                                options=[
                                    {'label': 'All Categories', 'value': 'all'},
                                    {'label': 'High Success', 'value': 'High'},
                                    {'label': 'Medium Success', 'value': 'Medium'},
                                    {'label': 'Low Success', 'value': 'Low'}
                                ],
                                value='all',
                                clearable=False,
                                className="text-dark"
                            )
                        ], md=6)
                    ], className="mb-4"),
                    
                    html.Div(id='data-table-container')
                ])
            ], className="shadow")
        ], width=12)
    ], className="mb-5"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                "Movie Success Analysis Dashboard v1.0 | ",
                html.Small(f"Data Range: {df['year'].min()}-{df['year'].max()} | ", className="text-muted"),
                html.Small(f"Total Records: {total_movies:,} | ", className="text-muted"),
                html.Small("Last Updated: ", className="text-muted"),
                html.Small(pd.Timestamp.now().strftime('%Y-%m-%d'), className="text-muted")
            ], className="text-center mt-4")
        ], width=12)
    ])
], fluid=True, className="px-4")

# Callbacks
@app.callback(
    Output('year-trend-chart', 'figure'),
    Input('year-slider', 'value')
)
def update_year_trend(year_range):
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    yearly_counts = filtered_df['year'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=yearly_counts.index,
        y=yearly_counts.values,
        name='Movies Released',
        marker_color='#2E86AB',
        hovertemplate='Year: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add trend line
    if len(yearly_counts) > 1:
        fig.add_trace(go.Scatter(
            x=yearly_counts.index,
            y=yearly_counts.rolling(window=3, center=True).mean(),
            name='3-Year Moving Avg',
            line=dict(color='#FF6B6B', width=3),
            mode='lines'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        title=f"Movie Releases ({year_range[0]}-{year_range[1]})",
        xaxis_title="Release Year",
        yaxis_title="Number of Movies",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

@app.callback(
    Output('success-dist-chart', 'figure'),
    Input('year-slider', 'value')
)
def update_success_dist(year_range):
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    fig = px.histogram(
        filtered_df,
        x='success_probability',
        nbins=30,
        title="Distribution of Success Probability",
        labels={'success_probability': 'Success Probability'},
        color_discrete_sequence=['#A23B72'],
        opacity=0.8
    )
    
    fig.update_layout(
        template='plotly_dark',
        xaxis_title="Success Probability",
        yaxis_title="Count",
        bargap=0.1,
        showlegend=False
    )
    
    # Add mean line
    mean_prob = filtered_df['success_probability'].mean()
    fig.add_vline(x=mean_prob, line_dash="dash", line_color="white", 
                  annotation_text=f"Mean: {mean_prob:.2f}")
    
    return fig

@app.callback(
    Output('genre-chart', 'figure'),
    Input('year-slider', 'value')
)
def update_genre_chart(year_range):
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    # Extract genres
    genre_list = []
    for genres in filtered_df['genres'].dropna():
        genre_list.extend([g.strip() for g in str(genres).split(',')])
    
    genre_counts = pd.Series(genre_list).value_counts().head(10)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=genre_counts.index,
        x=genre_counts.values,
        orientation='h',
        marker_color=px.colors.qualitative.Set3,
        hovertemplate='Genre: %{y}<br>Count: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        template='plotly_dark',
        title="Top 10 Movie Genres",
        xaxis_title="Number of Movies",
        yaxis_title="Genre",
        height=400,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('scatter-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('category-filter', 'value')]
)
def update_scatter_chart(year_range, category):
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    if category != 'all' and 'success_category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['success_category'] == category]
    
    fig = px.scatter(
        filtered_df,
        x='genre_count',
        y='cast_size',
        size='success_probability',
        color='success_probability',
        hover_data=['title', 'year'],
        title="Genre Count vs Cast Size",
        labels={
            'genre_count': 'Number of Genres',
            'cast_size': 'Cast Size',
            'success_probability': 'Success Probability'
        },
        color_continuous_scale='viridis',
        size_max=20
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        coloraxis_colorbar=dict(title="Success Prob")
    )
    
    return fig

@app.callback(
    Output('data-table-container', 'children'),
    [Input('year-slider', 'value'),
     Input('category-filter', 'value')]
)
def update_data_table(year_range, category):
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    if category != 'all' and 'success_category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['success_category'] == category]
    
    # Select and format columns for display
    display_cols = ['title', 'year', 'genres']
    if 'success_probability' in filtered_df.columns:
        display_cols.append('success_probability')
    if 'success_category' in filtered_df.columns:
        display_cols.append('success_category')
    
    table_df = filtered_df[display_cols].head(50).copy()
    
    # Format columns
    if 'success_probability' in table_df.columns:
        table_df['success_probability'] = table_df['success_probability'].apply(lambda x: f"{x:.1%}")
    
    return dbc.Table.from_dataframe(
        table_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="table-dark table-sm",
        style={'fontSize': '0.9em'}
    )

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)