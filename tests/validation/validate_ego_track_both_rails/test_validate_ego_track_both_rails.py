# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Tests for validate_ego_track_both_rails."""

import pytest
from raillabel.format import Point2d
from raillabel.scene_builder import SceneBuilder

from raillabel_providerkit.validation import IssueType
from raillabel_providerkit.validation.validate_ego_track_both_rails import (
    validate_ego_track_both_rails,
)


def add_ego_track_left_rail(
    builder: SceneBuilder,
    points: list[tuple[float, float]],
    object_name: str = "track_ego",
    sensor_id: str = "rgb_middle",
    frame_id: int = 1,
) -> SceneBuilder:
    """Add a left rail of the ego track."""
    return builder.add_poly2d(
        frame_id=frame_id,
        points=[Point2d(x=x, y=y) for x, y in points],
        attributes={"railSide": "leftRail", "isEgoTrack": True},
        object_name=object_name,
        sensor_id=sensor_id,
    )


def add_ego_track_right_rail(
    builder: SceneBuilder,
    points: list[tuple[float, float]],
    object_name: str = "track_ego",
    sensor_id: str = "rgb_middle",
    frame_id: int = 1,
) -> SceneBuilder:
    """Add a right rail of the ego track."""
    return builder.add_poly2d(
        frame_id=frame_id,
        points=[Point2d(x=x, y=y) for x, y in points],
        attributes={"railSide": "rightRail", "isEgoTrack": True},
        object_name=object_name,
        sensor_id=sensor_id,
    )


def add_non_ego_track_rail(
    builder: SceneBuilder,
    points: list[tuple[float, float]],
    rail_side: str,
    object_name: str = "track_other",
    sensor_id: str = "rgb_middle",
    frame_id: int = 1,
) -> SceneBuilder:
    """Add a non-ego track rail."""
    return builder.add_poly2d(
        frame_id=frame_id,
        points=[Point2d(x=x, y=y) for x, y in points],
        attributes={"railSide": rail_side, "isEgoTrack": False},
        object_name=object_name,
        sensor_id=sensor_id,
    )


def test_validate_ego_track_both_rails__no_center_cameras():
    """No issues when there are no center cameras."""
    scene = SceneBuilder.empty().add_sensor("lidar").add_frame(1).result
    issues = validate_ego_track_both_rails(scene)
    assert issues == []


def test_validate_ego_track_both_rails__no_ego_track_annotations():
    """No issues when no ego track annotations exist (handled by validate_missing_ego_track)."""
    scene = SceneBuilder.empty().add_sensor("rgb_middle").add_frame(1).result
    issues = validate_ego_track_both_rails(scene)
    assert issues == []


def test_validate_ego_track_both_rails__valid_overlapping_rails():
    """No issues when both rails exist with overlapping y-ranges."""
    builder = SceneBuilder.empty().add_sensor("rgb_middle").add_frame(1)
    builder = add_ego_track_left_rail(builder, [(100, 200), (100, 400), (100, 600)])
    builder = add_ego_track_right_rail(builder, [(200, 200), (200, 400), (200, 600)])
    scene = builder.result

    issues = validate_ego_track_both_rails(scene)
    assert issues == []


def test_validate_ego_track_both_rails__non_overlapping_y_ranges():
    """Issue when left and right rails don't have overlapping y-ranges."""
    builder = SceneBuilder.empty().add_sensor("rgb_middle").add_frame(1)
    # Left rail: y 100-200, Right rail: y 300-400 (no overlap)
    builder = add_ego_track_left_rail(builder, [(100, 100), (100, 200)])
    builder = add_ego_track_right_rail(builder, [(200, 300), (200, 400)])
    scene = builder.result

    issues = validate_ego_track_both_rails(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.EGO_TRACK_BOTH_RAILS
    assert "overlapping y ranges" in issues[0].reason


def test_validate_ego_track_both_rails__multiple_rails_at_common_y():
    """Issue when there are multiple left rails at the common y."""
    builder = SceneBuilder.empty().add_sensor("rgb_middle").add_frame(1)
    # Two left rails at the same y range
    builder = add_ego_track_left_rail(builder, [(100, 200), (100, 600)], object_name="track_ego1")
    builder = add_ego_track_left_rail(builder, [(150, 200), (150, 600)], object_name="track_ego2")
    builder = add_ego_track_right_rail(builder, [(200, 200), (200, 600)], object_name="track_ego1")
    scene = builder.result

    issues = validate_ego_track_both_rails(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.EGO_TRACK_BOTH_RAILS
    assert "not exactly 2 ego track rails" in issues[0].reason


def test_validate_ego_track_both_rails__one_side_missing_no_issue():
    """No issue when only one side exists (disabled as in original - too many false positives)."""
    builder = SceneBuilder.empty().add_sensor("rgb_middle").add_frame(1)
    # Only left rail, no right rail
    builder = add_ego_track_left_rail(builder, [(100, 200), (100, 600)])
    scene = builder.result

    issues = validate_ego_track_both_rails(scene)
    # This should NOT raise an issue (same behavior as original - disabled)
    assert issues == []


def test_validate_ego_track_both_rails__non_ego_track_ignored():
    """Non-ego-track annotations should be ignored."""
    builder = SceneBuilder.empty().add_sensor("rgb_middle").add_frame(1)
    # Non-ego-track rails with non-overlapping y ranges - should not cause issues
    builder = add_non_ego_track_rail(builder, [(100, 100), (100, 200)], "leftRail")
    builder = add_non_ego_track_rail(builder, [(200, 300), (200, 400)], "rightRail")
    scene = builder.result

    issues = validate_ego_track_both_rails(scene)
    # Non-ego tracks should not cause issues
    assert issues == []
