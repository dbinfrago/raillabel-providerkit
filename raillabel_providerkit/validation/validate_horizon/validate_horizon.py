# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import raillabel
from raillabel.filter import (
    IncludeAnnotationTypeFilter,
    IncludeObjectTypeFilter,
    IncludeSensorTypeFilter,
)
from raillabel.format import (
    Camera,
    Poly2d,
)

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

from ._horizon_calculator import _HorizonCalculator


def validate_horizon(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether all track/transition annotations are below the horizon.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all horizon crossing errors in the scene. If an empty list is returned, then there
        are no errors present.
    """
    issues = []

    filtered_scene = scene.filter(
        [
            IncludeObjectTypeFilter(["track", "transition"]),
            IncludeSensorTypeFilter(["camera"]),
            IncludeAnnotationTypeFilter(["poly2d"]),
        ]
    )

    for frame_uid, frame in filtered_scene.frames.items():
        for annotation_uid, annotation in frame.annotations.items():
            if not isinstance(annotation, Poly2d):
                raise AssertionError  # noqa: TRY004

            identifiers = IssueIdentifiers(
                annotation=annotation_uid,
                frame=frame_uid,
                object=annotation.object_id,
                object_type=filtered_scene.objects[annotation.object_id].type,
                sensor=annotation.sensor_id,
            )

            issues.extend(
                _validate_annotation_for_horizon(
                    annotation, filtered_scene.sensors[annotation.sensor_id], identifiers
                )
            )

    return issues


def _validate_annotation_for_horizon(
    annotation: Poly2d, camera: Camera, identifiers: IssueIdentifiers
) -> list[Issue]:
    horizon_calculator = _HorizonCalculator(camera)

    # Calculate the horizon from two points 10000m in front and then 1000m to each side
    # with an assumed inclination of 1m per 100m distance (0.01 = 1%)
    horizon_line_function = horizon_calculator.calculate_horizon(10000.0, 1000.0, 0.01)

    for point in annotation.points:
        horizon_y = horizon_line_function(point.x)
        if point.y < horizon_y:
            return [
                Issue(
                    IssueType.HORIZON_CROSSED,
                    identifiers,
                    f"The point {point} is above the expected"
                    f" horizon line ({point.y} < {horizon_y}).",
                )
            ]

    return []
