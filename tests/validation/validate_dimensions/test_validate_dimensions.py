# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel.scene_builder import SceneBuilder
from raillabel.format import Size3d

from raillabel_providerkit.validation import validate_dimensions
from raillabel_providerkit.validation import IssueType


def test_empty_scene():
    scene = SceneBuilder.empty().result

    issues = validate_dimensions(scene)
    assert issues == []


def test_undefined_class():
    scene = SceneBuilder.empty().add_cuboid(object_name="undefined_0001").result

    issues = validate_dimensions(scene)
    assert issues == []


def test_valid_dimensions_only_class():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="person_0001", size=Size3d(x=0.4, y=0.4, z=1.9))
        .add_cuboid(object_name="signal_0003", size=Size3d(x=0.8, y=1.0, z=3.5))
        .result
    )

    issues = validate_dimensions(scene)
    assert issues == []


def test_valid_dimensions_class_and_attributes():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(
            object_name="person_0001",
            attributes={"age": "child", "pose": "upgright"},
            size=Size3d(x=1.5, y=0.4, z=0.5),
        )
        .result
    )

    issues = validate_dimensions(scene)
    assert issues == []


def test_height_too_small():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="person_0001", size=Size3d(x=0.5, y=0.5, z=0.01))
        .result
    )

    issues = validate_dimensions(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.DIMENSION_INVALID
    assert "height" in issues[0].reason.lower()
    assert "small" in issues[0].reason.lower()
    assert "0.01" in issues[0].reason.lower()
    assert "0.1" in issues[0].reason.lower()


def test_height_too_large():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="person_0001", size=Size3d(x=0.5, y=0.5, z=10))
        .result
    )

    issues = validate_dimensions(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.DIMENSION_INVALID
    assert "height" in issues[0].reason.lower()
    assert "large" in issues[0].reason.lower()
    assert "10" in issues[0].reason.lower()
    assert "2.7" in issues[0].reason.lower()


def test_x_axis_too_small():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="wheelchair_0001", size=Size3d(x=0.1, y=0.8, z=1))
        .result
    )

    issues = validate_dimensions(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.DIMENSION_INVALID
    assert "width" in issues[0].reason.lower()
    assert "small" in issues[0].reason.lower()
    assert "0.1" in issues[0].reason.lower()
    assert "0.5" in issues[0].reason.lower()


def test_y_axis_too_small():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="wheelchair_0001", size=Size3d(x=0.8, y=0.1, z=1))
        .result
    )

    issues = validate_dimensions(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.DIMENSION_INVALID
    assert "width" in issues[0].reason.lower()
    assert "small" in issues[0].reason.lower()
    assert "0.1" in issues[0].reason.lower()
    assert "0.5" in issues[0].reason.lower()


def test_x_axis_too_large():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="wheelchair_0001", size=Size3d(x=5, y=0.8, z=1))
        .result
    )

    issues = validate_dimensions(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.DIMENSION_INVALID
    assert "width" in issues[0].reason.lower()
    assert "large" in issues[0].reason.lower()
    assert "5" in issues[0].reason.lower()
    assert "1.6" in issues[0].reason.lower()


def test_y_axis_too_large():
    scene = (
        SceneBuilder.empty()
        .add_cuboid(object_name="wheelchair_0001", size=Size3d(x=0.8, y=5, z=1))
        .result
    )

    issues = validate_dimensions(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.DIMENSION_INVALID
    assert "width" in issues[0].reason.lower()
    assert "large" in issues[0].reason.lower()
    assert "5" in issues[0].reason.lower()
    assert "1.6" in issues[0].reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
