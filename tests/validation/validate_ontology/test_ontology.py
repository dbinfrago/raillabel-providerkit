# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from uuid import UUID

import pytest

from raillabel_providerkit.validation.validate_ontology._ontology_classes import (
    _Ontology,
    _AnnotationWithMetadata,
)
from raillabel_providerkit.validation import IssueType, IssueIdentifiers, Issue
from raillabel.scene_builder import SceneBuilder


def test_fromdict__empty():
    ontology = _Ontology.fromdict({})
    assert len(ontology.classes) == 0
    assert len(ontology.errors) == 0


def test_fromdict__simple():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    assert len(ontology.classes) == 1
    assert "banana" in ontology.classes
    assert len(ontology.errors) == 0


def test_check__empty_scene():
    ontology = _Ontology.fromdict({})
    scene = SceneBuilder.empty().result

    issues = ontology.check(scene)
    assert issues == []


def test_check__correct():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="banana_0001")
        .add_bbox(
            object_name="banana_0001",
            attributes={"is_peelable": True},
        )
        .result
    )

    issues = ontology.check(scene)
    assert issues == []


def test_check__undefined_object_type():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="apple",
            object_name="apple_0001",
        )
        .add_bbox(
            object_name="banana_0001",
            attributes={"is_peelable": True},
        )
        .result
    )

    issues = ontology.check(scene)
    assert issues == [
        Issue(
            IssueType.OBJECT_TYPE_UNDEFINED,
            IssueIdentifiers(
                object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"), object_type="apple"
            ),
        )
    ]


def test_check__invalid_attribute_type():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="banana",
            object_name="banana_0001",
        )
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_center",
            attributes={"is_peelable": "i-like-trains"},
        )
        .result
    )
    issues = ontology.check(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_TYPE
    assert issues[0].identifiers == IssueIdentifiers(
        annotation=UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
        annotation_type="Bbox",
        attribute="is_peelable",
        frame=0,
        object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
        object_type="banana",
        sensor="rgb_center",
    )


def test_check__scope_inconsistency():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "frame"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="banana",
            object_name="banana_0001",
        )
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_center",
            attributes={"is_peelable": True},
        )
        .add_bbox(
            UUID("0ef548ab-70bc-4e74-9e11-76cff46ada0f"),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_left",
            attributes={"is_peelable": False},
        )
        .result
    )
    issues = ontology.check(scene)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_SCOPE
    assert issues[0].identifiers == IssueIdentifiers(
        annotation=UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
        annotation_type="Bbox",
        attribute="is_peelable",
        frame=0,
        object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
        object_type="banana",
        sensor="rgb_center",
    ) or issues[0].identifiers == IssueIdentifiers(
        annotation=UUID("0ef548ab-70bc-4e74-9e11-76cff46ada0f"),
        annotation_type="Bbox",
        attribute="is_peelable",
        frame=0,
        object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
        object_type="banana",
        sensor="rgb_left",
    )


def test_check_class_validity__empty_scene():
    ontology = _Ontology.fromdict({})
    scene = SceneBuilder.empty().result
    ontology._check_class_validity(scene)
    assert ontology.errors == []


def test_check_class_validity__correct():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = SceneBuilder.empty().add_object(object_type="banana").result
    ontology._check_class_validity(scene)
    assert ontology.errors == []


def test_check_class_validity__incorrect():
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"), object_name="apple_0000")
        .add_bbox(
            object_name="apple_0000",
        )
        .result
    )
    ontology._check_class_validity(scene)
    assert len(ontology.errors) == 1
    assert ontology.errors[0].type == IssueType.OBJECT_TYPE_UNDEFINED
    assert ontology.errors[0].identifiers == IssueIdentifiers(
        object=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"), object_type="apple"
    )


def test_check_attribute_scopes__empty():
    ontology = _Ontology.fromdict({})
    assert ontology._check_attribute_scopes([]) == []


def test_check_attribute_scopes__annotation(sample_uuid_1, sample_uuid_2, sample_uuid_3):
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="banana_0001")
        .add_bbox(
            uid=sample_uuid_1,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": True},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_2,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": False},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_3,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": True},
            sensor_id="rgb_center",
        )
        .result
    )
    assert (
        ontology._check_attribute_scopes(
            [
                _AnnotationWithMetadata(sample_uuid_1, 0, scene),
                _AnnotationWithMetadata(sample_uuid_2, 0, scene),
                _AnnotationWithMetadata(sample_uuid_3, 0, scene),
            ]
        )
        == []
    )


