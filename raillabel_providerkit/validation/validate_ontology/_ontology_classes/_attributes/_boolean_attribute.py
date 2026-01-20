# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _BooleanAttribute(_Attribute):
    ATTRIBUTE_TYPE_IDENTIFIER = "boolean"
    PYTHON_TYPE = bool
