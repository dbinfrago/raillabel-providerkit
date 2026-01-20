# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT
"""A library for annotation providers of raillabel-formatted data."""

from importlib import metadata

from . import format
from .convert import loader_classes
from .convert.convert import convert
from .ontologies import get_ontology_path, list_available_ontologies
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
    "validate",
    "get_ontology_path",
    "list_available_ontologies",
]
