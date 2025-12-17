# Movie Success Analysis - Data Dictionary

## Overview
This document describes the datasets used in the Movie Success Analysis project, covering the period 1990-2025.

## Raw Dataset: `movies_1990_2025.csv`

### Source
- **Primary Source**: Wikipedia Movie Data (prust/wikipedia-movie-data)
- **Extraction Method**: API curl command with Python processing
- **Period Covered**: 1990-01-01 to 2025-12-31

### Schema
| Column Name | Data Type | Description | Example | Nullable |
|-------------|-----------|-------------|---------|----------|
| `title` | string | Movie title | "The Matrix" | No |
| `year` | integer | Release year | 1999 | No |
| `genres` | string | Comma-separated list of genres | "Action,Sci-Fi" | Yes |
| `director` | string | Movie director(s) | "Lana Wachowski, Lilly Wachowski" | Yes |
| `cast` | string | Main cast members (comma-separated) | "Keanu Reeves, Laurence Fishburne" | Yes |
| `plot` | string | Movie plot summary | "A computer hacker learns..." | Yes |
| `notes` | string | Additional notes | "Won 4 Academy Awards" | Yes |

## Processed Dataset: `movies_engineered.csv`

### Base Features (from raw data)
| Column | Type | Description |
|--------|------|-------------|
| `title` | string | Original movie title |
| `year` | integer | Release year (1990-2025) |
| `genres` | string | Cleaned genre list |
| `director` | string | Director name(s) |
| `cast` | string | Cast member list |

### Engineered Features

#### Temporal Features
| Feature | Type | Description | Range/Values |
|---------|------|-------------|--------------|
| `decade` | integer | Decade of release | 1990, 2000, 2010, 2020 |
| `release_era` | string | Categorical era | "90s", "2000s", "2010s", "2020s" |
| `years_since_1990` | integer | Years elapsed since 1990 | 0-35 |

#### Genre Features
| Feature | Type | Description |
|---------|------|-------------|
| `genre_count` | integer | Number of genres assigned | 1-5 |
| `genre_{name}` | binary | Genre presence flags | 0/1 (e.g., `genre_action`) |

#### Textual Features
| Feature | Type | Description |
|---------|------|-------------|
| `title_length` | integer | Character count in title |
| `title_word_count` | integer | Word count in title |
| `cast_size` | integer | Number of cast members listed |
| `has_director` | binary | Director information available |
| `has_ensemble_cast` | binary | Cast size > 5 members |

#### Composite Features
| Feature | Type | Description | Formula |
|---------|------|-------------|---------|
| `complexity_score` | float | Combined complexity metric | `0.3*genre_count + 0.2*cast_size + 0.1*title_word_count + 0.4*years_since_1990` |
| `success_score` | float | Success likelihood score | `0.4*vote_average + 0.3*log(revenue) + 0.3*popularity` |

#### Target Variables
| Feature | Type | Description | Derivation |
|---------|------|-------------|------------|
| `success` | binary | Success classification | Top 25% by `success_score` = 1 |
| `success_probability` | float | Model-predicted probability | 0.0-1.0 |
| `success_category` | string | Human-readable category | "High Potential", "Standard" |

## Model Outputs

### Model Performance File
`model_performance.pkl` contains:
- Trained Random Forest model
- Feature scaler
- Label encoders
- Performance metrics

### Visualization Outputs
Directory: `results/figures/`
- `year_trend.png` - Release trends over time
- `genre_dist.png` - Genre distribution
- `correlation_heatmap.png` - Feature correlations
- `feature_importance.png` - Model feature importance

## Data Quality Notes

### Known Issues
1. **Missing Values**: Some historical records have incomplete cast/director information
2. **Genre Consistency**: Genre names may vary slightly (e.g., "Sci-Fi" vs "Science Fiction")
3. **Year Accuracy**: Some entries may have approximate years

### Data Cleaning Applied
1. Removed duplicates based on (title, year, director)
2. Filled missing genres with "Unknown"
3. Standardized text encoding (UTF-8)
4. Filtered to 1990-2025 range

## Usage Notes
- All engineered features are reproducible via `src/features/engineering.py`
- Missing values are handled appropriately in each modeling stage
- Temporal features account for industry evolution over 35-year period

---
*Last Updated: Wednesday, December 17, 2025*
*Version: 1.0*