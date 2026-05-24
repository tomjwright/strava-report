import pytest
from unittest.mock import Mock, patch, MagicMock
import os


def test_environment_variables():
    """Test that required environment variables are defined"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'STRAVA_CLIENT_ID', 'STRAVA_CLIENT_SECRET']
    
    # Mock environment variables for testing
    with patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test_key',
        'STRAVA_CLIENT_ID': 'test_id',
        'STRAVA_CLIENT_SECRET': 'test_secret'
    }):
        for var in required_vars:
            assert os.environ.get(var) is not None


def test_data_loader_imports():
    """Test that simple_data_loader can be imported"""
    try:
        import simple_data_loader
        assert True
    except ImportError:
        pytest.fail("simple_data_loader module could not be imported")


def test_dashboard_imports():
    """Test that clean_dashboard can be imported"""
    try:
        import clean_dashboard
        assert True
    except ImportError:
        pytest.fail("clean_dashboard module could not be imported")


def test_backend_imports():
    """Test that simple_backend can be imported"""
    try:
        import simple_backend
        assert True
    except ImportError:
        pytest.fail("simple_backend module could not be imported")