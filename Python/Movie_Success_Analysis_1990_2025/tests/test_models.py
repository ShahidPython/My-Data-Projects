import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.models.predictor import MovieSuccessPredictor

class TestMovieSuccessPredictor:
    """Test movie success prediction model."""
    
    def setup_method(self):
        """Create test data with realistic features."""
        np.random.seed(42)
        n_samples = 100
        
        self.test_df = pd.DataFrame({
            'year': np.random.choice(range(1990, 2024), n_samples),
            'genre_count': np.random.randint(1, 5, n_samples),
            'cast_size': np.random.randint(1, 10, n_samples),
            'title_length': np.random.randint(5, 50, n_samples),
            'title_word_count': np.random.randint(1, 5, n_samples),
            'has_director': np.random.choice([0, 1], n_samples),
            'years_since_1990': np.random.randint(0, 35, n_samples),
            'vote_average': np.random.uniform(1, 10, n_samples),
            'revenue': np.random.exponential(1000000, n_samples),
            'popularity': np.random.uniform(0, 100, n_samples)
        })
        
        # Create target based on some logic
        self.test_df['success_score'] = (
            self.test_df['vote_average'] * 0.4 +
            np.log1p(self.test_df['revenue']) * 0.3 +
            self.test_df['popularity'] * 0.3
        )
        self.threshold = self.test_df['success_score'].quantile(0.75)
        self.test_df['success'] = (self.test_df['success_score'] >= self.threshold).astype(int)
    
    def test_predictor_initialization(self):
        """Test predictor initialization."""
        predictor = MovieSuccessPredictor(model_type='random_forest')
        assert predictor.model is not None
        assert predictor.random_state == 42
    
    def test_prepare_features_training(self):
        """Test feature preparation during training."""
        predictor = MovieSuccessPredictor()
        X = predictor.prepare_features(self.test_df, is_training=True)
        
        assert isinstance(X, pd.DataFrame)
        assert len(X) == len(self.test_df)
        assert 'year' in X.columns
        assert not X.isnull().any().any()
    
    def test_prepare_features_prediction(self):
        """Test feature preparation during prediction."""
        predictor = MovieSuccessPredictor()
        
        # First prepare training to set feature columns
        X_train = predictor.prepare_features(self.test_df, is_training=True)
        
        # Then prepare for prediction
        X_pred = predictor.prepare_features(self.test_df.head(10), is_training=False)
        
        assert X_pred.shape[1] == X_train.shape[1]
        assert set(X_pred.columns) == set(X_train.columns)
    
    def test_create_target_distribution(self):
        """Test target creation logic."""
        predictor = MovieSuccessPredictor()
        y = predictor.create_target(self.test_df)
        
        assert isinstance(y, pd.Series)
        assert len(y) == len(self.test_df)
        assert set(y.unique()).issubset({0, 1})
        # Should be roughly 25% success (top quartile)
        assert 0.20 < y.mean() < 0.30, f"Target distribution skewed: {y.mean():.2f}"
    
    def test_train_model(self):
        """Test model training."""
        predictor = MovieSuccessPredictor()
        X = predictor.prepare_features(self.test_df, is_training=True)
        y = predictor.create_target(self.test_df)
        
        # Use small subset for quick test
        X_train = X[:80]
        y_train = y[:80]
        
        predictor.train(X_train, y_train, optimize=False)
        
        assert hasattr(predictor.model, 'predict')
        assert hasattr(predictor.model, 'predict_proba')
    
    def test_predict_method(self):
        """Test prediction method."""
        predictor = MovieSuccessPredictor()
        X = predictor.prepare_features(self.test_df, is_training=True)
        y = predictor.create_target(self.test_df)
        
        # Train on subset
        X_train = X[:80]
        y_train = y[:80]
        predictor.train(X_train, y_train, optimize=False)
        
        # Predict on remaining
        predictions, probabilities = predictor.predict(self.test_df.iloc[80:])
        
        assert len(predictions) == 20
        assert len(probabilities) == 20
        assert set(predictions).issubset({0, 1})
        assert all(0 <= p <= 1 for p in probabilities)
    
    def test_evaluate_method(self):
        """Test model evaluation."""
        predictor = MovieSuccessPredictor()
        X = predictor.prepare_features(self.test_df, is_training=True)
        y = predictor.create_target(self.test_df)
        
        # Split
        X_train, X_test = X[:80], X[80:]
        y_train, y_test = y[:80], y[80:]
        
        predictor.train(X_train, y_train, optimize=False)
        metrics = predictor.evaluate(X_test, y_test)
        
        assert isinstance(metrics, dict)
        expected_metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'confusion_matrix']
        assert all(key in metrics for key in expected_metrics)
        assert 0 <= metrics['accuracy'] <= 1
    
    def test_save_load_functionality(self):
        """Test model saving and loading."""
        import tempfile
        import os
        
        predictor = MovieSuccessPredictor()
        X = predictor.prepare_features(self.test_df, is_training=True)
        y = predictor.create_target(self.test_df)
        predictor.train(X[:50], y[:50], optimize=False)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            tmp_path = tmp.name
            
            # Save
            predictor.save(tmp_path)
            assert os.path.exists(tmp_path)
            
            # Load
            loaded_predictor = MovieSuccessPredictor.load(tmp_path)
            
            # Compare predictions
            pred1, prob1 = predictor.predict(self.test_df.head(5))
            pred2, prob2 = loaded_predictor.predict(self.test_df.head(5))
            
            np.testing.assert_array_equal(pred1, pred2)
            np.testing.assert_array_almost_equal(prob1, prob2, decimal=5)
        
        os.unlink(tmp_path)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])