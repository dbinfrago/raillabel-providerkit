# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from raillabel.scene_builder import SceneBuilder

from raillabel_providerkit.ontologies import detect_ontology


def test_detect_ontology__empty_scene():
    scene = SceneBuilder.empty().result
    assert detect_ontology(scene) is None


def test_detect_ontology__automatedtrain_by_train_front():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="train_front", object_name="train_front_0001")
        .add_bbox(object_name="train_front_0001")
        .result
    )
    assert detect_ontology(scene) == "automatedtrain"


def test_detect_ontology__automatedtrain_by_reflective_test_object():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="reflective_test_object", object_name="rto_0001")
        .add_bbox(object_name="rto_0001")
        .result
    )
    assert detect_ontology(scene) == "automatedtrain"


def test_detect_ontology__osdar23_by_transition():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="transition", object_name="transition_0001")
        .add_bbox(object_name="transition_0001")
        .result
    )
    assert detect_ontology(scene) == "osdar23"


def test_detect_ontology__osdar26_by_ignore_tracks_and_wagon():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="ignore_tracks", object_name="ignore_tracks_0001")
        .add_object(object_type="wagon", object_name="wagon_0001")
        .add_bbox(object_name="ignore_tracks_0001")
        .add_bbox(object_name="wagon_0001")
        .result
    )
    assert detect_ontology(scene) == "osdar26"


def test_detect_ontology__osdar26_by_wagon_singular():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="wagon", object_name="wagon_0001")
        .add_bbox(object_name="wagon_0001")
        .result
    )
    assert detect_ontology(scene) == "osdar26"


def test_detect_ontology__automatedtrain_by_wagons_plus_scooter():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="wagons", object_name="wagons_0001")
        .add_object(object_type="scooter", object_name="scooter_0001")
        .add_bbox(object_name="wagons_0001")
        .add_bbox(object_name="scooter_0001")
        .result
    )
    assert detect_ontology(scene) == "automatedtrain"


def test_detect_ontology__osdar23_by_wagons_without_exclusive():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="wagons", object_name="wagons_0001")
        .add_object(object_type="person", object_name="person_0001")
        .add_bbox(object_name="wagons_0001")
        .add_bbox(object_name="person_0001")
        .result
    )
    assert detect_ontology(scene) == "osdar23"


def test_detect_ontology__fallback_to_automatedtrain():
    scene = (
        SceneBuilder.empty()
        .add_object(object_type="person", object_name="person_0001")
        .add_bbox(object_name="person_0001")
        .result
    )
    assert detect_ontology(scene) == "automatedtrain"
