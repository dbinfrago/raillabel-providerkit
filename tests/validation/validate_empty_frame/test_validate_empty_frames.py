# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from uuid import UUID

import raillabel
from raillabel.format import Camera, Lidar, Bbox, Poly3d, Point2d, Size2d, Point3d, IntrinsicsPinhole

from raillabel_providerkit.validation.validate_empty_frames.validate_empty_frames import (
    _get_sensors_requiring_annotations,
    _sensor_has_annotations_in_frame,
    validate_empty_frames,
)
from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


@pytest.fixture
def middle_camera():
    return Camera(
        intrinsics=IntrinsicsPinhole(
            camera_matrix=(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0),
            distortion=(0, 0, 0, 0, 0),
            width_px=1920,
            height_px=1080,
        ),
        extrinsics=None,
        uri=None,
        description=None,
    )


@pytest.fixture
def lidar_sensor():
    return Lidar(
        extrinsics=None,
        uri=None,
        description=None,
    )


@pytest.fixture
def sample_bbox():
    return Bbox(
        object_id=UUID("7df959d7-0ec2-4722-8b62-bb2e529de2ec"),
        sensor_id="rgb_center",
        pos=Point2d(0.0, 0.0),
        size=Size2d(10.0, 10.0),
        attributes={},
    )


@pytest.fixture
def sample_poly3d():
    return Poly3d(
        object_id=UUID("7df959d7-0ec2-4722-8b62-bb2e529de2ec"),
        sensor_id="lidar",
        points=[Point3d(0, 0, 0), Point3d(1, 1, 1)],
        closed=False,
        attributes={},
    )


def test_get_sensors_requiring_annotations__empty_sensors():
    assert _get_sensors_requiring_annotations({}) == []


def test_get_sensors_requiring_annotations__middle_camera(middle_camera):
    sensors = {"rgb_center": middle_camera}
    result = _get_sensors_requiring_annotations(sensors)
    assert "rgb_center" in result


def test_get_sensors_requiring_annotations__middle_camera_variants(middle_camera):
    sensors = {
        "rgb_middle": middle_camera,
        "cam_center": middle_camera,
    }
    result = _get_sensors_requiring_annotations(sensors)
    assert "rgb_middle" in result
    assert "cam_center" in result


def test_get_sensors_requiring_annotations__side_cameras_ignored(middle_camera):
    sensors = {
        "rgb_left": middle_camera,
        "rgb_right": middle_camera,
    }
    result = _get_sensors_requiring_annotations(sensors)
    assert result == []


def test_get_sensors_requiring_annotations__lidar_included(lidar_sensor):
    sensors = {"lidar": lidar_sensor}
    result = _get_sensors_requiring_annotations(sensors)
    assert "lidar" in result


def test_sensor_has_annotations_in_frame__no_annotations():
    frame = raillabel.format.Frame(timestamp=None, sensors={}, frame_data={}, annotations={})
    assert not _sensor_has_annotations_in_frame("rgb_center", frame)


def test_sensor_has_annotations_in_frame__has_annotations(sample_bbox):
    frame = raillabel.format.Frame(
        timestamp=None,
        sensors={},
        frame_data={},
        annotations={UUID("0fb4fc0b-3eeb-443a-8dd0-2caf9912d016"): sample_bbox},
    )
    assert _sensor_has_annotations_in_frame("rgb_center", frame)


def test_sensor_has_annotations_in_frame__annotations_for_other_sensor(sample_bbox):
    frame = raillabel.format.Frame(
        timestamp=None,
        sensors={},
        frame_data={},
        annotations={UUID("0fb4fc0b-3eeb-443a-8dd0-2caf9912d016"): sample_bbox},
    )
    assert not _sensor_has_annotations_in_frame("lidar", frame)


def test_validate_empty_frames__no_error(middle_camera, sample_bbox):
    scene = raillabel.Scene(
        metadata=raillabel.format.Metadata(schema_version="1.0.0"),
        sensors={"rgb_center": middle_camera},
        objects={
            UUID("7df959d7-0ec2-4722-8b62-bb2e529de2ec"): raillabel.format.Object(
                name="obj", type="person"
            )
        },
        frames={
            0: raillabel.format.Frame(
                timestamp=None,
                sensors={},
                frame_data={},
                annotations={UUID("0fb4fc0b-3eeb-443a-8dd0-2caf9912d016"): sample_bbox},
            ),
        },
    )

    assert len(validate_empty_frames(scene)) == 0


def test_validate_empty_frames__one_error(middle_camera):
    scene = raillabel.Scene(
        metadata=raillabel.format.Metadata(schema_version="1.0.0"),
        sensors={"rgb_center": middle_camera},
        objects={},
        frames={
            0: raillabel.format.Frame(timestamp=None, sensors={}, frame_data={}, annotations={}),
        },
    )

    result = validate_empty_frames(scene)
    assert len(result) == 1
    assert result[0].type == IssueType.EMPTY_FRAMES
    assert result[0].identifiers.frame == 0
    assert result[0].identifiers.sensor == "rgb_center"


def test_validate_empty_frames__two_errors(middle_camera, lidar_sensor):
    scene = raillabel.Scene(
        metadata=raillabel.format.Metadata(schema_version="1.0.0"),
        sensors={"rgb_center": middle_camera, "lidar": lidar_sensor},
        objects={},
        frames={
            0: raillabel.format.Frame(timestamp=None, sensors={}, frame_data={}, annotations={}),
        },
    )

    result = validate_empty_frames(scene)
    assert len(result) == 2


def test_validate_empty_frames__no_relevant_sensors():
    """Test that non-middle cameras don't trigger issues."""
    camera = Camera(
        intrinsics=IntrinsicsPinhole(
            camera_matrix=(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0),
            distortion=(0, 0, 0, 0, 0),
            width_px=1920,
            height_px=1080,
        ),
        extrinsics=None,
        uri=None,
        description=None,
    )
    scene = raillabel.Scene(
        metadata=raillabel.format.Metadata(schema_version="1.0.0"),
        sensors={"rgb_left": camera, "rgb_right": camera},
        objects={},
        frames={
            0: raillabel.format.Frame(timestamp=None, sensors={}, frame_data={}, annotations={}),
        },
    )

    assert len(validate_empty_frames(scene)) == 0


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
