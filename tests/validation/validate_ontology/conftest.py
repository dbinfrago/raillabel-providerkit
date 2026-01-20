# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest


@pytest.fixture
def example_any_attribute_dict():
    return {"attribute_type": "any", "scope": "annotation"}


@pytest.fixture
def example_boolean_attribute_dict():
    return {"attribute_type": "boolean", "scope": "annotation"}


@pytest.fixture
def example_integer_attribute_dict():
    return {"attribute_type": "integer", "scope": "annotation"}


@pytest.fixture
def example_multi_reference_attribute_dict():
    return {"attribute_type": "multi-reference", "scope": "annotation"}


@pytest.fixture
def example_multi_select_attribute_dict():
    return {
        "attribute_type": {"type": "multi-select", "options": ["foo", "bar"]},
        "scope": "annotation",
    }


@pytest.fixture
def example_single_select_attribute_dict():
    return {
        "attribute_type": {"type": "single-select", "options": ["foo", "bar"]},
        "scope": "annotation",
    }


@pytest.fixture
def example_string_attribute_dict():
    return {"attribute_type": "string", "scope": "annotation"}


@pytest.fixture
def example_vector_attribute_dict():
    return {"attribute_type": "vector", "scope": "annotation"}
