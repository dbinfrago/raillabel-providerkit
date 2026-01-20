# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from raillabel import Scene
from raillabel.json_format import JSONScene

from raillabel_providerkit.format import understand_ai as uai_format

from ._loader_abc import LoaderABC


class LoaderUnderstandAi(LoaderABC):
    """Loader class for the Understand.Ai Trains4 annotation format.

    Attributes
    ----------
    scene: raillabel.format.understand_ai.Scene
        Loaded raillabel.format.understand_ai.Scene with the data.
    warnings: t.List[str]
        List of warning strings, that have been found during the execution of load().

    """

    scene: uai_format.Scene
    warnings: list[str]

    SCHEMA_PATH: Path = (
        Path(__file__).parent.parent.parent / "format" / "understand_ai_t4_schema.json"
    )

    def load(self, data: dict, validate_schema: bool = False) -> uai_format.Scene:
        """Load the data into a UAIScene and return it.

        Parameters
        ----------
        data: dict
            A dictionary loaded from a JSON-file.
        validate_schema: bool
            If True, the annotation data is validated via the respective schema. This is highly
            recommended, as not validating the data may lead to Errors during loading or while
            handling the scene. However, validating may increase the loading time. Default is False.

        Returns
        -------
        scene: raillabel.format.understand_ai.UAIScene
            The loaded scene with the data.

        """
        raise NotImplementedError(
            "We were not sure if this class is even used anymore. If you see this error, contact us "  # noqa: EM101
            "and we will re-implement the class."
        )

        if validate_schema:
            self.validate_schema(data)

        data_converted_to_raillabel = uai_format.Scene.fromdict(data).to_raillabel()

        return Scene.from_json(JSONScene(**data_converted_to_raillabel))

    def supports(self, data: dict) -> bool:
        """Determine if the loader is suitable for the data (lightweight).

        Parameters
        ----------
        data: dict
            A dictionary loaded from a JSON-file.

        Returns
        -------
        bool:
            If True, the Loader class is suitable for the data.

        """
        return (
            "metadata" in data
            and "project_id" in data["metadata"]
            and "coordinateSystems" in data
            and "frames" in data
        )

    def validate_schema(self, data: dict) -> list[str]:
        """Check if the schema is correct."""
        with self.SCHEMA_PATH.open() as file:
            schema = json.load(file)

        validator = jsonschema.Draft7Validator(schema=schema)
        return [
            "$" + error.json_path[1:] + ": " + str(error.message)
            for error in validator.iter_errors(data)
        ]
