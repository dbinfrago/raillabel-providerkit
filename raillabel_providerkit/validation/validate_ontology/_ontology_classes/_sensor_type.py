# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from enum import Enum


class _SensorType(Enum):
    CAMERA = "camera"
    LIDAR = "lidar"
    RADAR = "radar"
