# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from decimal import Decimal

import pytest
from raillabel.scene_builder import SceneBuilder
from raillabel.format import SensorReference

from raillabel_providerkit.validation import validate_uris, Issue, IssueIdentifiers, IssueType


def test_sensor_reference_uri_valid():
    scene = SceneBuilder.empty().add_sensor("rgb_center").add_frame(1).result
    scene.frames[1].sensors["rgb_center"] = SensorReference(
        timestamp=Decimal(0), uri="/rgb_center/0.png"
    )

    actual = validate_uris(scene)
    assert actual == []


def test_uri_does_not_contain_sensor_name():
    scene = SceneBuilder.empty().add_sensor("rgb_center").add_frame(1).result
    scene.frames[1].sensors["rgb_center"] = SensorReference(
        timestamp=Decimal(0), uri="/INVALID/0.png"
    )

    actual = validate_uris(scene)
    assert actual == [
        Issue(
            type=IssueType.URI_FORMAT,
            identifiers=IssueIdentifiers(frame=1, sensor="rgb_center"),
            reason="'/INVALID/0.png' does not comply with the schema '/SENSOR_NAME/FILE_NAME.FILE_TYPE'",
        )
    ]


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-vv"])
