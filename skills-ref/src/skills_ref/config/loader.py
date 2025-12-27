"""
Configuration loaders for various sources.
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from .defaults import get_default_config
from .schema import ConfigSchema, validate_config


class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load configuration as a dictionary."""
        pass

    def load_config(self) -> ConfigSchema:
        """Load and parse configuration into ConfigSchema."""
        data = self.load()
        return ConfigSchema.from_dict(data)


class EnvConfigLoader(ConfigLoader):
    """
    Load configuration from environment variables.

    Environment variable naming convention:
    - Prefix: AGENTSKILLS_
    - Nested: Use double underscore (__)
    - Example: AGENTSKILLS_AUTH__JWT_SECRET

    All values are strings; type conversion happens during schema parsing.
    """

    def __init__(
        self,
        prefix: str = "AGENTSKILLS_",
        separator: str = "__",
    ):
        self.prefix = prefix
        self.separator = separator

    def load(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        result: Dict[str, Any] = {}

        for key, value in os.environ.items():
            if not key.startswith(self.prefix):
                continue

            # Remove prefix and split by separator
            config_key = key[len(self.prefix):]
            parts = config_key.lower().split(self.separator)

            # Build nested dictionary
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the value (with type conversion)
            current[parts[-1]] = self._convert_value(value)

        return result

    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate type."""
        # Boolean
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # JSON (for lists/dicts)
        if value.startswith("[") or value.startswith("{"):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        # String (default)
        return value


class FileConfigLoader(ConfigLoader):
    """
    Load configuration from a file.

    Supports JSON and YAML formats.
    """

    def __init__(self, path: str):
        self.path = Path(path)

    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.path.exists():
            raise FileNotFoundError(f"Config file not found: {self.path}")

        content = self.path.read_text()

        if self.path.suffix in (".yaml", ".yml"):
            return self._load_yaml(content)
        elif self.path.suffix == ".json":
            return json.loads(content)
        else:
            # Try JSON first, then YAML
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._load_yaml(content)

    def _load_yaml(self, content: str) -> Dict[str, Any]:
        """Load YAML content."""
        try:
            import yaml
            return yaml.safe_load(content) or {}
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML configuration files. "
                "Install with: pip install pyyaml"
            )


class CompositeConfigLoader(ConfigLoader):
    """
    Combine multiple configuration sources with priority.

    Later loaders override earlier ones.
    Typical order: defaults -> file -> environment
    """

    def __init__(self, loaders: List[ConfigLoader]):
        self.loaders = loaders

    def load(self) -> Dict[str, Any]:
        """Load and merge configuration from all sources."""
        result: Dict[str, Any] = {}

        for loader in self.loaders:
            try:
                data = loader.load()
                result = self._deep_merge(result, data)
            except (FileNotFoundError, PermissionError):
                # Skip missing files
                continue

        return result

    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @classmethod
    def standard(
        cls,
        config_file: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> "CompositeConfigLoader":
        """
        Create standard loader with typical priority:
        1. Environment defaults
        2. Config file (if provided)
        3. Environment variables

        Args:
            config_file: Path to config file (optional)
            environment: Environment name for defaults

        Returns:
            Configured CompositeConfigLoader
        """
        loaders: List[ConfigLoader] = [
            DefaultsLoader(environment=environment),
        ]

        if config_file:
            loaders.append(FileConfigLoader(config_file))

        loaders.append(EnvConfigLoader())

        return cls(loaders)


class DefaultsLoader(ConfigLoader):
    """Load default configuration for an environment."""

    def __init__(self, environment: Optional[str] = None):
        self.environment = environment

    def load(self) -> Dict[str, Any]:
        """Load default configuration."""
        config = get_default_config(self.environment)
        return config.to_dict()


def load_config(
    config_file: Optional[str] = None,
    environment: Optional[str] = None,
    validate: bool = True,
) -> ConfigSchema:
    """
    Load configuration with standard priority.

    Priority (later overrides earlier):
    1. Environment defaults
    2. Config file (if provided)
    3. Environment variables

    Args:
        config_file: Path to config file (JSON or YAML)
        environment: Environment name (development, testing, staging, production)
        validate: Whether to validate configuration

    Returns:
        Loaded and optionally validated ConfigSchema

    Raises:
        ConfigError: If validation fails
    """
    loader = CompositeConfigLoader.standard(
        config_file=config_file,
        environment=environment,
    )

    config = loader.load_config()

    if validate:
        validate_config(config)

    return config


def get_config_from_env() -> ConfigSchema:
    """
    Quick helper to load config from environment only.

    Uses AGENTSKILLS_ENV to determine base defaults,
    then applies any AGENTSKILLS_* overrides.
    """
    return load_config(validate=False)
