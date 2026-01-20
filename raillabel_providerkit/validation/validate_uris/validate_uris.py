# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from raillabel import Scene

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_uris(scene: Scene) -> list[Issue]:
    """Validate whether all uri fields in a scene comply with the schema.

    Parameters
    ----------
    scene : Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all uri format errors in the scene. If an empty list is returned, then there
        are no errors present.
    """
    issues = []
    for frame_id, frame in scene.frames.items():
        for sensor_id, sensor_reference in frame.sensors.items():
            if _reference_uri_is_valid(sensor_id, sensor_reference.uri):
                continue
            issues.append(
                Issue(
                    type=IssueType.URI_FORMAT,
                    identifiers=IssueIdentifiers(frame=frame_id, sensor=sensor_id),
                    reason=(
                        f"'{sensor_reference.uri}' does not comply with the schema "
                        "'/SENSOR_NAME/FILE_NAME.FILE_TYPE'"
                    ),
                )
            )

    return issues


def _reference_uri_is_valid(sensor_id: str, uri: str) -> bool:
    return uri.startswith(f"/{sensor_id}/")
