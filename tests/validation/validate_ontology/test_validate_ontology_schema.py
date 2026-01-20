# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from pathlib import Path

import yaml

from raillabel_providerkit.validation.validate_ontology.validate_ontology import (
    _validate_ontology_schema,
    OntologySchemaError,
)

ONTOLOGY_PATH = Path(__file__).parent.parent.parent / "__assets__/osdar23_ontology.yaml"


def test_osdar23_valid():
    with ONTOLOGY_PATH.open() as f:
        osdar23_ontology = yaml.load(f, yaml.SafeLoader)
    _validate_ontology_schema(osdar23_ontology)


def test_empty_class_valid():
    ontology = {"person": {}}
    _validate_ontology_schema(ontology)


def test_valid_attribute_types():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "any"},
            "isPeelable": {"attribute_type": "boolean"},
            "numberOfFingers": {"attribute_type": "integer"},
            "holdsHandsWith": {"attribute_type": "multi-reference"},
            "carries": {"attribute_type": {"type": "multi-select", "options": ["foo", "bar"]}},
            "carriesOnBack": {
                "attribute_type": {"type": "single-select", "options": ["foo", "bar"]}
            },
            "firstName": {"attribute_type": "string"},
            "carriesWildcard": {"attribute_type": "vector"},
        }
    }
    _validate_ontology_schema(ontology)


def test_valid_attribute_types():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "unknown"},
        }
    }
    with pytest.raises(OntologySchemaError):
        _validate_ontology_schema(ontology)


def test_optional_field_valid():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "any", "optional": True},
            "isPeelable": {"attribute_type": "boolean", "optional": False},
        }
    }
    _validate_ontology_schema(ontology)


def test_optional_field_invalid_type():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "any", "optional": "no"},
        }
    }
    with pytest.raises(OntologySchemaError):
        _validate_ontology_schema(ontology)


def test_scope_field_valid():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "any", "scope": "annotation"},
            "isPeelable": {"attribute_type": "boolean", "scope": "frame"},
            "numberOfFingers": {"attribute_type": "integer", "scope": "object"},
        }
    }
    _validate_ontology_schema(ontology)


def test_scope_field_invalid_value():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "any", "scope": "scene"},
        }
    }
    with pytest.raises(OntologySchemaError):
        _validate_ontology_schema(ontology)


def test_sensor_types_field_valid():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "any", "sensor_types": ["camera", "lidar", "radar"]},
        }
    }
    _validate_ontology_schema(ontology)


def test_sensor_types_field_invalid_value():
    ontology = {
        "person": {
            "wildcard": {"attribute_type": "any", "sensor_types": ["gps_imu"]},
        }
    }
    with pytest.raises(OntologySchemaError):
        _validate_ontology_schema(ontology)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
