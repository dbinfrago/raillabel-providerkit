# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import raillabel

from raillabel_providerkit._util import SENSOR_METADATA
from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_sensors(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether whether all sensors have supported names and have the correct type.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all sensor name errors in the scene. If an empty list is returned, then there
        are no errors present.
    """
    issues = _validate_sensor_ids(scene)
    issues.extend(_validate_sensor_types(scene))
    return issues


def _validate_sensor_ids(scene: raillabel.Scene) -> list[Issue]:
    issues = []

    for sensor_id in scene.sensors:
        if sensor_id in SENSOR_METADATA:
            continue
        issues.append(
            Issue(
                type=IssueType.SENSOR_ID_UNKNOWN,
                identifiers=IssueIdentifiers(sensor=sensor_id),
                reason=f"Supported sensor ids: {list(SENSOR_METADATA.keys())}",
            )
        )

    return issues


def _validate_sensor_types(scene: raillabel.Scene) -> list[Issue]:
    issues = []

    for sensor_id, sensor in scene.sensors.items():
        if sensor_id not in SENSOR_METADATA:
            continue

        expected_type = SENSOR_METADATA[sensor_id]
        if isinstance(sensor, expected_type):
            continue

        issues.append(
            Issue(
                type=IssueType.SENSOR_TYPE_WRONG,
                identifiers=IssueIdentifiers(sensor=sensor_id),
                reason=(
                    f"The sensor is of type {sensor.__class__.__name__} "
                    f"(should be {expected_type.__name__})"
                ),
            )
        )

    return issues
