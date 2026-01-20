# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum

from raillabel_providerkit.exceptions import ValueDoesNotMatchTypeError


class AttributeType(Enum):
    """Enum of all valid RailLabel attribute types."""

    TEXT = "text"
    NUM = "num"
    BOOLEAN = "boolean"
    VEC = "vec"

    @classmethod
    def from_value(cls, attribute_value_class: type) -> AttributeType:
        """Return AttributeType based on class of attribute value.

        Parameters
        ----------
        attribute_value_class: type
            Class of the attribute value. Can be gathered by calling type()-function.

        Returns
        -------
        AttributeType
            Corresponding AttributeType.

        Raises
        ------
        ValueError
            if attribute value class does not correspond to an Attribute Type.

        """
        if attribute_value_class is str:
            return AttributeType.TEXT

        if attribute_value_class in [float, int]:
            return AttributeType.NUM

        if attribute_value_class is bool:
            return AttributeType.BOOLEAN

        if attribute_value_class in [list, tuple]:
            return AttributeType.VEC

        raise ValueDoesNotMatchTypeError(attribute_value_class)
