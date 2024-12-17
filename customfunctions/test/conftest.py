import pytest
import sys
import yaml
import tempfile
import os

from pathlib import Path
from unittest.mock import Mock, patch
from snowflake.snowpark import Session

@pytest.fixture
def mock_snowflake_session():
    """Create a mock Snowflake session."""
    return Mock(spec=Session)

@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the necessary directory structure
        config_dir = Path(temp_dir) / 'customfunctions' / 'files'
        config_dir.mkdir(parents=True)
        
        # Create a test config file
        config_path = config_dir / 'config.yaml'
        config_data = {'added_word': 'Have a great day!'}
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)
            
        yield config_path

@pytest.fixture
def mock_snowflake_env():
    """Mock Snowflake environment."""
    with patch.object(sys, '_xoptions', {'snowflake_import_directory': '/tmp/snowflake'}):
        yield

# Add any other shared fixtures or configuration that might be needed across tests
@pytest.fixture
def temp_working_dir():
    """Create a temporary working directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        yield Path(temp_dir)
        os.chdir(original_dir)