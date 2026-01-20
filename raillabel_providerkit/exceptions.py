# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT


class UnsupportedFormatError(Exception):
    """Raised when a loaded annotation file is not in a supported format."""

    __module__ = "raillabel_providerkit"

    def __init__(self) -> None:
        super().__init__("No loader could be found, that supported the provided data.")


class ValueDoesNotMatchTypeError(Exception):
    """Raised when the expected type of a field does not match its value."""

    __module__ = "raillabel_providerkit"

    def __init__(self, attribute_value_class: type) -> None:
        super().__init__(
            f"Type {attribute_value_class} does not correspond to a valid RailLabel attribute "
            "type. Supported types are str, float, int, bool, list, tuple."
        )


class SchemaError(Exception):
    """Raised when the data does not validate against a given schema."""

    __module__ = "raillabel_providerkit"


class OntologySchemaError(Exception):
    """Raised when the .yaml-file provided is not valid against the schema."""

    __module__ = "raillabel_providerkit"
