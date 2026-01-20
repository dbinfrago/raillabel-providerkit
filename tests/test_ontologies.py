# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Tests for the ontologies manager module."""

from pathlib import Path

import pytest

from raillabel_providerkit.ontologies import get_ontology_path, list_available_ontologies


class TestListAvailableOntologies:
    """Tests for list_available_ontologies function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        result = list_available_ontologies()
        assert isinstance(result, list)

    def test_returns_expected_ontologies(self):
        """Test that all expected ontologies are present."""
        result = list_available_ontologies()
        assert "osdar26" in result
        assert "automatedtrain" in result
        assert "osdar23" in result

    def test_returns_correct_count(self):
        """Test that exactly 3 ontologies are available."""
        result = list_available_ontologies()
        assert len(result) == 3


class TestGetOntologyPath:
    """Tests for get_ontology_path function."""

    def test_osdar26_path(self):
        """Test that OSDAR26 ontology path is correct."""
        path = get_ontology_path("osdar26")
        assert isinstance(path, Path)
        assert path.name == "osdar26.yaml"
        assert path.exists()

    def test_automatedtrain_path(self):
        """Test that AutomatedTrain ontology path is correct."""
        path = get_ontology_path("automatedtrain")
        assert isinstance(path, Path)
        assert path.name == "automatedtrain.yaml"
        assert path.exists()

    def test_osdar23_path(self):
        """Test that OSDAR23 ontology path is correct."""
        path = get_ontology_path("osdar23")
        assert isinstance(path, Path)
        assert path.name == "osdar23.yaml"
        assert path.exists()

    def test_invalid_ontology_raises_error(self):
        """Test that invalid ontology name raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            get_ontology_path("nonexistent_ontology")
        assert "Unknown ontology" in str(excinfo.value)
        assert "nonexistent_ontology" in str(excinfo.value)

    def test_path_contains_ontologies_directory(self):
        """Test that returned path is in the ontologies directory."""
        path = get_ontology_path("osdar26")
        assert "ontologies" in str(path)

    def test_all_ontologies_accessible(self):
        """Test that all listed ontologies can be accessed."""
        for ontology in list_available_ontologies():
            path = get_ontology_path(ontology)
            assert path.exists()
            assert path.is_file()


class TestOntologyContent:
    """Tests for ontology file content and validity."""

    def test_osdar26_valid_yaml(self):
        """Test that OSDAR26 ontology is valid YAML."""
        import yaml

        path = get_ontology_path("osdar26")
        with path.open() as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_osdar26_has_expected_classes(self):
        """Test that OSDAR26 has expected classes."""
        import yaml

        path = get_ontology_path("osdar26")
        with path.open() as f:
            data = yaml.safe_load(f)

        # Check for some key classes
        expected_classes = [
            "person",
            "crowd",
            "track",
            "signal",
            "train",
            "wagon",
            "animal",
        ]
        for cls in expected_classes:
            assert cls in data, f"Expected class {cls} not found in ontology"

    def test_automatedtrain_valid_yaml(self):
        """Test that AutomatedTrain ontology is valid YAML."""
        import yaml

        path = get_ontology_path("automatedtrain")
        with path.open() as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_automatedtrain_has_safety_critical_classes(self):
        """Test that AutomatedTrain has safety-critical classes."""
        import yaml

        path = get_ontology_path("automatedtrain")
        with path.open() as f:
            data = yaml.safe_load(f)

        # Check for safety-critical classes
        safety_classes = ["obstacle", "platform", "level_crossing", "speed_sign"]
        for cls in safety_classes:
            assert cls in data, f"Expected safety class {cls} not found"

    def test_osdar23_valid_yaml(self):
        """Test that OSDAR23 ontology is valid YAML."""
        import yaml

        path = get_ontology_path("osdar23")
        with path.open() as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)
        assert len(data) > 0


class TestOntologyIntegration:
    """Integration tests for ontology usage with validation."""

    def test_ontology_can_be_used_with_validate(self):
        """Test that ontology can be loaded by validation system."""
        from raillabel_providerkit.validation.validate_ontology.validate_ontology import (
            _validate_ontology_schema,
        )

        import yaml

        for ontology_name in list_available_ontologies():
            path = get_ontology_path(ontology_name)
            with path.open() as f:
                ontology_data = yaml.safe_load(f)

            # Should not raise any exceptions
            _validate_ontology_schema(ontology_data)
