# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Built-in ontology definitions for raillabel-providerkit.

This module provides access to pre-built ontology parameter files that can be used
for scene validation. Instead of managing ontology files separately, you can use:

    from raillabel_providerkit.ontologies import get_ontology_path

    path = get_ontology_path("osdar26")
    issues = validate(scene_path, ontology=path)
"""

from pathlib import Path


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
        Path to the ontology YAML file

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
    ontology_path = Path(__file__).parent / ontology_file

    if not ontology_path.exists():
        msg = f"Ontology file not found: {ontology_path}"
        raise FileNotFoundError(msg)

    return ontology_path


def list_available_ontologies() -> list[str]:
    """List all available built-in ontologies.

    Returns
    -------
    list[str]
        List of available ontology names
    """
    return ["osdar26", "automatedtrain", "osdar23"]


__all__ = ["get_ontology_path", "list_available_ontologies"]
