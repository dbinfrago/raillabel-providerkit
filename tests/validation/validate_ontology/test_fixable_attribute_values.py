# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest

from raillabel_providerkit.validation.validate_ontology._ontology_classes import (
    _Scope,
    _SingleSelectAttribute,
    _MultiSelectAttribute,
)
from raillabel_providerkit.validation import IssueIdentifiers, IssueType


class TestSingleSelectFixable:
    def test_whitespace_mismatch_is_fixable(self):
        attr = _SingleSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"0-25%", "25-50%", "50-75%", "75-100%", "undefined"},
        )
        errors = attr.check_type_and_value("occlusion", "0-25 %", IssueIdentifiers())
        assert len(errors) == 1
        assert errors[0].type == IssueType.ATTRIBUTE_VALUE
        assert errors[0].fixable is True
        assert errors[0].suggested_value == "0-25%"
        assert errors[0].reason is not None and "[FIXABLE]" in errors[0].reason

    def test_no_whitespace_mismatch_not_fixable(self):
        attr = _SingleSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"0-25%", "25-50%", "50-75%", "75-100%", "undefined"},
        )
        errors = attr.check_type_and_value("occlusion", "completely_wrong", IssueIdentifiers())
        assert len(errors) == 1
        assert errors[0].type == IssueType.ATTRIBUTE_VALUE
        assert errors[0].fixable is False
        assert errors[0].suggested_value is None

    def test_exact_match_no_issue(self):
        attr = _SingleSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"0-25%", "25-50%"},
        )
        errors = attr.check_type_and_value("occlusion", "0-25%", IssueIdentifiers())
        assert errors == []

    def test_leading_trailing_whitespace_is_fixable(self):
        attr = _SingleSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"hello-world"},
        )
        errors = attr.check_type_and_value("test", " hello-world ", IssueIdentifiers())
        assert len(errors) == 1
        assert errors[0].fixable is True
        assert errors[0].suggested_value == "hello-world"

    def test_multiple_spaces_is_fixable(self):
        attr = _SingleSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"50-75%"},
        )
        errors = attr.check_type_and_value("occlusion", "50 - 75 %", IssueIdentifiers())
        assert len(errors) == 1
        assert errors[0].fixable is True
        assert errors[0].suggested_value == "50-75%"


class TestMultiSelectFixable:
    def test_whitespace_mismatch_is_fixable(self):
        attr = _MultiSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"0-25%", "25-50%", "50-75%"},
        )
        errors = attr.check_type_and_value("occlusion", ["0-25 %"], IssueIdentifiers())
        assert len(errors) == 1
        assert errors[0].type == IssueType.ATTRIBUTE_VALUE
        assert errors[0].fixable is True
        assert errors[0].suggested_value == "0-25%"

    def test_no_whitespace_mismatch_not_fixable(self):
        attr = _MultiSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"0-25%", "25-50%"},
        )
        errors = attr.check_type_and_value("occlusion", ["totally_wrong"], IssueIdentifiers())
        assert len(errors) == 1
        assert errors[0].fixable is False

    def test_single_string_whitespace_mismatch_is_fixable(self):
        """Test backwards compat: single string input for multi-select."""
        attr = _MultiSelectAttribute(
            optional=False,
            scope=_Scope.ANNOTATION,
            sensor_types=["camera"],
            options={"0-25%", "25-50%"},
        )
        errors = attr.check_type_and_value("occlusion", "0-25 %", IssueIdentifiers())
        assert len(errors) == 1
        assert errors[0].fixable is True
        assert errors[0].suggested_value == "0-25%"
