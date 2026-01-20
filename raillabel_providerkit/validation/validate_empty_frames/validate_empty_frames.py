# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import raillabel
from raillabel.format import Camera, Lidar

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_empty_frames(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether sensors requiring annotations have at least one annotation per frame.

    Only validates middle/center cameras and lidar sensors. This matches the behavior
    of the legacy annotation-checks tool.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all empty sensor frame errors in the scene. If an empty list is returned, then
        there are no errors present.
    """
    errors = []

    # Get sensor IDs that require annotations (middle cameras + lidar)
    sensors_requiring_annotations = _get_sensors_requiring_annotations(scene.sensors)

    for frame_uid, frame in scene.frames.items():
        # Check each sensor that requires annotations
        errors.extend(
            Issue(
                type=IssueType.EMPTY_FRAMES,
                identifiers=IssueIdentifiers(frame=frame_uid, sensor=sensor_id),
                reason="There are no annotations in this sensor frame.",
            )
            for sensor_id in sensors_requiring_annotations
            if not _sensor_has_annotations_in_frame(sensor_id, frame)
        )

    return errors


def _get_sensors_requiring_annotations(
    sensors: dict[str, Camera | Lidar | object],
) -> list[str]:
    """Get sensor IDs that require annotations (middle/center cameras and lidar)."""
    sensor_ids = []
    for sensor_id, sensor in sensors.items():
        # Include middle/center cameras
        if isinstance(sensor, Camera):
            if "_middle" in sensor_id or "_center" in sensor_id:
                sensor_ids.append(sensor_id)
        # Include lidar sensors
        elif isinstance(sensor, Lidar):
            sensor_ids.append(sensor_id)
    return sensor_ids


def _sensor_has_annotations_in_frame(sensor_id: str, frame: raillabel.format.Frame) -> bool:
    """Check if a sensor has any annotations in the given frame."""
    return any(annotation.sensor_id == sensor_id for annotation in frame.annotations.values())
