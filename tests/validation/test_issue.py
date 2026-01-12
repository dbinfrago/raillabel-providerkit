# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import jsonschema.exceptions
import pytest
from uuid import UUID

import jsonschema

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def test_issue_identifiers_serialize__empty():
    identifiers = IssueIdentifiers()
    assert identifiers.serialize() == {}


def test_issue_identifiers_serialize__filled():
    identifiers = IssueIdentifiers(
        annotation=UUID("f9b8aa82-e42b-43df-85fb-99ab51145732"),
        annotation_type="Poly3d",
        attribute="likes_trains",
        frame=42,
        object=UUID("6caf0a36-3872-4368-8d88-801593c7bc24"),
        object_type="person",
        sensor="rgb_center",
    )
    assert identifiers.serialize() == {
        "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
        "annotation_type": "Poly3d",
        "attribute": "likes_trains",
        "frame": 42,
        "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
        "object_type": "person",
        "sensor": "rgb_center",
    }


def test_issue_identifiers_deserialize__empty():
    identifiers = IssueIdentifiers.deserialize({})
    assert identifiers == IssueIdentifiers(
        annotation=None,
        annotation_type=None,
        attribute=None,
        frame=None,
        object=None,
        object_type=None,
        sensor=None,
    )


def test_issue_identifiers_deserialize__filled():
    identifiers = IssueIdentifiers.deserialize(
        {
            "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
            "annotation_type": "Poly3d",
            "attribute": "likes_trains",
            "frame": 42,
            "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
            "object_type": "person",
            "sensor": "rgb_center",
        }
    )
    assert identifiers == IssueIdentifiers(
        annotation=UUID("f9b8aa82-e42b-43df-85fb-99ab51145732"),
        annotation_type="Poly3d",
        attribute="likes_trains",
        frame=42,
        object=UUID("6caf0a36-3872-4368-8d88-801593c7bc24"),
        object_type="person",
        sensor="rgb_center",
    )


def test_issue_identifiers_deserialize__invalid_type_annotation():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        IssueIdentifiers.deserialize(
            {
                "annotation": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_attribute():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        IssueIdentifiers.deserialize(
            {
                "attribute": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_frame():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        IssueIdentifiers.deserialize(
            {
                "frame": "the_first_frame",
            }
        )


def test_issue_identifiers_deserialize__invalid_type_object():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        IssueIdentifiers.deserialize(
            {
                "object": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_object_type():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        IssueIdentifiers.deserialize(
            {
                "object_type": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_sensor():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        IssueIdentifiers.deserialize(
            {
                "sensor": 42,
            }
        )


def test_issue_serialize__simple():
    issue = Issue(
        IssueType.ATTRIBUTE_MISSING,
        IssueIdentifiers(
            UUID("f9b8aa82-e42b-43df-85fb-99ab51145732"),
            "likes_trains",
            42,
            UUID("6caf0a36-3872-4368-8d88-801593c7bc24"),
            "person",
            "rgb_center",
        ),
        "some reason",
    )
    assert issue.serialize() == {
        "type": "AttributeMissing",
        "identifiers": issue.identifiers.serialize(),
        "reason": "some reason",
    }


def test_issue_serialize__do_not_add_reason_if_none():
    issue = Issue(
        IssueType.ATTRIBUTE_MISSING,
        IssueIdentifiers(
            UUID("f9b8aa82-e42b-43df-85fb-99ab51145732"),
            "likes_trains",
            42,
            UUID("6caf0a36-3872-4368-8d88-801593c7bc24"),
            "person",
            "rgb_center",
        ),
    )
    assert issue.serialize() == {
        "type": "AttributeMissing",
        "identifiers": issue.identifiers.serialize(),
    }


def test_issue_serialize__schema_error():
    issue = Issue(
        IssueType.SCHEMA,
        ["this", "is", "some", "schema", "error", 73],
        "some reason",
    )
    assert issue.serialize() == {
        "type": "SchemaIssue",
        "identifiers": ["this", "is", "some", "schema", "error", 73],
        "reason": "some reason",
    }


def test_issue_deserialize__simple():
    serialized = {
        "type": "AttributeMissing",
        "identifiers": {
            "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
            "attribute": "likes_trains",
            "frame": 42,
            "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
            "object_type": "person",
            "sensor": "rgb_center",
        },
        "reason": "some reason",
    }
    issue = Issue.deserialize(serialized)
    assert issue == Issue(
        IssueType.ATTRIBUTE_MISSING,
        IssueIdentifiers.deserialize(serialized["identifiers"]),
        "some reason",
    )


def test_issue_deserialize__without_reason():
    serialized = {
        "type": "AttributeMissing",
        "identifiers": {
            "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
            "attribute": "likes_trains",
            "frame": 42,
            "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
            "object_type": "person",
            "sensor": "rgb_center",
        },
    }
    issue = Issue.deserialize(serialized)
    assert issue == Issue(
        IssueType.ATTRIBUTE_MISSING, IssueIdentifiers.deserialize(serialized["identifiers"]), None
    )


def test_issue_deserialize__undefined_issue_type():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        Issue.deserialize({"type": "INVALID", "identifiers": {}})


def test_issue_deserialize__schema_error():
    issue = Issue.deserialize(
        {
            "type": "SchemaIssue",
            "identifiers": ["this", "is", "some", "schema", "error", 73],
            "reason": "some reason",
        }
    )
    assert issue == Issue(
        type=IssueType.SCHEMA,
        identifiers=["this", "is", "some", "schema", "error", 73],
        reason="some reason",
    )


def test_issue_deserialize__invalid_reason_type():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        Issue.deserialize(
            {
                "type": "SchemaIssue",
                "identifiers": ["ignore"],
                "reason": ["wait", "that's", "illegal"],
            }
        )


def test_issue_deserialize__invalid_identifiers_type():
    with pytest.raises(jsonschema.exceptions.ValidationError):
        Issue.deserialize(
            {
                "type": "SchemaIssue",
                "identifiers": "A simple string is forbidden",
                "reason": "ignore",
            }
        )


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
