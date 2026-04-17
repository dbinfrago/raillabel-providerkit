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
class _SingleSelectAttribute(_Attribute):
    options: set[str]
    ATTRIBUTE_TYPE_IDENTIFIER = "single-select"
    PYTHON_TYPE = str

    @classmethod
    def supports(cls, attribute_dict: dict) -> bool:
        return (
            "attribute_type" in attribute_dict
            and type(attribute_dict["attribute_type"]) is dict
            and "type" in attribute_dict["attribute_type"]
            and attribute_dict["attribute_type"]["type"] == cls.ATTRIBUTE_TYPE_IDENTIFIER
        )

    @classmethod
    def fromdict(cls, attribute_dict: dict) -> _SingleSelectAttribute:
        if not cls.supports(attribute_dict):
            raise ValueError

        return _SingleSelectAttribute(
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
        # Convert numeric types (int/float) to string for comparison
        # This handles cases where data contains numeric values (e.g., 1.0, 2.0)
        # but the ontology defines string options (e.g., "1", "2")
        # Only convert if all options are numeric strings
        # Note: bool must be excluded because isinstance(True, int) is True in Python
        if (
            not isinstance(attribute_values, bool)
            and isinstance(attribute_values, int | float)
            and self._all_options_are_numeric()
        ):
            attribute_values = str(int(attribute_values))

        type_issues = super().check_type_and_value(attribute_name, attribute_values, identifiers)
        if len(type_issues) > 0:
            return type_issues

        if attribute_values not in self.options:
            suggested = (
                self._find_whitespace_match(attribute_values)
                if isinstance(attribute_values, str)
                else None
            )
            if suggested is not None:
                return [
                    Issue(
                        type=IssueType.ATTRIBUTE_VALUE,
                        reason=(
                            f"Attribute '{attribute_name}' has an undefined value"
                            f" '{attribute_values}' (defined options: {self._stringify_options()})."
                            f" [FIXABLE] Did you mean '{suggested}'?"
                        ),
                        identifiers=identifiers,
                        fixable=True,
                        suggested_value=suggested,
                    )
                ]
            return [
                Issue(
                    type=IssueType.ATTRIBUTE_VALUE,
                    reason=(
                        f"Attribute '{attribute_name}' has an undefined value"
                        f" '{attribute_values}' (defined options: {self._stringify_options()})."
                    ),
                    identifiers=identifiers,
                )
            ]

        return []

    def _all_options_are_numeric(self) -> bool:
        """Check if all options are numeric strings (e.g., '1', '2', '10')."""
        return all(self._is_numeric_string(option) for option in self.options)

    @staticmethod
    def _is_numeric_string(value: str) -> bool:
        """Check if a string value represents a valid integer."""
        try:
            int(value)
        except (ValueError, TypeError):
            return False
        else:
            return True

    def _find_whitespace_match(self, value: str) -> str | None:
        """Find an option that matches the value when whitespace is normalized.

        Returns the correct ontology option if a match is found, otherwise None.
        """
        normalized_value = "".join(value.split())
        for option in self.options:
            if "".join(option.split()) == normalized_value:
                return option
        return None

    def _stringify_options(self) -> str:
        options_str = ""

        for option in sorted(self.options):
            options_str += f"'{option}', "

        if options_str != "":
            options_str = options_str[:-2]

        return options_str
