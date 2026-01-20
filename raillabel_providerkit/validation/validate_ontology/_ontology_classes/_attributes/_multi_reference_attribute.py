# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from uuid import UUID

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

from ._attribute_abc import _Attribute


@dataclass
class _MultiReferenceAttribute(_Attribute):
    ATTRIBUTE_TYPE_IDENTIFIER = "multi-reference"
    PYTHON_TYPE = list

    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_values: bool | float | str | list,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        type_issues = super().check_type_and_value(attribute_name, attribute_values, identifiers)
        if len(type_issues) > 0:
            return type_issues

        attribute_value: t.Any
        try:
            for attribute_value in attribute_values:
                UUID(attribute_value)
        except (ValueError, AttributeError):
            return [
                Issue(
                    type=IssueType.ATTRIBUTE_VALUE,
                    identifiers=identifiers,
                    reason=(
                        f"Attribute '{attribute_name}' has a non-UUID value '{attribute_value}'."
                    ),
                )
            ]

        return []
