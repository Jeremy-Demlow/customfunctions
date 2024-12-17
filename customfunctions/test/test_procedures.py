import pytest
from pathlib import Path
import sys
from unittest.mock import patch

# Import the functions to test
from customfunctions.procedures import (
    is_snowflake_environment,
    find_config_file,
    get_config_path,
    load_config,
    hello_procedure
)

# Tests for is_snowflake_environment
def test_is_snowflake_environment_false():
    """Test detection of non-Snowflake environment."""
    assert not is_snowflake_environment()

def test_is_snowflake_environment_true(mock_snowflake_env):
    """Test detection of Snowflake environment."""
    assert is_snowflake_environment()

# Tests for find_config_file
def test_find_config_file_exists(temp_config_file):
    """Test finding config file when it exists."""
    with patch('pathlib.Path.cwd', return_value=temp_config_file.parent.parent.parent):
        found_path = find_config_file()
        assert found_path is not None
        assert found_path.exists()
        assert found_path.name == 'config.yaml'

def test_find_config_file_not_exists(temp_working_dir):
    """Test behavior when config file doesn't exist."""
    found_path = find_config_file()
    assert found_path is None

# Tests for get_config_path
def test_get_config_path_local(temp_config_file):
    """Test getting config path in local environment."""
    with patch('pathlib.Path.cwd', return_value=temp_config_file.parent.parent.parent):
        config_path = get_config_path()
        assert config_path.exists()
        assert str(config_path).endswith('customfunctions/files/config.yaml')

@patch('zipfile.ZipFile')
def test_get_config_path_snowflake(mock_zipfile, mock_snowflake_env):
    """Test getting config path in Snowflake environment."""
    config_path = get_config_path()
    assert str(config_path) == '/tmp/customfunctions/customfunctions/files/config.yaml'

# Tests for load_config
def test_load_config_exists(temp_config_file):
    """Test loading existing config file."""
    config = load_config(temp_config_file)
    assert isinstance(config, dict)
    assert config.get('added_word') == 'Have a great day!'

def test_load_config_not_exists(temp_working_dir):
    """Test loading non-existent config file."""
    config = load_config(Path('nonexistent.yaml'))
    assert isinstance(config, dict)
    assert len(config) == 0

def test_load_config_invalid_yaml(temp_working_dir):
    """Test loading invalid YAML file."""
    invalid_yaml = temp_working_dir / "invalid.yaml"
    invalid_yaml.write_text("invalid: yaml: content")
    config = load_config(invalid_yaml)
    assert isinstance(config, dict)
    assert len(config) == 0


def test_hello_procedure_no_config(temp_working_dir):
    """Test hello procedure with no config file."""
    with patch('customfunctions.procedures.find_config_file', return_value=None):
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