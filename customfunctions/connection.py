"""Helps Manage Snowflake Connection"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_connection.ipynb.

# %% auto 0
__all__ = ['logger', 'AuthenticationError', 'SnowflakeConnection']

# %% ../nbs/00_connection.ipynb 3
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from pydantic import BaseModel, field_validator
from snowflake.snowpark import Session
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import yaml
from logging import getLogger
import warnings
# Suppress the specific Pydantic warning about schema
warnings.filterwarnings("ignore", message="Field name \"schema\" .* shadows an attribute in parent \"BaseModel\"")

logger = getLogger(__name__)

# %% ../nbs/00_connection.ipynb 4
class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass

class SnowflakeConnection(BaseModel):
    """
    Unified Snowflake connection configuration and session management.
    Supports password, key-pair, and external authenticator methods with session caching.
    """
    account: str
    user: str
    password: Optional[str] = None
    private_key_path: Optional[Path] = None
    private_key_pem: Optional[str] = None
    authenticator: Optional[str] = None
    role: str = "DATASCIENTIST"
    warehouse: str = "DS_WH_XS"
    database: Optional[str] = None
    schema: Optional[str] = None
    query_tag: Optional[Dict[str, Any]] = None
    _session_cache: Dict[Tuple[str, str, Optional[str]], Session] = {}

    def _get_default_query_tag(self) -> Dict[str, Any]:
        """Get default query tag if none is provided."""
        return {
            "origin": "snowpark_session",
            "name": self.user,
            "version": {
                "major": 1,
                "minor": 0
            },
            "attributes": {
                "source": self.database or "DATASCIENCE",
                "warehouse": self.warehouse,
                "role": self.role
            }
        }

    def _set_query_tag(self, session: Session, custom_tag: Optional[Dict[str, Any]] = None) -> None:
        """Set query tag for the session."""
        try:
            session.query_tag = custom_tag if custom_tag is not None else self._get_default_query_tag()
            logger.info(f"Set query tag: {session.query_tag}")
        except Exception as e:
            logger.warning(f"Failed to set query tag: {str(e)}")

    @field_validator("private_key_path", mode="before")
    def ensure_path_object(cls, v):
        return Path(v) if v and not isinstance(v, Path) else v

    @classmethod
    def from_yaml(cls, yaml_file: str = 'snowflake_config.yaml') -> 'SnowflakeConnection':
        """Create configuration from YAML file with environment variable fallback."""
        config = {}
        
        # Try loading from YAML first
        if os.path.isfile(yaml_file):
            with open(yaml_file, 'r') as file:
                config = yaml.safe_load(file).get('snowflake', {})

        # Environment variables override YAML
        env_vars = {
            'SNOWFLAKE_ACCOUNT': 'account',
            'SNOWFLAKE_USER': 'user',
            'SNOWFLAKE_PASSWORD': 'password',
            'SNOWFLAKE_ROLE': 'role',
            'SNOWFLAKE_WAREHOUSE': 'warehouse',
            'SNOWFLAKE_DATABASE': 'database',
            'SNOWFLAKE_SCHEMA': 'schema',
            'SNOWFLAKE_PRIVATE_KEY_PATH': 'private_key_path',
            'SNOWFLAKE_AUTHENTICATOR': 'authenticator'
        }

        for env_var, config_key in env_vars.items():
            if value := os.getenv(env_var):
                config[config_key] = value

        return cls(**config)

    def _load_private_key(self) -> bytes:
        """Load and format private key from file or PEM string."""
        try:
            if self.private_key_pem:
                key_data = self.private_key_pem.encode()
            elif self.private_key_path:
                with open(self.private_key_path, "rb") as key_file:
                    key_data = key_file.read()
            else:
                raise AuthenticationError("No private key source available")

            p_key = serialization.load_pem_private_key(
                key_data,
                password=None,
                backend=default_backend()
            )
            return p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        except Exception as e:
            raise AuthenticationError(f"Error loading private key: {str(e)}")

    def get_connection_params(
        self,
        role: Optional[str] = None,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get connection parameters with optional overrides."""
        params = {
            "account": self.account,
            "user": self.user,
            "role": role or self.role,
            "warehouse": warehouse or self.warehouse,
        }

        if database or self.database:
            params["database"] = database or self.database
        if schema or self.schema:
            params["schema"] = schema or self.schema
        if self.authenticator:
            params["authenticator"] = self.authenticator
        elif self.private_key_pem or self.private_key_path:
            params["private_key"] = self._load_private_key()
        elif self.password:
            params["password"] = self.password
        else:
            raise AuthenticationError(
                "No authentication method provided. Please provide either "
                "authenticator, private_key, or password."
            )

        return params

    def get_session(
        self,
        role: Optional[str] = None,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        use_cache: bool = True,
        query_tag: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Get or create a Snowflake session.
        
        Args:
            role: Override default role
            warehouse: Override default warehouse
            database: Override default database
            schema: Override default schema
            use_cache: Whether to use session caching (default True)
            query_tag: Optional custom query tag
            
        Returns:
            Session: A Snowflake session object
        """
        final_role = role or self.role
        final_warehouse = warehouse or self.warehouse
        final_database = database or self.database
        
        if use_cache:
            cache_key = (final_role, final_warehouse, final_database)
            if cache_key in self._session_cache:
                session = self._session_cache[cache_key]
                if schema:
                    session.use_schema(schema)
                # Set query tag even for cached sessions
                self._set_query_tag(session, query_tag or self.query_tag)
                return session

        # Create new session
        params = self.get_connection_params(final_role, final_warehouse, final_database, schema)
        try:
            session = Session.builder.configs(params).create()
            logger.info(f"Created new session for {final_role}, {final_warehouse}, {final_database}")
            
            # Set query tag for new session
            self._set_query_tag(session, query_tag or self.query_tag)
            
            if use_cache:
                cache_key = (final_role, final_warehouse, final_database)
                self._session_cache[cache_key] = session
                logger.info(f"Created and cached new session for {cache_key}")
            
            return session
            
        except Exception as e:
            raise AuthenticationError(f"Failed to create session: {str(e)}")

    def close_all_sessions(self) -> None:
        """Close all cached sessions."""
        for session in self._session_cache.values():
            try:
                session.close()
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
        self._session_cache.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all_sessions()
