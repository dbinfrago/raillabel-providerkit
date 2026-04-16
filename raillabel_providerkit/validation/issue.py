# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, cast
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
        annotation_raw = serialized_identifiers.get("annotation")
        object_raw = serialized_identifiers.get("object")
        return IssueIdentifiers(
            annotation=UUID(str(annotation_raw)) if annotation_raw is not None else None,
            annotation_type=cast(
                Literal["Bbox", "Cuboid", "Num", "Poly2d", "Poly3d", "Seg3d"] | None,
                serialized_identifiers.get("annotation_type"),
            ),
            attribute=cast(str | None, serialized_identifiers.get("attribute")),
            frame=cast(int | None, serialized_identifiers.get("frame")),
            object=UUID(str(object_raw)) if object_raw is not None else None,
            object_type=cast(str | None, serialized_identifiers.get("object_type")),
            sensor=cast(str | None, serialized_identifiers.get("sensor")),
        )


@dataclass
class Issue:
    """An error that was found inside the scene."""

    type: IssueType
    identifiers: IssueIdentifiers | list[str | int]
    reason: str | None = None
    fixable: bool = False
    suggested_value: str | None = None

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
                "fixable": self.fixable if self.fixable else None,
                "suggested_value": self.suggested_value,
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
        identifiers = serialized_issue["identifiers"]
        return Issue(
            type=IssueType(serialized_issue["type"]),
            identifiers=IssueIdentifiers.deserialize(cast(dict[str, str | int], identifiers))
            if not isinstance(identifiers, list)
            else identifiers,
            reason=cast(str | None, serialized_issue.get("reason")),
            fixable=cast(bool, serialized_issue.get("fixable", False)),
            suggested_value=cast(str | None, serialized_issue.get("suggested_value")),
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
                "fixable": {"type": "boolean"},
                "suggested_value": {"type": "string"},
            },
            "required": ["type", "identifiers"],
        },
    },
    "items": {"$ref": "#/definitions/issue"},
}


def _verify_issue_schema(d: dict) -> None:
    schema = cast(dict[str, Any], ISSUES_SCHEMA["definitions"])
    jsonschema.validate(d, schema["issue"])


def _verify_identifiers_schema(d: dict) -> None:
    schema = cast(dict[str, Any], ISSUES_SCHEMA["definitions"])
    jsonschema.validate(d, schema["issue"]["properties"]["identifiers"])
