# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from uuid import UUID

import numpy as np
import raillabel
from raillabel.filter import (
    IncludeAnnotationTypeFilter,
    IncludeObjectTypeFilter,
    IncludeSensorIdFilter,
    IncludeSensorTypeFilter,
)

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_rail_side(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether all tracks have <= one left and right rail, and that they have correct order.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene, that should be validated.

    Returns
    -------
    list[Issue]
        List of all rail side errors in the scene. If an empty list is returned, then there are no
        errors present.

    """
    errors = []

    camera_uids = list(scene.filter([IncludeSensorTypeFilter(["camera"])]).sensors.keys())

    for camera_uid in camera_uids:
        filtered_scene = scene.filter(
            [
                IncludeObjectTypeFilter(["track", "transition"]),
                IncludeSensorIdFilter([camera_uid]),
                IncludeAnnotationTypeFilter(["poly2d"]),
            ]
        )

        for frame_uid, frame in filtered_scene.frames.items():
            counts_per_track = _count_rails_per_track_in_frame(frame)

            for object_uid, (left_count, right_count) in counts_per_track.items():
                context = IssueIdentifiers(
                    frame=frame_uid,
                    sensor=camera_uid,
                    object=object_uid,
                )

                count_errors = _check_rail_counts(context, left_count, right_count)
                exactly_one_left_and_right_rail_exist = count_errors != []
                if exactly_one_left_and_right_rail_exist:
                    errors.extend(count_errors)
                    continue

                left_rail = _get_track_from_frame(frame, object_uid, "leftRail")
                right_rail = _get_track_from_frame(frame, object_uid, "rightRail")
                if left_rail is None or right_rail is None:
                    continue

                errors.extend(_check_rails_for_swap_or_intersection(left_rail, right_rail, context))

    return errors


def _check_rail_counts(context: IssueIdentifiers, left_count: int, right_count: int) -> list[Issue]:
    errors = []
    if left_count > 1:
        errors.append(
            Issue(
                type=IssueType.RAIL_SIDE,
                reason=f"This track has {left_count} left rails.",
                identifiers=context,
            )
        )
    if right_count > 1:
        errors.append(
            Issue(
                type=IssueType.RAIL_SIDE,
                reason=f"This track has {right_count} right rails.",
                identifiers=context,
            )
        )
    return errors


def _check_rails_for_swap_or_intersection(
    left_rail: raillabel.format.Poly2d,
    right_rail: raillabel.format.Poly2d,
    context: IssueIdentifiers,
) -> list[Issue]:
    if left_rail.object_id != right_rail.object_id:
        return []

    max_common_y = _find_max_common_y(left_rail, right_rail)
    if max_common_y is None:
        return []

    left_x = _find_x_by_y(max_common_y, left_rail)
    right_x = _find_x_by_y(max_common_y, right_rail)
    if left_x is None or right_x is None:
        return []

    if left_x >= right_x:
        return [
            Issue(
                type=IssueType.RAIL_SIDE,
                reason="The left and right rails of this track are swapped.",
                identifiers=context,
            )
        ]

    if _polylines_are_intersecting(left_rail, right_rail):
        return [
            Issue(
                type=IssueType.RAIL_SIDE,
                reason="The left and right rails of this track intersect.",
                identifiers=context,
            )
        ]

    return []


def _count_rails_per_track_in_frame(frame: raillabel.format.Frame) -> dict[UUID, tuple[int, int]]:
    """For each track, count the left and right rails."""
    counts: dict[UUID, list[int]] = {}

    unfiltered_annotations = list(frame.annotations.values())
    poly2ds: list[raillabel.format.Poly2d] = _filter_for_poly2ds(unfiltered_annotations)

    for poly2d in poly2ds:
        object_id = poly2d.object_id
        if object_id not in counts:
            counts[object_id] = [0, 0]

        rail_side = poly2d.attributes["railSide"]
        if rail_side == "leftRail":
            counts[object_id][0] += 1
        elif rail_side == "rightRail":
            counts[object_id][1] += 1
        else:
            # NOTE: This is ignored because it is covered by validate_ontology
            continue

    return {
        object_id: (object_counts[0], object_counts[1])
        for object_id, object_counts in counts.items()
    }


def _filter_for_poly2ds(
    unfiltered_annotations: list,
) -> list[raillabel.format.Poly2d]:
    return [
        annotation
        for annotation in unfiltered_annotations
        if isinstance(annotation, raillabel.format.Poly2d)
    ]


def _polylines_are_intersecting(
    line1: raillabel.format.Poly2d, line2: raillabel.format.Poly2d
) -> bool:
    """If the two polylines intersect anywhere, return the y interval where they intersect."""
    y_values_with_points_in_either_polyline: list[float] = sorted(
        _get_y_of_all_points_of_poly2d(line1).union(_get_y_of_all_points_of_poly2d(line2))
    )

    order: bool | None = None
    last_y: float | None = None
    for y in y_values_with_points_in_either_polyline:
        x1 = _find_x_by_y(y, line1)
        x2 = _find_x_by_y(y, line2)

        if x1 is None or x2 is None:
            order = None
            continue

        if x1 == x2:
            return True

        new_order = x1 < x2

        order_has_flipped = order is not None and new_order != order and last_y is not None
        if order_has_flipped:
            return True

        order = new_order
        last_y = y

    return False


def _find_max_y(poly2d: raillabel.format.Poly2d) -> float:
    return np.max([point.y for point in poly2d.points])


def _find_max_common_y(
    line1: raillabel.format.Poly2d, line2: raillabel.format.Poly2d
) -> float | None:
    one_line_is_empty = len(line1.points) == 0 or len(line2.points) == 0
    if one_line_is_empty:
        return None

    max_y_of_line1: float = _find_max_y(line1)
    highest_y_is_bottom_of_line1 = _y_in_poly2d(max_y_of_line1, line2)
    if highest_y_is_bottom_of_line1:
        return max_y_of_line1

    max_y_of_line2: float = _find_max_y(line2)
    highest_y_is_bottom_of_line2 = _y_in_poly2d(max_y_of_line2, line1)
    if highest_y_is_bottom_of_line2:
        return max_y_of_line2

    return None


def _find_x_by_y(y: float, poly2d: raillabel.format.Poly2d) -> float | None:
    """Find the x value of the first point where the polyline passes through y.

    Parameters
    ----------
    y : float
        The y value to check.
    poly2d : raillabel.format.Poly2d
       The Poly2D whose points will be checked against.

    Returns
    -------
    float | None
        The x value of a point (x,y) that poly2d passes through,
        or None if poly2d doesn't go through y.

    """
    # 1. Find the first two points between which y is located
    points = poly2d.points
    p1: raillabel.format.Point2d | None = None
    p2: raillabel.format.Point2d | None = None
    for i in range(len(points) - 1):
        current = points[i]
        next_ = points[i + 1]
        if (current.y >= y >= next_.y) or (current.y <= y <= next_.y):
            p1 = current
            p2 = next_
            break

    # 2. Abort if no valid points have been found
    if not (p1 and p2):
        return None

    # 3. Return early if p1=p2 (to avoid division by zero)
    if p1.x == p2.x:
        return p1.x

    # 4. Calculate m and n for the line g(x)=mx+n connecting p1 and p2
    m = (p2.y - p1.y) / (p2.x - p1.x)
    n = p1.y - (m * p1.x)

    # 5. Return early if m is 0, as that means p2.y=p1.y, which implies p2.y=p1.y=y
    if m == 0:
        return p1.x

    # 6. Calculate the x we were searching for and return it
    return (y - n) / m


def _get_track_from_frame(
    frame: raillabel.format.Frame, object_uid: UUID, rail_side: str
) -> raillabel.format.Poly2d | None:
    for annotation in frame.annotations.values():
        if not isinstance(annotation, raillabel.format.Poly2d):
            continue

        if annotation.object_id != object_uid:
            continue

        if "railSide" not in annotation.attributes:
            continue

        if annotation.attributes["railSide"] == rail_side:
            return annotation

    return None


def _get_y_of_all_points_of_poly2d(poly2d: raillabel.format.Poly2d) -> set[float]:
    y_values: set[float] = set()
    for point in poly2d.points:
        y_values.add(point.y)
    return y_values


def _y_in_poly2d(y: float, poly2d: raillabel.format.Poly2d) -> bool:
    """Check whether the polyline created by the given Poly2d passes through the given y value.

    Parameters
    ----------
    y : float
        The y value to check.
    poly2d : raillabel.format.Poly2d
        The Poly2D whose points will be checked against.

    Returns
    -------
    bool
        Does the Poly2d pass through the given y value?

    """
    # For every point (except the last), check if the y is between them
    for i in range(len(poly2d.points) - 1):
        current = poly2d.points[i]
        next_ = poly2d.points[i + 1]
        if (current.y >= y >= next_.y) or (current.y <= y <= next_.y):
            return True
    return False
