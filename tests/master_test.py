# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import os
import pathlib

import pytest

# Executes the test
os.system("clear")
pytest.main(
    [
        str(pathlib.Path(__file__).parent),
        "--disable-pytest-warnings",
        "--cache-clear",
    ]
)
