# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from uuid import UUID

import raillabel

from raillabel_providerkit.validation.issue import Issue, IssueIdentifiers, IssueType

# Mapping:
# - camera: Bbox, Poly2d (for tracks/transitions)
# - lidar: Cuboid, Poly3d (for tracks), Seg3d (for segmentation)
# - radar: Bbox and Cuboid
_ALLOWED_BY_SENSOR_TYPE: dict[str, tuple[str, ...]] = {
    "camera": ("Bbox", "Poly2d"),
    "lidar": ("Cuboid", "Poly3d", "Seg3d"),
    "radar": ("Bbox", "Cuboid"),
}


def _normalize_anno_type(t: str) -> str:
    t_low = (t or "").strip().lower()
    mapping = {
        "bbox": "Bbox",
        "cuboid": "Cuboid",
        "poly2d": "Poly2d",
        "poly3d": "Poly3d",
        "num": "Num",
        "seg3d": "Seg3d",
    }
    return mapping.get(t_low, t if t else "")


def _iter_annotations(scene: raillabel.Scene) -> Iterable[tuple[int, Any]]:
    """Iterate over all annotations in the scene."""
    frames = getattr(scene, "frames", {}) or {}
    for frame_id, frame in getattr(frames, "items", lambda: frames.items())():
        annotations = getattr(frame, "annotations", {}) or {}
        for anno in annotations.values():
            yield frame_id, anno


def _get_annotation_id(anno: object) -> UUID | None:
    return getattr(anno, "id", None)


def _get_annotation_type(anno: object) -> str | None:
    t = getattr(anno, "type", None)
    if not t:
        return None
    return _normalize_anno_type(str(t))


def _get_sensor_id_from_annotation(anno: object) -> str | None:
    # 1) coordinate.sensor / coordinate.sensor_id
    coord = getattr(anno, "coordinate", None)
    if coord is not None:
        sid = getattr(coord, "sensor", None) or getattr(coord, "sensor_id", None)
        if sid:
            return str(sid)

    # 2) anno.sensor / anno.sensor_id
    for attr in ("sensor", "sensor_id"):
        sid = getattr(anno, attr, None)
        if sid:
            return str(sid)

    # 3) coordinates-Collection
    coords = getattr(anno, "coordinates", None)
    if isinstance(coords, list | tuple):
        for c in coords:
            sid = getattr(c, "sensor", None) or getattr(c, "sensor_id", None)
            if sid:
                return str(sid)

    return None


def _sensor_type(scene: raillabel.Scene, sensor_id: str) -> str | None:
    """Return the sensor type ('camera', 'lidar', 'radar') or None if unknown."""
    sensors = getattr(scene, "sensors", {}) or {}
    sensor = sensors.get(sensor_id)
    if sensor is None and hasattr(sensors, "get"):
        sensor = sensors.get(sensor_id)
    if sensor is None:
        return None
    s_type = getattr(sensor, "type", None)
    return str(s_type).lower() if s_type else None


def validate_annotation_type_per_sensor(scene: raillabel.Scene) -> list[Issue]:
    """Validate that each annotation type is compatible with its sensor type.

    Returns:
        List of Issues if mismatches are found.
    """
    issues: list[Issue] = []

    for frame_id, anno in _iter_annotations(scene):
        a_type = _get_annotation_type(anno)
        if not a_type:
            continue

        sensor_id = _get_sensor_id_from_annotation(anno)
        if not sensor_id:
            continue

        s_type = _sensor_type(scene, sensor_id)
        if not s_type:
            continue

        allowed = _ALLOWED_BY_SENSOR_TYPE.get(s_type, ())
        if allowed and a_type not in allowed:
            issue = Issue(
                type=IssueType.ANNOTATION_SENSOR_MISMATCH,
                identifiers=IssueIdentifiers(
                    frame=frame_id,
                    sensor=sensor_id,
                    annotation=_get_annotation_id(anno),
                    annotation_type=a_type,
                ),
                reason=(
                    f"Annotation type '{a_type}' not allowed for sensor type '{s_type}'. "
                    f"Allowed types: {', '.join(allowed) if allowed else 'n/a'}."
                ),
            )
            issues.append(issue)

    return issues
