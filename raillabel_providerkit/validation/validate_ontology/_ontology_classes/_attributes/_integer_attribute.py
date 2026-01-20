# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _IntegerAttribute(_Attribute):
    ATTRIBUTE_TYPE_IDENTIFIER = "integer"
    PYTHON_TYPE = int
