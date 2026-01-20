# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import re

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

# Sensor naming patterns for automatic calibration detection
# OSDAR23 uses: rgb_center, rgb_left, rgb_right, ir_center, ir_left, ir_right
# OSDAR26 uses: rgb_12mp_left, rgb_5mp_middle, ir_middle, etc.
_OSDAR26_SENSOR_PATTERN = re.compile(r"^(rgb|ir)_\d+mp_(left|middle|right)$|^ir_middle$")


def _uses_osdar26_calibration(sensor_id: str) -> bool:
    """Detect if the sensor uses OSDAR26 calibration conventions.

    OSDAR26 sensors have different extrinsics rotation axis conventions
    compared to OSDAR23. This function detects the calibration type based on
    sensor naming patterns.

    Parameters
    ----------
    sensor_id : str
        The sensor identifier to check.

    Returns
    -------
    bool
        True if the sensor uses OSDAR26 calibration conventions.
    """
    return bool(_OSDAR26_SENSOR_PATTERN.match(sensor_id))


def validate_horizon(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether all track/transition annotations are below the horizon.

    The horizon validation automatically detects the calibration format based on
    sensor naming conventions and applies the appropriate coordinate transformation.

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

            sensor_id = annotation.sensor_id
            uses_osdar26 = _uses_osdar26_calibration(sensor_id)

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
                    uses_osdar26,
                )
            )

    return issues


def _validate_annotation_for_horizon(
    annotation: Poly2d,
    camera: Camera,
    identifiers: IssueIdentifiers,
    use_osdar26_calibration: bool,
) -> list[Issue]:
    horizon_calculator = _HorizonCalculator(
        camera, alternative_calibration_workaround=use_osdar26_calibration
    )

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
