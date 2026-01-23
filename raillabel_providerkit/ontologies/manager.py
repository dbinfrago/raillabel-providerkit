# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Built-in ontology definitions for raillabel-providerkit.

This module provides access to pre-built ontology parameter files that can be used
for scene validation. Instead of managing ontology files separately, you can use:

    from raillabel_providerkit.ontologies import get_ontology_path

    path = get_ontology_path("osdar26")
    issues = validate(scene_path, ontology=path)

All ontology files are stored centrally in the config/ontologies/ directory.
"""

from pathlib import Path


def _get_config_dir() -> Path:
    """Get the path to the config directory.

    Returns the config directory relative to the package root.
    Works both in development and when installed via pip.
    """
    # Go up from raillabel_providerkit/ontologies/manager.py to project root
    package_root = Path(__file__).parent.parent.parent
    config_dir = package_root / "config"

    if not config_dir.exists():
        msg = f"Config directory not found at: {config_dir}"
        raise FileNotFoundError(msg)

    return config_dir


def get_ontology_path(ontology_name: str) -> Path:
    """Get the path to a built-in ontology file.

    Parameters
    ----------
    ontology_name : str
        Name of the ontology to load. Supported values:
        - "osdar26": Extended railway environment ontology (25 classes)
        - "automatedtrain": Safety-critical classes for automated train operation
        - "osdar23": Original OSDAR23 dataset ontology

    Returns
    -------
    Path
        Path to the ontology YAML file (located in config/ontologies/)

    Raises
    ------
    ValueError
        If the ontology name is not recognized
    """
    valid_ontologies = {
        "osdar26": "osdar26.yaml",
        "automatedtrain": "automatedtrain.yaml",
        "osdar23": "osdar23.yaml",
    }

    if ontology_name not in valid_ontologies:
        msg = (
            f"Unknown ontology '{ontology_name}'. "
            f"Supported ontologies: {', '.join(valid_ontologies.keys())}"
        )
        raise ValueError(msg)

    ontology_file = valid_ontologies[ontology_name]
    ontology_path = _get_config_dir() / "ontologies" / ontology_file

    if not ontology_path.exists():
        msg = f"Ontology file not found: {ontology_path}"
        raise FileNotFoundError(msg)

    return ontology_path


def get_schema_path(schema_name: str) -> Path:
    """Get the path to a built-in schema file.

    Parameters
    ----------
    schema_name : str
        Name of the schema to load. Supported values:
        - "raillabel": RailLabel JSON schema
        - "understand_ai_t4": Understand.AI T4 format schema
        - "ontology": Ontology validation schema (v2)

    Returns
    -------
    Path
        Path to the schema file (located in config/schemas/)

    Raises
    ------
    ValueError
        If the schema name is not recognized
    """
    valid_schemas = {
        "raillabel": "raillabel_schema.json",
        "understand_ai_t4": "understand_ai_t4_schema.json",
        "ontology": "ontology_schema_v2.yaml",
    }

    if schema_name not in valid_schemas:
        msg = (
            f"Unknown schema '{schema_name}'. "
            f"Supported schemas: {', '.join(valid_schemas.keys())}"
        )
        raise ValueError(msg)

    schema_file = valid_schemas[schema_name]
    schema_path = _get_config_dir() / "schemas" / schema_file

    if not schema_path.exists():
        msg = f"Schema file not found: {schema_path}"
        raise FileNotFoundError(msg)

    return schema_path


def list_available_ontologies() -> list[str]:
    """List all available built-in ontologies.

    Returns
    -------
    list[str]
        List of available ontology names
    """
    return ["osdar26", "automatedtrain", "osdar23"]


def list_available_schemas() -> list[str]:
    """List all available built-in schemas.

    Returns
    -------
    list[str]
        List of available schema names
    """
    return ["raillabel", "understand_ai_t4", "ontology"]


__all__ = [
    "get_ontology_path",
    "get_schema_path",
    "list_available_ontologies",
    "list_available_schemas",
]
