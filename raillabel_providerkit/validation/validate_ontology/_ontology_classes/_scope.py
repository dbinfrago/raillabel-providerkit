# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from enum import Enum


class _Scope(Enum):
    ANNOTATION = "annotation"
    FRAME = "frame"
    OBJECT = "object"
