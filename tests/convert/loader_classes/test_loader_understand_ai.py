# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel import Scene
from raillabel.json_format import JSONScene

from raillabel_providerkit.convert.loader_classes.loader_understand_ai import LoaderUnderstandAi


# def test_supports__true(json_data):
#     assert LoaderUnderstandAi().supports(json_data["understand_ai_real_life"])


# def test_supports__false(json_data):
#     data = json_data["understand_ai_real_life"]
#     del data["metadata"]["project_id"]
#     assert not LoaderUnderstandAi().supports(data)


# def test_validate_schema__real_life_file__no_errors(json_data):
#     actual = LoaderUnderstandAi().validate_schema(json_data["understand_ai_real_life"])
#     assert actual == []


# def test_validate_schema__real_life_file__errors(json_data):
#     data = json_data["understand_ai_real_life"]
#     del data["coordinateSystems"][0]["topic"]

#     actual = LoaderUnderstandAi().validate_schema(json_data["understand_ai_real_life"])
#     assert len(actual) == 1
#     assert "topic" in actual[0]


# def test_load(json_data):
#     input_data_raillabel = remove_non_parsed_fields(json_data["openlabel_v1_short"])
#     input_data_uai = json_data["understand_ai_t4_short"]

#     scene_ground_truth = Scene.from_json(JSONScene(**input_data_raillabel))
#     scene = LoaderUnderstandAi().load(input_data_uai, validate_schema=False)

#     scene.metadata = scene_ground_truth.metadata
#     assert scene.frames[0].annotations == scene_ground_truth.frames[0].annotations
#     assert scene == scene_ground_truth


# def remove_non_parsed_fields(raillabel_data: dict) -> dict:
#     """Return RailLabel file with frame_data and poly3ds removed."""

#     for frame in raillabel_data["openlabel"]["frames"].values():
#         if "frame_data" in frame["frame_properties"]:
#             del frame["frame_properties"]["frame_data"]

#         for object_id, object in list(frame["objects"].items()):
#             if "poly3d" not in object["object_data"]:
#                 continue

#             del object["object_data"]["poly3d"]
#             if len(object["object_data"]) == 0:
#                 del frame["objects"][object_id]

#     return raillabel_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
