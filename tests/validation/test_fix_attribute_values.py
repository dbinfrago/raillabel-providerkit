# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import copy
import json

import pytest

from raillabel_providerkit.validation.fix_attribute_values import fix_attribute_values


@pytest.fixture
def ontology_with_options():
    return {
        "classes": {
            "person": {
                "attributes": {
                    "occlusion": {
                        "attribute_type": {
                            "type": "single-select",
                            "options": ["0-25%", "25-50%", "50-75%", "75-100%", "undefined"],
                        }
                    },
                    "tags": {
                        "attribute_type": {
                            "type": "multi-select",
                            "options": ["standing", "walking", "sitting"],
                        }
                    },
                    "name": {
                        "attribute_type": "string",
                    },
                }
            }
        }
    }


@pytest.fixture
def scene_with_whitespace_issue():
    return {
        "openlabel": {
            "frames": {
                "0": {
                    "objects": {
                        "obj-1": {
                            "object_data": {
                                "bbox": [
                                    {
                                        "uid": "ann-1",
                                        "name": "rgb_center__bbox__person",
                                        "val": [0, 0, 1, 1],
                                        "coordinate_system": "rgb_center",
                                        "attributes": {
                                            "text": [
                                                {
                                                    "name": "occlusion",
                                                    "val": "0-25 %",
                                                }
                                            ],
                                        },
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def scene_with_correct_values():
    return {
        "openlabel": {
            "frames": {
                "0": {
                    "objects": {
                        "obj-1": {
                            "object_data": {
                                "bbox": [
                                    {
                                        "uid": "ann-1",
                                        "name": "rgb_center__bbox__person",
                                        "val": [0, 0, 1, 1],
                                        "coordinate_system": "rgb_center",
                                        "attributes": {
                                            "text": [
                                                {
                                                    "name": "occlusion",
                                                    "val": "0-25%",
                                                }
                                            ],
                                        },
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }


class TestFixAttributeValues:
    def test_fixes_whitespace_mismatch(self, scene_with_whitespace_issue, ontology_with_options):
        fixed, fixes = fix_attribute_values(scene_with_whitespace_issue, ontology_with_options)

        assert len(fixes) == 1
        assert "'0-25 %' -> '0-25%'" in fixes[0]

        # Check the fixed value
        bbox = fixed["openlabel"]["frames"]["0"]["objects"]["obj-1"]["object_data"]["bbox"][0]
        assert bbox["attributes"]["text"][0]["val"] == "0-25%"

    def test_no_fix_needed(self, scene_with_correct_values, ontology_with_options):
        fixed, fixes = fix_attribute_values(scene_with_correct_values, ontology_with_options)

        assert len(fixes) == 0

    def test_does_not_modify_original(self, scene_with_whitespace_issue, ontology_with_options):
        original = copy.deepcopy(scene_with_whitespace_issue)
        fix_attribute_values(scene_with_whitespace_issue, ontology_with_options)

        assert scene_with_whitespace_issue == original

    def test_fixes_multi_select_whitespace(self, ontology_with_options):
        scene = {
            "openlabel": {
                "frames": {
                    "0": {
                        "objects": {
                            "obj-1": {
                                "object_data": {
                                    "bbox": [
                                        {
                                            "uid": "ann-1",
                                            "name": "rgb_center__bbox__person",
                                            "val": [0, 0, 1, 1],
                                            "coordinate_system": "rgb_center",
                                            "attributes": {
                                                "vec": [
                                                    {
                                                        "name": "tags",
                                                        "val": ["stand ing", "walking"],
                                                    }
                                                ],
                                            },
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
        fixed, fixes = fix_attribute_values(scene, ontology_with_options)

        assert len(fixes) == 1
        assert "'stand ing' -> 'standing'" in fixes[0]

    def test_empty_ontology(self, scene_with_whitespace_issue):
        fixed, fixes = fix_attribute_values(scene_with_whitespace_issue, {"classes": {}})
        assert len(fixes) == 0

    def test_ontology_from_path(self, scene_with_whitespace_issue, tmp_path, ontology_with_options):
        import yaml  # type: ignore[import-untyped]

        ontology_path = tmp_path / "ontology.yaml"
        with ontology_path.open("w") as f:
            yaml.dump(ontology_with_options, f)

        fixed, fixes = fix_attribute_values(scene_with_whitespace_issue, ontology_path)
        assert len(fixes) == 1