def test_check_attribute_scopes__frame_correct(
    sample_uuid_1, sample_uuid_2, sample_uuid_3, sample_uuid_4
):
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "frame"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="banana_0001")
        .add_object(object_name="banana_0002")
        .add_bbox(
            uid=sample_uuid_1,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": True},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_2,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": True},
            sensor_id="rgb_left",
        )
        .add_bbox(
            uid=sample_uuid_3,
            frame_id=1,
            object_name="banana_0001",
            attributes={"is_peelable": False},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_4,
            frame_id=0,
            object_name="banana_0002",
            attributes={"is_peelable": False},
            sensor_id="rgb_center",
        )
        .result
    )
    assert (
        ontology._check_attribute_scopes(
            [
                _AnnotationWithMetadata(sample_uuid_1, 0, scene),
                _AnnotationWithMetadata(sample_uuid_2, 0, scene),
                _AnnotationWithMetadata(sample_uuid_3, 1, scene),
                _AnnotationWithMetadata(sample_uuid_4, 0, scene),
            ]
        )
        == []
    )


def test_check_attribute_scopes__frame_incorrect(
    sample_uuid_1, sample_uuid_2, sample_uuid_3, sample_uuid_4, sample_uuid_5
):
    ontology = _Ontology.fromdict(
        {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "frame"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="banana_0001")
        .add_bbox(
            uid=sample_uuid_1,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": True},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_2,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": True},
            sensor_id="rgb_left",
        )
        .add_bbox(
            uid=sample_uuid_3,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": False},
            sensor_id="rgb_right",
        )
        .add_bbox(
            uid=sample_uuid_4,
            frame_id=0,
            object_name="banana_0001",
            attributes={"is_peelable": False},
            sensor_id="ir_center",
        )
        .add_bbox(
            uid=sample_uuid_5,
            frame_id=1,
            object_name="banana_0001",
            attributes={"is_peelable": False},
            sensor_id="rgb_center",
        )
        .result
    )
    errors = ontology._check_attribute_scopes(
        [
            _AnnotationWithMetadata(sample_uuid_1, 0, scene),
            _AnnotationWithMetadata(sample_uuid_2, 0, scene),
            _AnnotationWithMetadata(sample_uuid_3, 0, scene),
            _AnnotationWithMetadata(sample_uuid_4, 0, scene),
            _AnnotationWithMetadata(sample_uuid_5, 1, scene),
        ]
    )
    assert len(errors) == 2
    for error in errors:
        assert error.type == IssueType.ATTRIBUTE_SCOPE


