# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType
from raillabel_providerkit.validation.validate_ontology._ontology_classes._scope import (
    _Scope,
)

from ._attribute_abc import _Attribute


@dataclass
class _MultiSelectAttribute(_Attribute):
    options: set[str]
    ATTRIBUTE_TYPE_IDENTIFIER = "multi-select"
    PYTHON_TYPE = list

    @classmethod
    def supports(cls, attribute_dict: dict) -> bool:
        return (
            "attribute_type" in attribute_dict
            and type(attribute_dict["attribute_type"]) is dict
            and "type" in attribute_dict["attribute_type"]
            and attribute_dict["attribute_type"]["type"] == cls.ATTRIBUTE_TYPE_IDENTIFIER
        )

    @classmethod
    def fromdict(cls, attribute_dict: dict) -> _MultiSelectAttribute:
        if not cls.supports(attribute_dict):
            raise ValueError

        return _MultiSelectAttribute(
            optional=attribute_dict.get("optional", False),
            scope=_Scope(attribute_dict.get("scope", "annotation")),
            sensor_types=attribute_dict.get("sensor_types", ["camera", "lidar", "radar"]),
            options=set(attribute_dict["attribute_type"]["options"]),
        )

    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_values: bool | float | str | list,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        # Accept single strings as a list with one element (for backwards compatibility
        # with annotation tools that output single-select format for multi-select attributes)
        if isinstance(attribute_values, str):
            attribute_values = [attribute_values]

        type_issues = super().check_type_and_value(attribute_name, attribute_values, identifiers)
        if len(type_issues) > 0:
            return type_issues

        for attribute_value in attribute_values:
            if attribute_value not in self.options:
                return [
                    Issue(
                        type=IssueType.ATTRIBUTE_VALUE,
                        reason=(
                            f"Attribute '{attribute_name}' has an undefined value"
                            f" '{attribute_value}' (defined options: {self._stringify_options()})."
                        ),
                        identifiers=identifiers,
                    )
                ]

        return []

    def check_scope_for_two_annotations(
        self,
        attribute_name: str,
        attribute_value_1: bool | float | str | list,
        attribute_value_2: bool | float | str | list,
        annotation_1_identifiers: IssueIdentifiers,
        annotation_2_identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        # Accept single strings as a list with one element (for backwards compatibility
        # with annotation tools that output single-select format for multi-select attributes)
        if isinstance(attribute_value_1, str):
            attribute_value_1 = [attribute_value_1]
        if isinstance(attribute_value_2, str):
            attribute_value_2 = [attribute_value_2]

        return super().check_scope_for_two_annotations(
            attribute_name,
            attribute_value_1,
            attribute_value_2,
            annotation_1_identifiers,
            annotation_2_identifiers,
        )

    def _stringify_options(self) -> str:
        options_str = ""

        for option in sorted(self.options):
            options_str += f"'{option}', "

        if options_str != "":
            options_str = options_str[:-2]

        return options_str
