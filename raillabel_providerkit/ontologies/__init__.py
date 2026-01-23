# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Package for built-in ontology and schema definitions."""

from .manager import (
    get_ontology_path,
    get_schema_path,
    list_available_ontologies,
    list_available_schemas,
)

__all__ = [
    "get_ontology_path",
    "get_schema_path",
    "list_available_ontologies",
    "list_available_schemas",
]
