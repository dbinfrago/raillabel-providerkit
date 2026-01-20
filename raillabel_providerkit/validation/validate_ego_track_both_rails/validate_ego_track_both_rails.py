# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Validate that both rails (left and right) of the ego track exist in center cameras."""

from __future__ import annotations

import raillabel
from raillabel.format import Camera, Poly2d

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_ego_track_both_rails(scene: raillabel.Scene) -> list[Issue]:
    """Validate that ego track has both left and right rails in center cameras.

    This validator checks:
    1. That the y-ranges of left and right ego track rails overlap
    2. That exactly one left and one right rail exist at the common y position

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all ego track rail issues. If an empty list is returned, then there are no
        errors present.

    """
    issues: list[Issue] = []

    center_cameras = _get_center_camera_uids(scene.sensors)
    if not center_cameras:
        return issues

    for frame_uid, frame in scene.frames.items():
        for camera_uid in center_cameras:
            camera_issues = _validate_frame_for_camera(frame_uid, frame, camera_uid, scene)
            issues.extend(camera_issues)

    return issues


def _get_center_camera_uids(sensors: dict) -> list[str]:
    """Return UIDs of center/middle cameras."""
    center_cameras = []
    for sensor_uid, sensor in sensors.items():
        if isinstance(sensor, Camera) and ("center" in sensor_uid or "middle" in sensor_uid):
            center_cameras.append(sensor_uid)
    return center_cameras


def _validate_frame_for_camera(
    frame_uid: int,
    frame: raillabel.format.Frame,
    camera_uid: str,
    scene: raillabel.Scene,
) -> list[Issue]:
    """Validate ego track rails for a specific camera in a frame."""
    left_rails, right_rails = _collect_ego_track_rails(frame, camera_uid, scene)
    return _check_rail_issues(frame_uid, camera_uid, left_rails, right_rails)


def _collect_ego_track_rails(
    frame: raillabel.format.Frame,
    camera_uid: str,
    scene: raillabel.Scene,
) -> tuple[list[Poly2d], list[Poly2d]]:
    """Collect left and right ego track rails for a camera."""
    left_rails: list[Poly2d] = []
    right_rails: list[Poly2d] = []

    for annotation in frame.annotations.values():
        if annotation.sensor_id != camera_uid:
            continue
        if not isinstance(annotation, Poly2d):
            continue
        if not _annotation_is_ego_track(annotation, scene):
            continue

        rail_side = annotation.attributes.get("railSide")
        if rail_side == "leftRail":
            left_rails.append(annotation)
        elif rail_side == "rightRail":
            right_rails.append(annotation)

    return left_rails, right_rails


def _check_rail_issues(
    frame_uid: int,
    camera_uid: str,
    left_rails: list[Poly2d],
    right_rails: list[Poly2d],
) -> list[Issue]:
    """Check for rail issues and return issues list."""
    # If no ego track at all, this is handled by validate_missing_ego_track
    if not left_rails and not right_rails:
        return []

    # If one side is missing entirely, skip (disabled in original - too many false positives)
    if not left_rails or not right_rails:
        return []

    left_y_range = _get_y_range(left_rails)
    right_y_range = _get_y_range(right_rails)

    if left_y_range is None or right_y_range is None:
        return []

    issues: list[Issue] = []
    left_min, left_max = left_y_range
    right_min, right_max = right_y_range

    # Check if ranges don't overlap
    if left_min > right_max or right_min > left_max:
        issues.append(
            Issue(
                type=IssueType.EGO_TRACK_BOTH_RAILS,
                reason=(
                    f"Ego track rails for sensor {camera_uid} don't have overlapping y ranges. "
                    f"Left: ({left_min:.1f} to {left_max:.1f}), "
                    f"right: ({right_min:.1f} to {right_max:.1f})."
                ),
                identifiers=IssueIdentifiers(
                    frame=frame_uid,
                    sensor=camera_uid,
                ),
            )
        )
        return issues

    # Find the common y (the lower of the maximum y values)
    common_y = min(left_max, right_max)

    # Count rails at common_y
    left_count_at_y = sum(1 for rail in left_rails if _y_in_poly2d(common_y, rail))
    right_count_at_y = sum(1 for rail in right_rails if _y_in_poly2d(common_y, rail))

    if left_count_at_y != 1 or right_count_at_y != 1:
        issues.append(
            Issue(
                type=IssueType.EGO_TRACK_BOTH_RAILS,
                reason=(
                    f"For sensor {camera_uid}, not exactly 2 ego track rails at y={common_y:.1f}. "
                    f"Found {left_count_at_y} left rail(s) and {right_count_at_y} right rail(s)."
                ),
                identifiers=IssueIdentifiers(
                    frame=frame_uid,
                    sensor=camera_uid,
                    attribute="railSide",
                ),
            )
        )

    return issues


def _annotation_is_ego_track(annotation: Poly2d, scene: raillabel.Scene) -> bool:
    """Check if the annotation belongs to an ego track object."""
    object_data = scene.objects.get(annotation.object_id)
    if object_data is None:
        return False

    # Check isEgoTrack attribute on the annotation (newer format)
    if "isEgoTrack" in annotation.attributes:
        return bool(annotation.attributes["isEgoTrack"])

    # Check trackID attribute for legacy ego track identifiers
    track_id_keys = {"trackID", "trackId", "TrackID", "onTrack"}
    track_id_ego_values = {0, "0", "ego_track"}

    for key in track_id_keys:
        if key in annotation.attributes:
            track_id = annotation.attributes[key]
            if track_id in track_id_ego_values:
                return True

    return False


def _get_y_range(rails: list[Poly2d]) -> tuple[float, float] | None:
    """Get the min and max y values across all rails."""
    if not rails:
        return None

    all_y_values = [point.y for rail in rails for point in rail.points]

    if not all_y_values:
        return None

    return min(all_y_values), max(all_y_values)


def _y_in_poly2d(y: float, poly2d: Poly2d) -> bool:
    """Check if a y value falls within the y-range of a poly2d."""
    y_values = [point.y for point in poly2d.points]
    if not y_values:
        return False
    return min(y_values) <= y <= max(y_values)
