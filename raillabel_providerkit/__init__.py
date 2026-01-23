# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""A library for annotation providers of raillabel-formatted data."""

from importlib import metadata

from . import format
from .convert import loader_classes
from .convert.convert import convert
from .export.export_scenes import export_scenes
from .ontologies import (
    get_ontology_path,
    get_schema_path,
    list_available_ontologies,
    list_available_schemas,
)
from .validation.validate import validate

try:
    __version__ = metadata.version("raillabel-providerkit")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0+unknown"
del metadata

__all__ = [
    "format",
    "loader_classes",
    "convert",
    "export_scenes",
    "validate",
    "get_ontology_path",
    "get_schema_path",
    "list_available_ontologies",
    "list_available_schemas",
]
