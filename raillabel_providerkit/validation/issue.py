# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from enum import Enum
from typing import Literal
from uuid import UUID

import jsonschema


class IssueType(Enum):
    """General classification of the issue."""

    SCHEMA = "SchemaIssue"
    ATTRIBUTE_MISSING = "AttributeMissing"
    ATTRIBUTE_SCOPE = "AttributeScopeInconsistency"
    ATTRIBUTE_TYPE = "AttributeTypeIssue"
    ATTRIBUTE_UNDEFINED = "AttributeUndefined"
    ATTRIBUTE_VALUE = "AttributeValueIssue"
    DIMENSION_INVALID = "DimensionInvalidIssue"
    EGO_TRACK_BOTH_RAILS = "EgoTrackBothRails"
    EMPTY_FRAMES = "EmptyFramesIssue"
    HORIZON_CROSSED = "HorizonCrossedIssue"
    MISSING_EGO_TRACK = "MissingEgoTrackIssue"
    OBJECT_TYPE_UNDEFINED = "ObjectTypeUndefined"
    RAIL_SIDE = "RailSide"
    SENSOR_ID_UNKNOWN = "SensorIdUnknown"
    SENSOR_TYPE_WRONG = "SensorTypeWrong"
    TRANSITION_IDENTICAL_START_END = "TransitionIdenticalStartAndEnd"
    UNEXPECTED_CLASS = "UnexpectedClassIssue"
    URI_FORMAT = "UriFormatIssue"
    ANNOTATION_SENSOR_MISMATCH = "AnnotationSensorMismatch"

    @classmethod
    def names(cls) -> list[str]:
        """Return the string names of all IssueTypes as a list."""
        return [type_.value for type_ in cls]


@dataclass
class IssueIdentifiers:
    """Information for locating an issue."""

    annotation: UUID | None = None
    annotation_type: Literal["Bbox", "Cuboid", "Num", "Poly2d", "Poly3d", "Seg3d"] | None = None
    attribute: str | None = None
    frame: int | None = None
    object: UUID | None = None
    object_type: str | None = None
    sensor: str | None = None

    def serialize(self) -> dict[str, str | int]:
        """Serialize the IssueIdentifiers into a JSON-compatible dictionary.

        Returns
        -------
        dict[str, str | int]
            The serialized IssueIdentifiers as a JSON-compatible dictionary
        """
        return _clean_dict(
            {
                "annotation": str(self.annotation),
                "annotation_type": self.annotation_type,
                "attribute": self.attribute,
                "frame": self.frame,
                "object": str(self.object),
                "object_type": self.object_type,
                "sensor": self.sensor,
            }
        )

    @classmethod
    def deserialize(cls, serialized_identifiers: dict[str, str | int]) -> "IssueIdentifiers":
        """Deserialize a JSON-compatible dictionary back into an IssueIdentifiers class instance.

        Parameters
        ----------
        serialized_identifiers : dict[str, str  |  int]
            The serialized IssueIdentifiers as a JSON-compatible dictionary

        Returns
        -------
        IssueIdentifiers
            The deserialized IssueIdentifiers class instance

        Raises
        ------
        TypeError
            If any of the fields have an unexpected type
        """
        _verify_identifiers_schema(serialized_identifiers)
        return IssueIdentifiers(
            annotation=UUID(serialized_identifiers.get("annotation"))
            if serialized_identifiers.get("annotation") is not None
            else None,
            annotation_type=serialized_identifiers.get("annotation_type"),
            attribute=serialized_identifiers.get("attribute"),
            frame=serialized_identifiers.get("frame"),
            object=UUID(serialized_identifiers.get("object"))
            if serialized_identifiers.get("object") is not None
            else None,
            object_type=serialized_identifiers.get("object_type"),
            sensor=serialized_identifiers.get("sensor"),
        )


@dataclass
class Issue:
    """An error that was found inside the scene."""

    type: IssueType
    identifiers: IssueIdentifiers | list[str | int]
    reason: str | None = None

    def serialize(self) -> dict[str, str | dict[str, str | int] | list[str | int]]:
        """Serialize the Issue into a JSON-compatible dictionary.

        Returns
        -------
        dict[str, str | dict[str, str | int] | list[str | int]]
            The serialized Issue as a JSON-compatible dictionary
        """
        return _clean_dict(
            {
                "type": str(self.type.value),
                "identifiers": (
                    self.identifiers.serialize()
                    if isinstance(self.identifiers, IssueIdentifiers)
                    else self.identifiers
                ),
                "reason": self.reason,
            }
        )

    @classmethod
    def deserialize(
        cls, serialized_issue: dict[str, str | dict[str, str | int] | list[str | int]]
    ) -> "Issue":
        """Deserialize a JSON-compatible dictionary back into an Issue class instance.

        Parameters
        ----------
        serialized_issue : dict[str, str  |  dict[str, str  |  int]  |  list[str  |  int]]
           The serialized Issue as a JSON-compatible dictionary

        Returns
        -------
        Issue
            The deserialized Issue class instance

        Raises
        ------
        jsonschema.exceptions.ValidationError
            If the serialized data does not match the Issue JSONSchema.
        """
        _verify_issue_schema(serialized_issue)
        return Issue(
            type=IssueType(serialized_issue["type"]),
            identifiers=IssueIdentifiers.deserialize(serialized_issue["identifiers"])
            if not isinstance(serialized_issue["identifiers"], list)
            else serialized_issue["identifiers"],
            reason=serialized_issue.get("reason"),
        )


def _clean_dict(d: dict) -> dict:
    """Remove all fields in a dict that are None or 'None'."""
    return {k: v for k, v in d.items() if str(v) != "None"}


ISSUES_SCHEMA = {
    "type": "array",
    "definitions": {
        "issue": {
            "type": "object",
            "properties": {
                "type": {"enum": IssueType.names()},
                "identifiers": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "annotation": {
                                    "type": "string",
                                    "pattern": "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$",  # noqa: E501
                                },
                                "annotation_type": {
                                    "enum": ["Bbox", "Cuboid", "Num", "Poly2d", "Poly3d", "Seg3d"]
                                },
                                "attribute": {"type": "string"},
                                "frame": {"type": "integer"},
                                "object": {
                                    "type": "string",
                                    "pattern": "^(-?[0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$",  # noqa: E501
                                },
                                "object_type": {"type": "string"},
                                "sensor": {"type": "string"},
                            },
                        },
                        {"type": "array", "items": {"type": ["string", "integer"]}},
                    ]
                },
                "reason": {"type": "string"},
            },
            "required": ["type", "identifiers"],
        },
    },
    "items": {"$ref": "#/definitions/issue"},
}


def _verify_issue_schema(d: dict) -> None:
    jsonschema.validate(d, ISSUES_SCHEMA["definitions"]["issue"])


def _verify_identifiers_schema(d: dict) -> None:
    jsonschema.validate(d, ISSUES_SCHEMA["definitions"]["issue"]["properties"]["identifiers"])
