# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, List
from uuid import uuid4

import pytest

from raillabel_providerkit.validation.issue import IssueType
from raillabel_providerkit.validation.validate_annotation_type_per_sensor import (
    validate_annotation_type_per_sensor,
)


@dataclass
class _Coord:
    sensor: Optional[str] = None
    sensor_id: Optional[str] = None


@dataclass
class _Annotation:
    id: str
    type: str
    coordinate: Optional[_Coord] = None


@dataclass
class _Frame:
    annotations: Dict[str, _Annotation]


@dataclass
class _Sensor:
    id: str
    type: str


@dataclass
class _Scene:
    sensors: Dict[str, _Sensor]
    frames: Dict[int, _Frame]


# ----------------------------------------------------------------


def _mk_bbox(sensor_id: str) -> _Annotation:
    return _Annotation(id=str(uuid4()), type="Bbox", coordinate=_Coord(sensor=sensor_id))


def _mk_cuboid(sensor_id: str) -> _Annotation:
    return _Annotation(id=str(uuid4()), type="Cuboid", coordinate=_Coord(sensor=sensor_id))


def test_camera_allows_only_bbox():
    scene = _Scene(
        sensors={"cam0": _Sensor(id="cam0", type="camera")},
        frames={0: _Frame(annotations={"a": _mk_bbox("cam0")})},
    )
    issues = validate_annotation_type_per_sensor(scene)
    assert issues == []

    scene_bad = _Scene(
        sensors={"cam0": _Sensor(id="cam0", type="camera")},
        frames={0: _Frame(annotations={"a": _mk_cuboid("cam0")})},
    )
    issues = validate_annotation_type_per_sensor(scene_bad)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ANNOTATION_SENSOR_MISMATCH
    assert issues[0].identifiers.annotation_type == "Cuboid"
    assert issues[0].identifiers.sensor == "cam0"
    assert issues[0].identifiers.frame == 0


def test_lidar_allows_only_cuboid():
    scene = _Scene(
        sensors={"lid0": _Sensor(id="lid0", type="lidar")},
        frames={1: _Frame(annotations={"a": _mk_cuboid("lid0")})},
    )
    assert validate_annotation_type_per_sensor(scene) == []

    scene_bad = _Scene(
        sensors={"lid0": _Sensor(id="lid0", type="lidar")},
        frames={1: _Frame(annotations={"a": _mk_bbox("lid0")})},
    )
    issues = validate_annotation_type_per_sensor(scene_bad)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ANNOTATION_SENSOR_MISMATCH
    assert issues[0].identifiers.annotation_type == "Bbox"
    assert issues[0].identifiers.sensor == "lid0"
    assert issues[0].identifiers.frame == 1


def test_radar_allows_bbox_and_cuboid():
    scene = _Scene(
        sensors={"rad0": _Sensor(id="rad0", type="radar")},
        frames={2: _Frame(annotations={"a": _mk_bbox("rad0"), "b": _mk_cuboid("rad0")})},
    )
    assert validate_annotation_type_per_sensor(scene) == []


def test_missing_sensor_binding_is_ignored():
    ann = _Annotation(id=str(uuid4()), type="Bbox", coordinate=None)  # kein Sensor
    scene = _Scene(
        sensors={"cam0": _Sensor(id="cam0", type="camera")},
        frames={3: _Frame(annotations={"a": ann})},
    )
    assert validate_annotation_type_per_sensor(scene) == []