def test_check_attribute_scopes__object_correct(
    sample_uuid_1, sample_uuid_2, sample_uuid_3, sample_uuid_4, sample_uuid_5
):
    ontology = _Ontology.fromdict(
        {"person": {"greeting": {"attribute_type": "string", "scope": "object"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="person_0001")
        .add_object(object_name="person_0002")
        .add_bbox(
            uid=sample_uuid_1,
            frame_id=0,
            object_name="person_0001",
            attributes={"greeting": "hello"},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_2,
            frame_id=20,
            object_name="person_0001",
            attributes={"greeting": "hello"},
            sensor_id="rgb_left",
        )
        .add_bbox(
            uid=sample_uuid_3,
            frame_id=0,
            object_name="person_0001",
            attributes={"greeting": "hello"},
            sensor_id="rgb_right",
        )
        .add_bbox(
            uid=sample_uuid_4,
            frame_id=42,
            object_name="person_0001",
            attributes={"greeting": "hello"},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_5,
            frame_id=1,
            object_name="person_0002",
            attributes={"greeting": "hey"},
            sensor_id="rgb_center",
        )
        .result
    )
    assert (
        ontology._check_attribute_scopes(
            [
                _AnnotationWithMetadata(sample_uuid_1, 0, scene),
                _AnnotationWithMetadata(sample_uuid_2, 20, scene),
                _AnnotationWithMetadata(sample_uuid_3, 0, scene),
                _AnnotationWithMetadata(sample_uuid_4, 42, scene),
                _AnnotationWithMetadata(sample_uuid_5, 1, scene),
            ]
        )
        == []
    )


def test_check_attribute_scopes__object_incorrect(
    sample_uuid_1, sample_uuid_2, sample_uuid_3, sample_uuid_4, sample_uuid_5
):
    ontology = _Ontology.fromdict(
        {"person": {"greeting": {"attribute_type": "string", "scope": "object"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="person_0001")
        .add_object(object_name="person_0002")
        .add_bbox(
            uid=sample_uuid_1,
            frame_id=0,
            object_name="person_0001",
            attributes={"greeting": "hello"},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_2,
            frame_id=20,
            object_name="person_0001",
            attributes={"greeting": "hi"},
            sensor_id="rgb_left",
        )
        .add_bbox(
            uid=sample_uuid_3,
            frame_id=0,
            object_name="person_0001",
            attributes={"greeting": "hey"},
            sensor_id="rgb_right",
        )
        .add_bbox(
            uid=sample_uuid_4,
            frame_id=42,
            object_name="person_0002",
            attributes={"greeting": "hello there"},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_5,
            frame_id=1,
            object_name="person_0001",
            attributes={"greeting": "ah, i have expected you"},
            sensor_id="rgb_center",
        )
        .result
    )
    errors = ontology._check_attribute_scopes(
        [
            _AnnotationWithMetadata(sample_uuid_1, 0, scene),
            _AnnotationWithMetadata(sample_uuid_2, 20, scene),
            _AnnotationWithMetadata(sample_uuid_3, 0, scene),
            _AnnotationWithMetadata(sample_uuid_4, 42, scene),
            _AnnotationWithMetadata(sample_uuid_5, 1, scene),
        ]
    )
    assert len(errors) == 3
    for error in errors:
        assert error.type == IssueType.ATTRIBUTE_SCOPE


def test_check_attribute_scopes__ignore_unknown_attribute(sample_uuid_1, sample_uuid_2):
    ontology = _Ontology.fromdict(
        {"person": {"greeting": {"attribute_type": "string", "scope": "object"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="person_0001")
        .add_bbox(
            uid=sample_uuid_1,
            frame_id=0,
            object_name="person_0001",
            attributes={"greeting": "hello", "likes_trains": True},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_2,
            frame_id=20,
            object_name="person_0001",
            attributes={"greeting": "hello", "likes_trains": False},
            sensor_id="rgb_left",
        )
        .result
    )
    assert (
        ontology._check_attribute_scopes(
            [
                _AnnotationWithMetadata(sample_uuid_1, 0, scene),
                _AnnotationWithMetadata(sample_uuid_2, 20, scene),
            ]
        )
        == []
    )


def test_check_attribute_scopes__ignore_missing_attribute_from_one(sample_uuid_1, sample_uuid_2):
    ontology = _Ontology.fromdict(
        {"person": {"greeting": {"attribute_type": "string", "scope": "object"}}}
    )
    scene = (
        SceneBuilder.empty()
        .add_object(object_name="person_0001")
        .add_bbox(
            uid=sample_uuid_1,
            frame_id=0,
            object_name="person_0001",
            attributes={"greeting": "hello"},
            sensor_id="rgb_center",
        )
        .add_bbox(
            uid=sample_uuid_2,
            frame_id=20,
            object_name="person_0001",
            attributes={},
            sensor_id="rgb_left",
        )
        .result
    )
    assert (
        ontology._check_attribute_scopes(
            [
                _AnnotationWithMetadata(sample_uuid_1, 0, scene),
                _AnnotationWithMetadata(sample_uuid_2, 20, scene),
            ]
        )
        == []
    )


def test_compile_annotations__empty_scene():
    scene = SceneBuilder.empty().result
    annotations = _Ontology._compile_annotations(scene)
    assert len(annotations) == 0


def test_compile_annotations__three_annotations_in_two_frames():
    scene = (
        SceneBuilder.empty()
        .add_bbox(
            frame_id=0,
            object_name="box_0001",
        )
        .add_bbox(
            frame_id=0,
            object_name="box_0002",
        )
        .add_bbox(
            frame_id=1,
            object_name="box_0003",
        )
        .result
    )
    annotations = _Ontology._compile_annotations(scene)
    assert len(annotations) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
