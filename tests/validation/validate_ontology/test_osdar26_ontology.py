# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Tests for the OSDAR26 ontology file."""

import pytest
from pathlib import Path
import yaml
import jsonschema

# Path to the OSDAR26 ontology file
OSDAR26_ONTOLOGY_PATH = Path(__file__).parent.parent.parent / "__assets__" / "osdar26_ontology.yaml"

# Path to the ontology schema
ONTOLOGY_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "raillabel_providerkit"
    / "validation"
    / "validate_ontology"
    / "ontology_schema_v2.yaml"
)


def _load_ontology(ontology_path: Path) -> dict:
    """Load and return the ontology as a dictionary."""
    with ontology_path.open("r") as f:
        return yaml.safe_load(f)


def _load_schema(schema_path: Path) -> dict:
    """Load and return the schema as a dictionary."""
    with schema_path.open("r") as f:
        return yaml.safe_load(f)


class TestOsdar26OntologySchema:
    """Tests for validating the OSDAR26 ontology against the schema."""

    def test_ontology_file_exists(self):
        assert OSDAR26_ONTOLOGY_PATH.exists()

    def test_ontology_valid_yaml(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        assert ontology_dict is not None
        assert isinstance(ontology_dict, dict)

    def test_ontology_conforms_to_schema(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        schema_dict = _load_schema(ONTOLOGY_SCHEMA_PATH)
        # This will raise ValidationError if the ontology doesn't conform
        jsonschema.validate(instance=ontology_dict, schema=schema_dict)


class TestOsdar26ExpectedClasses:
    """Tests to ensure all expected OSDAR26 classes are present."""

    def test_all_expected_classes_present(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        expected_classes = {
            "person",
            "crowd",
            "personal_item",
            "pram",
            "scooter",
            "bicycle",
            "group_of_bicycles",
            "motorcycle",
            "road_vehicle",
            "animal",
            "group_of_animals",
            "wheelchair",
            "train",
            "wagon",
            "drag_shoe",
            "track",
            "transition",
            "switch",
            "catenary_pole",
            "signal_pole",
            "signal",
            "signal_bridge",
            "buffer_stop",
            "flame",
            "smoke",
        }
        assert set(ontology_dict.keys()) == expected_classes


class TestOsdar26OcclusionFormat:
    """Tests for OSDAR26 specific occlusion value format."""

    def test_occlusion_values_are_percentage_ranges(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        expected_occlusion_options = ["0-24 %", "25-49 %", "50-74 %", "75-99 %", "100 %"]

        # Check a few classes with occlusion
        classes_with_occlusion = ["person", "bicycle", "signal", "train", "flame"]
        for cls in classes_with_occlusion:
            assert cls in ontology_dict
            assert "occlusion" in ontology_dict[cls]
            occlusion_opts = ontology_dict[cls]["occlusion"]["attribute_type"]["options"]
            assert occlusion_opts == expected_occlusion_options


class TestOsdar26SignalAspects:
    """Tests for OSDAR26 signal aspect options."""

    def test_signal_aspect_options_present(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        assert "signal" in ontology_dict
        assert "signalAspect" in ontology_dict["signal"]

        signal_aspects = ontology_dict["signal"]["signalAspect"]["attribute_type"]["options"]

        # Check for specific signal aspects
        expected_aspects = [
            "Hp_0_light",
            "Hp_0_shape",
            "Hp_1_light",
            "Hp_1_shape",
            "Hp_2_light",
            "Hp_2_shape",
            "Ks_1",
            "Ks_2",
            "Vr_0_light",
            "Vr_0_shape",
            "Vr_1_light",
            "Vr_1_shape",
            "Vr_2_light",
            "Vr_2_shape",
            "Zs_2",
            "Zs_2v",
            "Zs_3_light",
            "Zs_3_shape",
            "Zs_3v_light",
            "Zs_3v_shape",
            "Sh_0_light",
            "Sh_0_shape",
            "Sh_1_light",
            "Sh_1_shape",
            "Sh_2_shape",
            "other_light",
            "other_shape",
            "invalid",
            "unknown",
        ]

        for aspect in expected_aspects:
            assert aspect in signal_aspects


class TestOsdar26PersonalItemAndPram:
    """Tests for personal_item, pram, and scooter classes."""

    def test_personal_item_type_options(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        assert "personal_item" in ontology_dict
        opts = ontology_dict["personal_item"]["type"]["attribute_type"]["options"]
        for opt in ["suitcase", "backpack", "handbag", "bag", "umbrella", "case"]:
            assert opt in opts

    def test_pram_type_options(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        assert "pram" in ontology_dict
        opts = ontology_dict["pram"]["type"]["attribute_type"]["options"]
        for opt in ["stroller", "buggy", "babySeat"]:
            assert opt in opts

    def test_scooter_type_options(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        assert "scooter" in ontology_dict
        opts = ontology_dict["scooter"]["type"]["attribute_type"]["options"]
        for opt in ["eScooter", "scooter", "hoverboard"]:
            assert opt in opts


class TestOsdar26AnimalSpecies:
    """Tests for animal species options."""

    def test_animal_species_comprehensive(self):
        ontology_dict = _load_ontology(OSDAR26_ONTOLOGY_PATH)
        assert "animal" in ontology_dict
        species_opts = ontology_dict["animal"]["species"]["attribute_type"]["options"]

        expected_species = [
            "dog",
            "cat",
            "racoon",
            "badger",
            "swan",
            "sheep",
            "cow",
            "horse",
            "pig",
            "fox",
            "wolf",
            "wildBoar",
            "deer",
            "stork",
            "rabbit",
            "bird",
        ]

        for species in expected_species:
            assert species in species_opts
