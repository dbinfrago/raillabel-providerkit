# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel.scene_builder import SceneBuilder
from raillabel.format import Lidar

from raillabel_providerkit.validation import IssueIdentifiers, IssueType, validate_sensors
from raillabel_providerkit.validation.validate_sensors.validate_sensors import SENSOR_METADATA


def test_all_sensors_valid():
    scene_builder = SceneBuilder.empty()
    for sensor_id, sensor_type in SENSOR_METADATA.items():
        scene_builder.add_sensor(sensor_id)

    scene = scene_builder.result

    actual = validate_sensors(scene)
    assert actual == []


def test_sensor_id_unknown():
    scene = SceneBuilder.empty().add_sensor("rgb_unknown").result

    actual = validate_sensors(scene)
    assert len(actual) == 1
    assert actual[0].type == IssueType.SENSOR_ID_UNKNOWN
    assert actual[0].identifiers == IssueIdentifiers(sensor="rgb_unknown")


def test_wrong_sensor_type():
    scene = SceneBuilder.empty().result
    scene.sensors["rgb_center"] = Lidar()

    actual = validate_sensors(scene)
    assert len(actual) == 1
    assert actual[0].type == IssueType.SENSOR_TYPE_WRONG
    assert actual[0].identifiers == IssueIdentifiers(sensor="rgb_center")
    assert actual[0].reason is not None
    assert "lidar" in actual[0].reason.lower()
    assert "camera" in actual[0].reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
