# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import raillabel
from raillabel.format import (
    Bbox,
    Camera,
    Cuboid,
    GpsImu,
    Lidar,
    OtherSensor,
    Poly2d,
    Poly3d,
    Radar,
    Seg3d,
)

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_missing_ego_track(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether all middle cameras have ego track annotations.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all missing ego track errors in the scene. If an empty list is returned, then there
        are no errors present.
    """
    issues = []

    sensors_that_require_ego_track = _filter_out_sensors_that_do_not_require_ego_track(scene.sensors)
    for frame_id, frame in scene.frames.items():
        issues.extend(_validate_for_frame(frame_id, frame, sensors_that_require_ego_track))

    return issues


def _filter_out_sensors_that_do_not_require_ego_track(
    sensors: dict[str, Camera | Lidar | Radar | GpsImu | OtherSensor],
) -> list[str]:
    sensor_ids_that_require_ego_track = []
    for sensor_id, sensor in sensors.items():
        if not isinstance(sensor, Camera):
            continue
        if not ("_middle" in sensor_id or "_center" in sensor_id):
            continue
        sensor_ids_that_require_ego_track.append(sensor_id)

    return sensor_ids_that_require_ego_track


def _validate_for_frame(
    frame_id: int, frame: raillabel.format.Frame, sensors_that_require_ego_track: list[str]
) -> list[Issue]:
    issues = []
    for sensor_id in sensors_that_require_ego_track:
        issues.extend(_validate_for_sensor_frame(sensor_id, frame, frame_id))
    return issues


def _validate_for_sensor_frame(
    sensor_id: str, frame: raillabel.format.Frame, frame_id: int
) -> list[Issue]:
    ego_track_is_in_sensor_frame = False
    for annotation in frame.annotations.values():
        if annotation.sensor_id != sensor_id:
            continue

        if _annotation_is_ego_track_osdar23(annotation) or _annotation_is_ego_track_open_data(
            annotation
        ):
            ego_track_is_in_sensor_frame = True
            break

    if ego_track_is_in_sensor_frame:
        return []

    return [
        Issue(
            type=IssueType.MISSING_EGO_TRACK,
            identifiers=IssueIdentifiers(
                frame=frame_id,
                sensor=sensor_id,
            ),
        )
    ]


def _annotation_is_ego_track_osdar23(annotation: Bbox | Cuboid | Poly2d | Poly3d | Seg3d) -> bool:
    return "trackID" in annotation.attributes and annotation.attributes["trackID"] == 0


def _annotation_is_ego_track_open_data(annotation: Bbox | Cuboid | Poly2d | Poly3d | Seg3d) -> bool:
    return "isEgoTrack" in annotation.attributes and annotation.attributes["isEgoTrack"] is True
