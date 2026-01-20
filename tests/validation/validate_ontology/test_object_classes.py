# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from uuid import UUID

from raillabel_providerkit.validation.validate_ontology._ontology_classes import (
    _ObjectClass,
    _BooleanAttribute,
    _IntegerAttribute,
    _MultiReferenceAttribute,
    _MultiSelectAttribute,
    _SingleSelectAttribute,
    _StringAttribute,
    _VectorAttribute,
    _SensorType,
    _AnnotationWithMetadata,
)
from raillabel_providerkit.validation import Issue, IssueType
from raillabel.scene_builder import SceneBuilder


def build_bbox_with_attributes(attributes: dict) -> _AnnotationWithMetadata:
    scene = (
        SceneBuilder.empty()
        .add_bbox(
            uid=UUID("00000000-0000-0000-0000-000000000000"), frame_id=1, attributes=attributes
        )
        .result
    )
    return _AnnotationWithMetadata(
        annotation_id=UUID("00000000-0000-0000-0000-000000000000"), frame_id=1, scene=scene
    )


def test_fromdict__empty():
    object_class = _ObjectClass.fromdict({})
    assert object_class.attributes == {}


def test_fromdict__boolean_attributes():
    object_class = _ObjectClass.fromdict({"isPeelable": {"attribute_type": "boolean"}})
    assert object_class.attributes == {
        "isPeelable": _BooleanAttribute.fromdict({"attribute_type": "boolean"})
    }


def test_fromdict__integer_attributes():
    object_class = _ObjectClass.fromdict({"numberOfFingers": {"attribute_type": "integer"}})
    assert object_class.attributes == {
        "numberOfFingers": _IntegerAttribute.fromdict({"attribute_type": "integer"})
    }


def test_fromdict__multi_reference_attributes():
    object_class = _ObjectClass.fromdict({"connectedTo": {"attribute_type": "multi-reference"}})
    assert object_class.attributes == {
        "connectedTo": _MultiReferenceAttribute.fromdict({"attribute_type": "multi-reference"})
    }


def test_fromdict__multi_select_attributes():
    object_class = _ObjectClass.fromdict(
        {"carries": {"attribute_type": {"type": "multi-select", "options": ["foo", "bar"]}}}
    )
    assert object_class.attributes == {
        "carries": _MultiSelectAttribute.fromdict(
            {"attribute_type": {"type": "multi-select", "options": ["foo", "bar"]}}
        )
    }


def test_fromdict__single_select_attributes():
    object_class = _ObjectClass.fromdict(
        {"carries": {"attribute_type": {"type": "single-select", "options": ["foo", "bar"]}}}
    )
    assert object_class.attributes == {
        "carries": _SingleSelectAttribute.fromdict(
            {"attribute_type": {"type": "single-select", "options": ["foo", "bar"]}}
        )
    }


def test_fromdict__string_attributes():
    object_class = _ObjectClass.fromdict({"name": {"attribute_type": "string"}})
    assert object_class.attributes == {
        "name": _StringAttribute.fromdict({"attribute_type": "string"})
    }


def test_fromdict__vector_attributes():
    object_class = _ObjectClass.fromdict({"carries": {"attribute_type": "vector"}})
    assert object_class.attributes == {
        "carries": _VectorAttribute.fromdict({"attribute_type": "vector"})
    }


def test_check__correct():
    object_class = _ObjectClass.fromdict({"isPeelable": {"attribute_type": "boolean"}})
    annotation_metadata = build_bbox_with_attributes({"isPeelable": True})

    issues = object_class.check(annotation_metadata)
    assert issues == []


def test_check__all_error_types():
    object_class = _ObjectClass.fromdict(
        {
            "isPeelable": {"attribute_type": "boolean"},
            "isStillGreen": {"attribute_type": "boolean"},
        }
    )
    annotation_metadata = build_bbox_with_attributes(
        {"isPeelable": "not-a-boolean", "unknown-attribute": False},
    )

    issues = object_class.check(annotation_metadata)
    issue_types_found = [issue.type for issue in issues]
    assert len(issues) == 3
    assert IssueType.ATTRIBUTE_UNDEFINED in issue_types_found
    assert IssueType.ATTRIBUTE_MISSING in issue_types_found
    assert IssueType.ATTRIBUTE_TYPE in issue_types_found


def test_check__undefined_attribute():
    object_class = _ObjectClass.fromdict({"isPeelable": {"attribute_type": "boolean"}})
    annotation_metadata = build_bbox_with_attributes({"isPeelable": True, "isBanana": False})

    issues = object_class.check(annotation_metadata)
    assert issues == [
        Issue(
            type=IssueType.ATTRIBUTE_UNDEFINED,
            identifiers=annotation_metadata.to_identifiers("isBanana"),
        )
    ]


def test_check__missing_attribute():
    object_class = _ObjectClass.fromdict(
        {"isPeelable": {"attribute_type": "boolean", "optional": False}}
    )
    annotation_metadata = build_bbox_with_attributes({})

    issues = object_class.check(annotation_metadata)
    assert issues == [
        Issue(
            type=IssueType.ATTRIBUTE_MISSING,
            identifiers=annotation_metadata.to_identifiers("isPeelable"),
        )
    ]


def test_check__missing_attribute_optional():
    object_class = _ObjectClass.fromdict(
        {"isPeelable": {"attribute_type": "boolean", "optional": True}}
    )
    annotation_metadata = build_bbox_with_attributes({})

    issues = object_class.check(annotation_metadata)
    assert issues == []


def test_check__false_attribute_type():
    object_class = _ObjectClass.fromdict({"likesTrains": {"attribute_type": "boolean"}})
    annotation_metadata = build_bbox_with_attributes({"likesTrains": "yes"})

    issues = object_class.check(annotation_metadata)
    assert issues == [
        Issue(
            type=IssueType.ATTRIBUTE_TYPE,
            identifiers=annotation_metadata.to_identifiers(attribute="likesTrains"),
            reason="Attribute 'likesTrains' is of type str (should be bool).",
        )
    ]


def test_compile_applicable_attributes__not_matching(example_boolean_attribute_dict):
    example_boolean_attribute_dict["sensor_types"] = ["camera"]
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    assert object_class._compile_applicable_attributes(_SensorType.LIDAR) == {}


def test_compile_applicable_attributes__matching(example_boolean_attribute_dict):
    example_boolean_attribute_dict["sensor_types"] = ["camera"]
    object_class = _ObjectClass.fromdict({"test_attribute": example_boolean_attribute_dict})
    assert "test_attribute" in object_class._compile_applicable_attributes(_SensorType.CAMERA)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
