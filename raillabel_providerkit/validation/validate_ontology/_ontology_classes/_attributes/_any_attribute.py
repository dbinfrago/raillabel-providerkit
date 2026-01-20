# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass

from raillabel_providerkit.validation import Issue, IssueIdentifiers

from ._attribute_abc import _Attribute


@dataclass
class _AnyAttribute(_Attribute):
    ATTRIBUTE_TYPE_IDENTIFIER = "any"
    PYTHON_TYPE = None

    def check_type_and_value(
        self,
        attribute_name: str,  # noqa: ARG002
        attribute_value: bool | float | str | list,  # noqa: ARG002
        identifiers: IssueIdentifiers,  # noqa: ARG002
    ) -> list[Issue]:
        return []
