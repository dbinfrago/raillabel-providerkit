# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import os
import sys
from pathlib import Path

import pytest

import raillabel_providerkit


# def test_convert_uai_select_class(json_data):
#     scene = raillabel_providerkit.convert(data=json_data["understand_ai_t4_short"])
#     assert len(scene.frames) != 0


# def test_convert_uai_provide_class(json_data):
#     scene = raillabel_providerkit.convert(
#         data=json_data["understand_ai_t4_short"],
#         loader_class=raillabel_providerkit.loader_classes.LoaderUnderstandAi,
#     )
#     assert len(scene.frames) != 0


# Executes the test if the file is called
if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear"])
