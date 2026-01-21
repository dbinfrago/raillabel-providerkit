# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Validate that track/transition annotations are below the horizon line."""

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


def validate_horizon(
    scene: raillabel.Scene,
    horizon_tolerance_percent: float = 10.0,
) -> list[Issue]:
    """Validate whether all track/transition annotations are below the horizon.

    This validation only applies to **track** and **transition** object types.
    Other object types are not checked against the horizon line.

    The horizon is calculated based on each camera's pitch angle (tilt), derived
    from the extrinsics rotation matrix. This approach is robust across different
    calibration conventions (OSDAR23, OSDAR26, etc.).

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.
    horizon_tolerance_percent : float, optional
        Tolerance buffer as percentage of the horizon position from the top of the image.
        Higher values move the horizon line up (smaller Y), making the validation more
        permissive. For example, 10.0 means the horizon is moved up by 10% of its
        distance from the top. Default is 10.0.

    Returns
    -------
    list[Issue]
        List of all horizon crossing errors in the scene (only for track/transition
        annotations). If an empty list is returned, then there are no errors present.
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

            sensor_id = annotation.sensor_id

            identifiers = IssueIdentifiers(
                annotation=annotation_uid,
                frame=frame_uid,
                object=annotation.object_id,
                object_type=filtered_scene.objects[annotation.object_id].type,
                sensor=sensor_id,
            )

            issues.extend(
                _validate_annotation_for_horizon(
                    annotation,
                    filtered_scene.sensors[sensor_id],
                    identifiers,
                    horizon_tolerance_percent,
                )
            )

    return issues


def _validate_annotation_for_horizon(
    annotation: Poly2d,
    camera: Camera,
    identifiers: IssueIdentifiers,
    horizon_tolerance_percent: float = 10.0,
) -> list[Issue]:
    """Check if any point of the annotation is above the horizon line.

    Parameters
    ----------
    annotation : Poly2d
        The polygon annotation to check.
    camera : Camera
        The camera sensor with calibration data.
    identifiers : IssueIdentifiers
        Identifiers for error reporting.
    horizon_tolerance_percent : float
        Tolerance buffer as percentage. Moves horizon up to reduce false positives.

    Returns
    -------
    list[Issue]
        List containing one Issue if a point is above horizon, empty otherwise.
    """
    horizon_calculator = _HorizonCalculator(camera)

    # Calculate the horizon line (returns a function that gives Y for any X)
    horizon_line_function = horizon_calculator.calculate_horizon()

    for point in annotation.points:
        horizon_y = horizon_line_function(point.x)

        # Apply tolerance buffer: move horizon line up by the tolerance percentage
        # The horizon_y is measured from the top of the image (Y=0 is top)
        # Moving it "up" means making it smaller
        # tolerance_percent% of horizon_y is subtracted
        horizon_y_with_buffer = horizon_y * (1.0 - horizon_tolerance_percent / 100.0)

        if point.y < horizon_y_with_buffer:
            return [
                Issue(
                    IssueType.HORIZON_CROSSED,
                    identifiers,
                    f"The point ({point.x:.1f}, {point.y:.1f}) is above the horizon line "
                    f"(horizon at Y={horizon_y:.1f}, with {horizon_tolerance_percent}% "
                    f"tolerance: Y={horizon_y_with_buffer:.1f}).",
                )
            ]

    return []
