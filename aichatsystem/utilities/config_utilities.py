#!/usr/bin/env python3
"""
The functions for get and set configs.
"""

import logging
from pathlib import Path
from typing import Any

import yaml  # pip install pyyaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(config_file_name: str = './configs/sample_config.yaml') -> dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_file_name (str): The name of the configuration file. Defaults to './configs/sample_config.yaml'.

    Returns:
        dict[str, Any]: A dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    try:
        with Path(config_file_name).open('r', encoding='utf-8') as f:
            configs = yaml.safe_load(f)
    except FileNotFoundError:
        logging.exception('Configuration file "%s" not found.', config_file_name)
        raise
    except yaml.YAMLError:
        logging.exception('Error parsing YAML file "%s"', config_file_name)
        raise

    return configs


def get_config_value(key: str, default: Any = None) -> Any:  # noqa: ANN401
    """
    Get a configuration value by key, with an optional default value.

    NOTE: The configuration value is unknown, so "Any" is allowed.

    Args:
        key (str): The configuration key to retrieve.
        default (Any, optional):
            The default value to return if the key is not found. Defaults to None.

    Returns:
        Any: The configuration value associated with the key, or the default value if not found.
    """
    configs = load_config()
    return configs.get(key, default)
