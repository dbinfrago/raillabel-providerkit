# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json

from pydantic_core import ValidationError
from raillabel.json_format import JSONScene

from raillabel_providerkit.validation import Issue, IssueType


def validate_schema(data: dict) -> list[Issue]:
    """Validate a scene for adherence to the raillabel schema.

    Parameters
    ----------
    data : dict
        _description_

    Returns
    -------
    list[Issue]
        List of all schema errors in the scene. If an empty list is returned, then there
        are no errors present
    """
    try:
        JSONScene(**data)
    except ValidationError as errors:
        return _make_errors_readable(errors)
    else:
        return []


def _make_errors_readable(errors: ValidationError) -> list[Issue]:  # noqa: C901
    readable_errors = []
    for error in json.loads(errors.json()):
        match error["type"]:
            case "missing":
                readable_errors.append(_convert_missing_error_to_issue(error))

            case "extra_forbidden":
                readable_errors.append(_convert_unexpected_field_error_to_issue(error))

            case "literal_error":
                readable_errors.append(_convert_literal_error_to_issue(error))

            case "bool_type" | "bool_parsing":
                readable_errors.append(_convert_false_type_error_to_issue(error, "bool"))

            case "int_type" | "int_parsing" | "int_from_float":
                readable_errors.append(_convert_false_type_error_to_issue(error, "int"))

            case "decimal_type" | "decimal_parsing":
                readable_errors.append(_convert_false_type_error_to_issue(error, "Decimal"))

            case "string_type" | "string_parsing":
                readable_errors.append(_convert_false_type_error_to_issue(error, "str"))

            case "float_type" | "float_parsing":
                readable_errors.append(_convert_false_type_error_to_issue(error, "float"))

            case "uuid_type" | "uuid_parsing":
                readable_errors.append(_convert_false_type_error_to_issue(error, "UUID"))

            case "too_long":
                readable_errors.append(_convert_too_long_error_to_issue(error))

            case _:
                readable_errors.append(
                    Issue(type=IssueType.SCHEMA, identifiers=[], reason=str(error))
                )

    return readable_errors


def _build_error_path(loc: list[str]) -> str:
    path = "$"
    for part in loc:
        path += f".{part}"
    return path


def _convert_missing_error_to_issue(error: dict) -> Issue:
    return Issue(
        type=IssueType.SCHEMA,
        identifiers=error["loc"][:-1],
        reason=f"Required field '{error['loc'][-1]}' is missing.",
    )


def _convert_unexpected_field_error_to_issue(error: dict) -> Issue:
    return Issue(
        type=IssueType.SCHEMA,
        identifiers=error["loc"][:-1],
        reason=f"Found unexpected field '{error['loc'][-1]}'.",
    )


def _convert_literal_error_to_issue(error: dict) -> Issue:
    return Issue(
        type=IssueType.SCHEMA,
        identifiers=error["loc"],
        reason=(
            f"Value '{error['input']}' does not match allowed values"
            f" ({error['ctx']['expected']})."
        ),
    )


def _convert_false_type_error_to_issue(error: dict, target_type: str) -> Issue:
    error_path = error["loc"][:-2] if "[key]" in error["loc"] else error["loc"]

    return Issue(
        type=IssueType.SCHEMA,
        identifiers=error_path,
        reason=f"Value '{error['input']}' could not be interpreted as {target_type}.",
    )


def _convert_too_long_error_to_issue(error: dict) -> Issue:
    return Issue(
        type=IssueType.SCHEMA,
        identifiers=error["loc"],
        reason=(
            f"Should have length of {error['ctx']['actual_length']} but has length of "
            f"{error['ctx']['max_length']}."
        ),
    )
