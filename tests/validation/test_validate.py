# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from decimal import Decimal
from pathlib import Path
import json
import pytest

from raillabel.scene_builder import SceneBuilder
from raillabel.format import Point2d, SensorReference, Scene, Size3d

from raillabel_providerkit import validate


def write_to_json(content: dict, path: Path):
    with path.open("w") as f:
        json.dump(content, f)


def scene_to_dict(scene: Scene) -> dict:
    return json.loads(scene.to_json().model_dump_json())


def test_no_issues_in_empty_scene_dict():
    scene_dict = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}
    assert len(validate(scene_dict)) == 0


def test_no_issues_in_empty_scene_path(tmp_path):
    scene_dict = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}
    scene_path = tmp_path / "empty_scene.json"
    write_to_json(scene_dict, scene_path)

    assert len(validate(scene_path)) == 0


def test_validate_schema_included():
    scene_dict = {"openlabel": {}}
    assert len(validate(scene_dict)) == 1


def test_validate_empty_frames_included():
    scene = SceneBuilder.empty().add_frame().result
    scene_dict = scene_to_dict(scene)

    assert len(validate(scene_dict, validate_for_empty_frames=False)) == 0
    assert len(validate(scene_dict, validate_for_empty_frames=True)) == 1


def test_validate_rail_side_included():
    scene = (
        SceneBuilder.empty()
        .add_poly2d(
            points=[
                Point2d(0, 0),
                Point2d(0, 1),
            ],
            attributes={"railSide": "rightRail", "trackID": 0},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .add_poly2d(
            points=[
                Point2d(1, 0),
                Point2d(1, 1),
            ],
            attributes={"railSide": "leftRail", "trackID": 0},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )
    scene_dict = scene_to_dict(scene)

    assert (
        len(validate(scene_dict, validate_for_rail_side_order=False, validate_for_horizon=False))
        == 0
    )
    assert (
        len(validate(scene_dict, validate_for_rail_side_order=True, validate_for_horizon=False)) == 1
    )


def test_validate_missing_ego_track_included():
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_frame()
        .add_bbox(sensor_id="rgb_center")
        .result
    )
    scene_dict = scene_to_dict(scene)

    assert len(validate(scene_dict, validate_for_missing_ego_track=False)) == 0
    assert len(validate(scene_dict, validate_for_missing_ego_track=True)) == 1


def test_validate_sensors_included():
    scene = SceneBuilder.empty().add_sensor("rgb_unknown").result
    scene_dict = scene_to_dict(scene)

    assert len(validate(scene_dict, validate_for_sensors=False)) == 0
    assert len(validate(scene_dict, validate_for_sensors=True)) == 1

    actual = validate(scene_dict)
    assert len(actual) == 1


def test_validate_uris_included():
    scene = SceneBuilder.empty().add_sensor("lidar").add_frame(1).add_poly3d().result
    scene.frames[1].sensors["lidar"] = SensorReference(timestamp=Decimal(0), uri="/INVALID/0.pcd")
    scene_dict = scene_to_dict(scene)

    assert len(validate(scene_dict, validate_for_uris=False)) == 0
    assert len(validate(scene_dict, validate_for_uris=True)) == 1


def test_validate_dimensions_included():
    scene = scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="person_0001", size=Size3d(x=0.5, y=0.5, z=0.01))
        .result
    )
    scene_dict = scene_to_dict(scene)

    assert len(validate(scene_dict, validate_for_dimensions=False)) == 0
    assert len(validate(scene_dict, validate_for_dimensions=True)) == 1


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
