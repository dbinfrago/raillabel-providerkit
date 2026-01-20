# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT
from __future__ import annotations

import abc
from collections import Counter
from dataclasses import dataclass
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType
from raillabel_providerkit.validation.validate_ontology._ontology_classes._scope import _Scope


@dataclass
class _Attribute(abc.ABC):
    """Attribute definition of an object class.

    Parameters
    ----------
    optional: bool
        Whether the attribute is required to exist in every annotation of the object class.
    scope: _Scope
        The scope all attributes following this definition have to adhere to.
    sensor_types: list[str]
        The sensors for which annotations are allowed to have this attribute.
    """

    optional: bool
    scope: _Scope
    sensor_types: list[str]

    @property
    @abc.abstractmethod
    def ATTRIBUTE_TYPE_IDENTIFIER(self) -> str:  # noqa: N802
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def PYTHON_TYPE(self) -> type:  # noqa: N802
        raise NotImplementedError

    @classmethod
    def supports(cls, attribute_dict: dict) -> bool:
        return (
            "attribute_type" in attribute_dict
            and attribute_dict["attribute_type"] == cls.ATTRIBUTE_TYPE_IDENTIFIER
        )

    @classmethod
    def fromdict(cls, attribute_dict: dict) -> _Attribute:
        if not cls.supports(attribute_dict):
            raise ValueError

        return cls(
            optional=attribute_dict.get("optional", False),
            scope=_Scope(attribute_dict.get("scope", "annotation")),
            sensor_types=attribute_dict.get("sensor_types", ["camera", "lidar", "radar"]),
        )

    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_value: bool | float | str | list,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        if isinstance(attribute_value, self.PYTHON_TYPE):
            return []

        return [
            Issue(
                type=IssueType.ATTRIBUTE_TYPE,
                identifiers=identifiers,
                reason=(
                    f"Attribute '{attribute_name}' is of type "
                    f"{attribute_value.__class__.__name__} (should be {self.PYTHON_TYPE.__name__})."
                ),
            )
        ]

    def check_scope_for_two_annotations(  # noqa: PLR0911
        self,
        attribute_name: str,
        attribute_value_1: bool | float | str | list,
        attribute_value_2: bool | float | str | list,
        annotation_1_identifiers: IssueIdentifiers,
        annotation_2_identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        if self.scope == _Scope.ANNOTATION:
            return []

        if (
            self.scope == _Scope.FRAME
            and annotation_1_identifiers.frame != annotation_2_identifiers.frame
        ):
            return []

        if annotation_1_identifiers.object != annotation_2_identifiers.object:
            return []

        if type(attribute_value_1) is not type(attribute_value_2):
            # NOTE: this is covered by check_type_and_value
            return []

        # If the attribute is a list, it is not an error if the lists have the same
        # values, but are in a different order
        if (
            type(attribute_value_1) is list
            and type(attribute_value_2) is list
            and Counter(attribute_value_1) == Counter(attribute_value_2)
        ):
            return []

        if attribute_value_1 != attribute_value_2:
            return [
                Issue(
                    type=IssueType.ATTRIBUTE_SCOPE,
                    identifiers=annotation_2_identifiers,
                    reason=(
                        f"Attribute '{attribute_name}' is inconsistent with referenced"
                        f" annotation '{annotation_1_identifiers.annotation}'"
                        f" (considering scope {self.scope})"
                    ),
                )
            ]

        return []


def attribute_classes() -> list[type[_Attribute]]:
    """Return dictionary with Attribute child classes."""
    return ATTRIBUTE_CLASSES


def _collect_attribute_classes() -> None:
    """Collect attribute child classes and store them."""
    package_dir = str(Path(__file__).resolve().parent)
    for _, module_name, _ in iter_modules([package_dir]):
        module = import_module(
            f"raillabel_providerkit.validation.validate_ontology._ontology_classes._attributes.{module_name}"
        )
        for class_name in dir(module):
            class_ = getattr(module, class_name)

            if isclass(class_) and issubclass(class_, _Attribute) and class_ != _Attribute:
                ATTRIBUTE_CLASSES.append(class_)


ATTRIBUTE_CLASSES: list[type[_Attribute]] = []
_collect_attribute_classes()
