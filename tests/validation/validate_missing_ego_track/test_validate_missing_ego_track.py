# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel.scene_builder import SceneBuilder

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType
from raillabel_providerkit.validation import validate_missing_ego_track


def test_no_center_sensors():
    scene = SceneBuilder.empty().add_sensor("rgb_left").add_frame().result

    actual = validate_missing_ego_track(scene)
    assert actual == []


def test_no_frames():
    scene = SceneBuilder.empty().add_sensor("rgb_center").result

    actual = validate_missing_ego_track(scene)
    assert actual == []


def test_osdar_schema__not_missing():
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="track")
        .add_poly2d(object_name="track_0000", sensor_id="rgb_center", attributes={"trackID": 0})
        .result
    )

    actual = validate_missing_ego_track(scene)
    assert actual == []


def test_osdar_schema__missing():
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="track")
        .add_poly2d(
            frame_id=1, object_name="track_0000", sensor_id="rgb_center", attributes={"trackID": 1}
        )
        .result
    )

    actual = validate_missing_ego_track(scene)
    assert actual == [
        Issue(
            type=IssueType.MISSING_EGO_TRACK,
            identifiers=IssueIdentifiers(frame=1, sensor="rgb_center"),
        )
    ]


def test_open_dataset_schema__not_missing():
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="track")
        .add_poly2d(
            object_name="track_0000", sensor_id="rgb_center", attributes={"isEgoTrack": True}
        )
        .result
    )

    actual = validate_missing_ego_track(scene)
    assert actual == []


def test_open_dataset_schema__missing():
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="track")
        .add_poly2d(
            object_name="track_0000", sensor_id="rgb_center", attributes={"isEgoTrack": False}
        )
        .result
    )

    actual = validate_missing_ego_track(scene)
    assert actual == [
        Issue(
            type=IssueType.MISSING_EGO_TRACK,
            identifiers=IssueIdentifiers(frame=1, sensor="rgb_center"),
        )
    ]


def test_missing_in_two_sensors():
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_sensor("ir_center")
        .add_object(object_type="track")
        .add_frame(frame_id=1)
        .result
    )

    actual = validate_missing_ego_track(scene)
    assert actual == [
        Issue(
            type=IssueType.MISSING_EGO_TRACK,
            identifiers=IssueIdentifiers(frame=1, sensor="rgb_center"),
        ),
        Issue(
            type=IssueType.MISSING_EGO_TRACK,
            identifiers=IssueIdentifiers(frame=1, sensor="ir_center"),
        ),
    ]


def test_missing_in_two_frames():
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="track")
        .add_frame(frame_id=1)
        .add_frame(frame_id=2)
        .result
    )

    actual = validate_missing_ego_track(scene)
    assert actual == [
        Issue(
            type=IssueType.MISSING_EGO_TRACK,
            identifiers=IssueIdentifiers(frame=1, sensor="rgb_center"),
        ),
        Issue(
            type=IssueType.MISSING_EGO_TRACK,
            identifiers=IssueIdentifiers(frame=2, sensor="rgb_center"),
        ),
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
