# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from pathlib import Path
from uuid import UUID

from raillabel_providerkit.validation.validate_ontology.validate_ontology import (
    validate_ontology,
    _load_ontology,
)
from raillabel_providerkit.validation import IssueType
from raillabel.scene_builder import SceneBuilder
from raillabel.format import Point2d, Size2d

ONTOLOGY_PATH = Path(__file__).parent.parent.parent / "__assets__/osdar23_ontology.yaml"


@pytest.fixture
def example_ontology_dict() -> dict:
    return {"banana": {"is_peelable": {"attribute_type": "boolean", "scope": "annotation"}}}


def test_validate_ontology__empty_scene(example_ontology_dict):
    scene = SceneBuilder.empty().result
    issues = validate_ontology(scene, example_ontology_dict)
    assert issues == []


def test_validate_ontology__correct(example_ontology_dict):
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="banana",
            object_name="banana_0001",
        )
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_center",
            attributes={"is_peelable": True},
        )
        .result
    )
    issues = validate_ontology(scene, example_ontology_dict)
    assert issues == []


def test_validate_ontology__invalid_attribute_type(example_ontology_dict):
    scene = (
        SceneBuilder.empty()
        .add_object(
            object_id=UUID("ba73e75d-b996-4f6e-bdad-39c465420a33"),
            object_type="banana",
            object_name="banana_0001",
        )
        .add_bbox(
            UUID("f54d41d6-5e36-490b-9efc-05a6deb7549a"),
            pos=Point2d(0, 0),
            size=Size2d(1, 1),
            frame_id=0,
            object_name="banana_0001",
            sensor_id="rgb_center",
            attributes={"is_peelable": "i-like-trains"},
        )
        .result
    )
    issues = validate_ontology(scene, example_ontology_dict)
    assert len(issues) == 1
    assert issues[0].type == IssueType.ATTRIBUTE_TYPE


def test_load_ontology__invalid_path():
    invalid_path = Path("/this/should/point/nowhere")
    with pytest.raises(FileNotFoundError):
        _load_ontology(invalid_path)


def test_load_ontology__osdar23():
    ontology_dict = _load_ontology(ONTOLOGY_PATH)
    assert isinstance(ontology_dict, dict)


def test_unexpected_class(example_ontology_dict):
    scene = SceneBuilder.empty().add_bbox(object_name="apple_0001").result

    validate_ontology(scene, example_ontology_dict)


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
