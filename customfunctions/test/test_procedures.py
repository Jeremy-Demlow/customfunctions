import pytest
from pathlib import Path
import sys
from unittest.mock import patch

from customfunctions.common import (
    is_snowflake_environment,
    find_config_file,
    get_config_path,
    load_config
)

# Import the functions to test
from customfunctions.procedures import hello_procedure



def test_hello_procedure_no_config(temp_working_dir):
    """Test hello procedure with no config file."""
    with patch('customfunctions.common.find_config_file', return_value=None):
        result = hello_procedure(name="Test")
        assert result == "Hello, Test!"

def test_hello_procedure_default_config():
    """Test hello procedure with default config."""
    result = hello_procedure(name="Test")
    assert result == "Hello, Test! YAML FOR THE WIN"

# Remove the original test_hello_procedure_basic since we've split it into two tests

def test_hello_procedure_with_config(temp_config_file):
    """Test hello procedure with custom config file."""
    with patch('pathlib.Path.cwd', return_value=temp_config_file.parent.parent.parent):
        result = hello_procedure(name="Test")
        assert result == "Hello, Test! Have a great day!"

def test_hello_procedure_with_session(mock_snowflake_session):
    """Test hello procedure with Snowflake session."""
    result = hello_procedure(session=mock_snowflake_session, name="Test")
    assert result.startswith("Hello, Test")

def test_hello_procedure_error_handling():
    """Test hello procedure error handling."""
    with patch('customfunctions.procedures.get_config_path', side_effect=Exception("Test error")):
        result = hello_procedure(name="Test")
        assert result == "Hello, Test!"

def test_full_integration(temp_config_file):
    """Test full integration of all components."""
    with patch('pathlib.Path.cwd', return_value=temp_config_file.parent.parent.parent):
        assert not is_snowflake_environment()
        config_path = get_config_path()
        assert config_path.exists()
        config = load_config(config_path)
        assert config.get('added_word') == 'Have a great day!'
        result = hello_procedure(name="Integration")
        assert result == "Hello, Integration! Have a great day!"