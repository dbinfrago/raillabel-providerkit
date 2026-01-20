# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from raillabel.format import Camera, GpsImu, Lidar, Radar

SENSOR_METADATA = {
    # OSDAR23 sensors
    "rgb_center": Camera,
    "rgb_left": Camera,
    "rgb_right": Camera,
    "rgb_highres_center": Camera,
    "rgb_highres_left": Camera,
    "rgb_highres_right": Camera,
    "rgb_longrange_center": Camera,
    "rgb_longrange_left": Camera,
    "rgb_longrange_right": Camera,
    "ir_center": Camera,
    "ir_left": Camera,
    "ir_right": Camera,
    "lidar": Lidar,
    "radar": Radar,
    "gps_imu": GpsImu,
    # OSDAR26 sensors
    "rgb_12mp_left": Camera,
    "rgb_12mp_middle": Camera,
    "rgb_12mp_right": Camera,
    "rgb_5mp_left": Camera,
    "rgb_5mp_middle": Camera,
    "rgb_5mp_right": Camera,
    "ir_middle": Camera,
    "lidar_merged": Lidar,
    "radar_cartesian": Radar,
}
