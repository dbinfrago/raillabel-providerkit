# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from uuid import UUID

from raillabel_providerkit.validation.validate_ontology._ontology_classes import (
    _Scope,
    _AnyAttribute,
)
from raillabel_providerkit.validation import IssueIdentifiers, IssueType


def test_supports__empty_dict():
    assert not _AnyAttribute.supports({})


def test_supports__correct(example_any_attribute_dict):
    assert _AnyAttribute.supports(example_any_attribute_dict)


def test_supports__invalid_type_string(example_string_attribute_dict):
    assert not _AnyAttribute.supports(example_string_attribute_dict)


def test_supports__invalid_type_dict(example_single_select_attribute_dict):
    assert not _AnyAttribute.supports(example_single_select_attribute_dict)


def test_fromdict__empty():
    with pytest.raises(ValueError):
        _AnyAttribute.fromdict({})


def test_fromdict__optional(example_any_attribute_dict):
    for val in [False, True]:
        example_any_attribute_dict["optional"] = val
        assert _AnyAttribute.fromdict(example_any_attribute_dict).optional == val


def test_fromdict__scope_invalid(example_any_attribute_dict):
    with pytest.raises(ValueError):
        example_any_attribute_dict["scope"] = "some random string"
        _AnyAttribute.fromdict(example_any_attribute_dict)


def test_fromdict__scope_empty(example_any_attribute_dict):
    del example_any_attribute_dict["scope"]
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.ANNOTATION


def test_fromdict__scope_annotation(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "annotation"
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.ANNOTATION


def test_fromdict__scope_frame(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "frame"
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.FRAME


def test_fromdict__scope_object(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "object"
    assert _AnyAttribute.fromdict(example_any_attribute_dict).scope == _Scope.OBJECT


def test_check_type_and_value__correct_boolean(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert attr.check_type_and_value("example_name", True, IssueIdentifiers()) == []


def test_check_type_and_value__correct_string(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert attr.check_type_and_value("example_name", "hello_there", IssueIdentifiers()) == []


def test_check_type_and_value__correct_int(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert attr.check_type_and_value("example_name", 42, IssueIdentifiers()) == []


def test_check_type_and_value__correct_list(example_any_attribute_dict):
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_type_and_value("example_name", ["this", "is", "a", "test"], IssueIdentifiers())
        == []
    )


def test_check_scope_for_two_annotations__ignore_unmatched_types(
    example_any_attribute_dict,
):
    example_any_attribute_dict["scope"] = "annotation"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_scope_for_two_annotations(
            "example_name", ["foo"], 42, IssueIdentifiers(), IssueIdentifiers()
        )
        == []
    )


def test_check_scope_for_two_annotations__annotation_correct(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "annotation"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_scope_for_two_annotations(
            "example_name", ["foo"], ["bar"], IssueIdentifiers(), IssueIdentifiers()
        )
        == []
    )


def test_check_scope_for_two_annotations__frame_correct_same_frame(
    example_any_attribute_dict, ignore_uuid
):
    example_any_attribute_dict["scope"] = "frame"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_scope_for_two_annotations(
            "example_name",
            ["foo"],
            ["foo"],
            IssueIdentifiers(frame=42, object=ignore_uuid),
            IssueIdentifiers(frame=42, object=ignore_uuid),
        )
        == []
    )


def test_check_scope_for_two_annotations__frame_correct_different_frame(
    example_any_attribute_dict, ignore_uuid
):
    example_any_attribute_dict["scope"] = "frame"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_scope_for_two_annotations(
            "example_name",
            ["foo"],
            ["bar"],
            IssueIdentifiers(frame=42, object=ignore_uuid),
            IssueIdentifiers(frame=73, object=ignore_uuid),
        )
        == []
    )


def test_check_scope_for_two_annotations__frame_inconsistent(
    example_any_attribute_dict, ignore_uuid
):
    example_any_attribute_dict["scope"] = "frame"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    errors = attr.check_scope_for_two_annotations(
        "example_name",
        ["foo"],
        ["bar"],
        IssueIdentifiers(frame=42, object=ignore_uuid),
        IssueIdentifiers(frame=42, object=ignore_uuid),
    )
    assert len(errors) == 1
    assert errors[0].type == IssueType.ATTRIBUTE_SCOPE


def test_check_scope_for_two_annotations__object_correct_same_object(
    example_any_attribute_dict,
):
    example_any_attribute_dict["scope"] = "object"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_scope_for_two_annotations(
            "example_name",
            ["foo"],
            ["foo"],
            IssueIdentifiers(frame=42, object=UUID("44de4109-ee2c-4729-956d-8e965c7ce231")),
            IssueIdentifiers(frame=42, object=UUID("44de4109-ee2c-4729-956d-8e965c7ce231")),
        )
        == []
    )


def test_check_scope_for_two_annotations__object_correct_different_object(
    example_any_attribute_dict,
):
    example_any_attribute_dict["scope"] = "object"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_scope_for_two_annotations(
            "example_name",
            ["foo"],
            ["bar"],
            IssueIdentifiers(frame=42, object=UUID("44de4109-ee2c-4729-956d-8e965c7ce231")),
            IssueIdentifiers(frame=42, object=UUID("98e93d07-e81a-4827-8c62-a82c3c4bfc42")),
        )
        == []
    )


def test_check_scope_for_two_annotations__object_inconsistent(example_any_attribute_dict):
    example_any_attribute_dict["scope"] = "object"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    errors = attr.check_scope_for_two_annotations(
        "example_name",
        ["foo"],
        ["bar"],
        IssueIdentifiers(frame=42, object=UUID("44de4109-ee2c-4729-956d-8e965c7ce231")),
        IssueIdentifiers(frame=42, object=UUID("44de4109-ee2c-4729-956d-8e965c7ce231")),
    )
    assert len(errors) == 1
    assert errors[0].type == IssueType.ATTRIBUTE_SCOPE


def test_check_scope_for_two_annotations__object_correct_different_order(
    example_any_attribute_dict,
):
    example_any_attribute_dict["scope"] = "object"
    attr = _AnyAttribute.fromdict(example_any_attribute_dict)
    assert (
        attr.check_scope_for_two_annotations(
            "example_name",
            ["foo", "bar"],
            ["bar", "foo"],
            IssueIdentifiers(frame=42, object=UUID("44de4109-ee2c-4729-956d-8e965c7ce231")),
            IssueIdentifiers(frame=42, object=UUID("44de4109-ee2c-4729-956d-8e965c7ce231")),
        )
        == []
    )
