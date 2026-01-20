# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest

from raillabel_providerkit.validation import validate_schema, Issue, IssueType


def test_no_errors__empty():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0"}}}

    actual = validate_schema(data)
    assert actual == []


def test_required_field_missing():
    data: dict = {"openlabel": {"metadata": {}}}

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=["openlabel", "metadata"],
            reason="Required field 'schema_version' is missing.",
        )
    ]


def test_unsupported_field():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0"}, "UNSUPPORTED_FIELD": {}}}

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=["openlabel"],
            reason="Found unexpected field 'UNSUPPORTED_FIELD'.",
        )
    ]


def test_unexpected_value():
    data = {"openlabel": {"metadata": {"schema_version": "SOMETHING UNSUPPORTED"}}}

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=["openlabel", "metadata", "schema_version"],
            reason="Value 'SOMETHING UNSUPPORTED' does not match allowed values ('1.0.0').",
        )
    ]


def test_wrong_type_bool():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "frames": {
                "1": {
                    "objects": {
                        "113c2b35-0965-4c80-a212-08b262e94203": {
                            "object_data": {
                                "poly2d": [
                                    {
                                        "closed": "NOT A BOOLEAN",
                                        "name": "not_important",
                                        "val": [],
                                        "mode": "MODE_POLY2D_ABSOLUTE",
                                        "coordinate_system": "not_important",
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        }
    }

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=[
                "openlabel",
                "frames",
                "1",
                "objects",
                "113c2b35-0965-4c80-a212-08b262e94203",
                "object_data",
                "poly2d",
                0,
                "closed",
            ],
            reason="Value 'NOT A BOOLEAN' could not be interpreted as bool.",
        )
    ]


def test_wrong_type_int():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0"}, "frames": {"NOT AN INT": {}}}}

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=[
                "openlabel",
                "frames",
            ],
            reason="Value 'NOT AN INT' could not be interpreted as int.",
        )
    ]


def test_wrong_type_string():
    data = {"openlabel": {"metadata": {"schema_version": "1.0.0", "comment": False}}}

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=[
                "openlabel",
                "metadata",
                "comment",
            ],
            reason="Value 'False' could not be interpreted as str.",
        )
    ]


def test_wrong_type_float():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "coordinate_systems": {
                "rgb_center": {
                    "pose_wrt_parent": {
                        "translation": (None, 0.0, 0.0),
                        "quaternion": (0.0, 0.0, 0.0, 0.0),
                    },
                    "parent": "",
                    "type": "sensor",
                }
            },
        }
    }

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=[
                "openlabel",
                "coordinate_systems",
                "rgb_center",
                "pose_wrt_parent",
                "translation",
                0,
            ],
            reason="Value 'None' could not be interpreted as float.",
        )
    ]


def test_wrong_type_uuid():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "objects": {
                "NOT A VALID UUID": {
                    "name": "person_0001",
                    "type": "person",
                }
            },
        }
    }

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=[
                "openlabel",
                "objects",
            ],
            reason="Value 'NOT A VALID UUID' could not be interpreted as UUID.",
        )
    ]


def test_tuple_too_long():
    data = {
        "openlabel": {
            "metadata": {"schema_version": "1.0.0"},
            "coordinate_systems": {
                "rgb_center": {
                    "pose_wrt_parent": {
                        "translation": (0.0, 0.0, 0.0, 0.0),  # should have length of 3
                        "quaternion": (0.0, 0.0, 0.0, 0.0),
                    },
                    "parent": "",
                    "type": "sensor",
                }
            },
        }
    }

    actual = validate_schema(data)
    assert actual == [
        Issue(
            type=IssueType.SCHEMA,
            identifiers=[
                "openlabel",
                "coordinate_systems",
                "rgb_center",
                "pose_wrt_parent",
                "translation",
            ],
            reason="Should have length of 4 but has length of 3.",
        )
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
