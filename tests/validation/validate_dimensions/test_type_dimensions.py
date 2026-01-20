# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel.format import Cuboid, Point3d, Quaternion, Size3d

from raillabel_providerkit.validation.validate_dimensions._dimensions import _TypeDimensions


def build_cuboid(attributes: dict = {}) -> Cuboid:
    return Cuboid(
        pos=Point3d(0, 0, 0),
        quat=Quaternion(0, 0, 0, 1),
        size=Size3d(0, 0, 0),
        object_id=None,
        sensor_id=None,
        attributes=attributes,
    )


def test_applies_only_class_true():
    type_dimensions = _TypeDimensions(type="person")
    assert type_dimensions.applies("person", build_cuboid())


def test_applies_only_class_false():
    type_dimensions = _TypeDimensions(type="person")
    assert not type_dimensions.applies("animal", build_cuboid())


def test_applies_multiple_classes_true():
    type_dimensions = _TypeDimensions(type=["person", "animal"])
    assert type_dimensions.applies("animal", build_cuboid())


def test_applies_multiple_classes_false():
    type_dimensions = _TypeDimensions(type=["person", "animal"])
    assert not type_dimensions.applies("road_vehicle", build_cuboid())


def test_applies_class_and_attributes_true():
    type_dimensions = _TypeDimensions(type="person", attributes={"age": "adult"})
    assert type_dimensions.applies("person", build_cuboid(attributes={"age": "adult"}))


def test_applies_class_and_attributes_false():
    type_dimensions = _TypeDimensions(type="person", attributes={"age": "adult"})
    assert not type_dimensions.applies("person", build_cuboid(attributes={"age": "child"}))


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
