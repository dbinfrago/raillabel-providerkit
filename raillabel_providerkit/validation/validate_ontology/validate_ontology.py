# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

import jsonschema
import raillabel
import yaml

from raillabel_providerkit.exceptions import OntologySchemaError
from raillabel_providerkit.validation import Issue

from ._ontology_classes import _Ontology


def validate_ontology(scene: raillabel.Scene, ontology_input: dict | Path) -> list[Issue]:
    """Validate a scene based on the classes and attributes.

    Parameters
    ----------
    scene : raillabel.Scene
        The scene containing the annotations.
    ontology_input : dict or Path
        Ontology YAML-data or file containing a information about all classes and their
        attributes. The ontology must adhere to the ontology_schema. If a path is provided, the
        file is loaded as a YAML.

    Returns
    -------
    list[Issue]
        List of all ontology errors in the scene. If an empty list is returned, then there are no
        errors present.

    """
    if isinstance(ontology_input, Path):
        ontology_input = _load_ontology(Path(ontology_input))

    _validate_ontology_schema(ontology_input)

    ontology = _Ontology.fromdict(ontology_input)

    return ontology.check(scene)


def _load_ontology(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def _validate_ontology_schema(ontology: dict) -> None:
    schema_path = Path(__file__).parent / "ontology_schema_v2.yaml"

    with schema_path.open() as f:
        ontology_schema = yaml.safe_load(f)

    validator = jsonschema.Draft7Validator(schema=ontology_schema)

    schema_errors = ""
    for error in validator.iter_errors(ontology):
        schema_errors += f"${error.json_path[1:]}: {error.message}\n"

    if schema_errors != "":
        raise OntologySchemaError(
            "The provided ontology is not valid. The following errors have been found:\n"
            + schema_errors
        )
