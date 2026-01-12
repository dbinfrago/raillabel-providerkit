# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import csv
import json
from pathlib import Path

import click
import jsonschema
from tqdm import tqdm

from raillabel_providerkit import validate
from raillabel_providerkit.validation.issue import ISSUES_SCHEMA, Issue


def store_issues_to_json(issues: list[Issue], filepath: Path) -> None:
    """Store the given issues in a .json file under the given filepath.

    Parameters
    ----------
    issues : list[Issue]
        The issues to store
    filepath : Path
        The path to the .json file to store the issues in
    """
    issues_serialized = [issue.serialize() for issue in issues]
    if not _adheres_to_issues_schema(issues_serialized):
        raise AssertionError
    issues_json = json.dumps(issues_serialized, indent=2)
    with Path.open(filepath, "w") as file:
        file.write(issues_json)


def _adheres_to_issues_schema(
    data: list[dict[str, str | dict[str, str | int] | list[str | int]]],
) -> bool:
    try:
        jsonschema.validate(data, ISSUES_SCHEMA)
    except jsonschema.ValidationError:
        return False

    return True


def store_issues_to_csv(issues: list[Issue], filepath: Path) -> None:
    """Store the given issues in a .csv file under the given filepath.

    Parameters
    ----------
    issues : list[Issue]
        The issues to store
    filepath : Path
        The path to the .csv file to store the issues in

    Raises
    ------
    TypeError
        If the issues are malformed after serialization
    """
    issues_serialized = [issue.serialize() for issue in issues]

    file = Path.open(filepath, "w")

    writer = csv.writer(file, dialect="excel-tab")
    writer.writerow(
        [
            "issue_type",
            "frame",
            "sensor",
            "object_type",
            "object",
            "annotation",
            "attribute",
            "schema_path",
            "reason",
        ]
    )

    for issue in issues_serialized:
        issue_type = issue["type"]
        reason = issue.get("reason", "")
        if not isinstance(issue_type, str) or not isinstance(reason, str):
            raise TypeError

        row: list[str | int] = []
        row.append(issue_type)
        identifiers = issue["identifiers"]
        if isinstance(identifiers, dict):
            row.append(identifiers.get("frame", ""))
            row.append(identifiers.get("sensor", ""))
            row.append(identifiers.get("object_type", ""))
            row.append(identifiers.get("object", ""))
            row.append(identifiers.get("annotation", ""))
            row.append(identifiers.get("attribute", ""))
            row.append("")
        else:
            # It's a schema issue, so there are no standard identifiers
            row.extend(["", "", "", "", "", ""])
            row.append(str(identifiers))
        row.append(reason)

        writer.writerow(row)

    file.close()


@click.command()
@click.argument(
    "annotations_folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument(
    "output_folder",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--ontology",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help=(
        "The path to the ontology against which to validate attributes of all annotations,"
        " by default none"
    ),
)
@click.option(
    "--use-csv/--no-csv",
    default=False,
    help="Create human-readable .csv files containing the issues",
)
@click.option("--use-json/--no-json", default=True, help="Create .json files containing the issues")
@click.option("-q", "--quiet", is_flag=True, help="Disable progress bars")
def run_raillabel_providerkit(  # noqa: PLR0913
    annotations_folder: Path,
    output_folder: Path,
    ontology: Path | None,
    use_csv: bool,
    use_json: bool,
    quiet: bool,
) -> None:
    """Check a raillabel scene's annotations for errors."""
    # Stop early if there is nothing to output
    if not use_csv and not use_json:
        return

    # Ensure output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)

    # Get all scenes (.json files) in the folder and subfolders but ignore hidden folders
    scene_files = list(
        set(annotations_folder.glob("**/*.json")) - set(annotations_folder.glob(".*/**/*"))
    )

    for scene_path in tqdm(scene_files, desc="Validating files", disable=quiet):
        issues = validate(
            scene_path,
            ontology,
        )

        scene_name = scene_path.name
        if use_json:
            store_issues_to_json(issues, output_folder / scene_name.replace(".json", ".issues.json"))
        if use_csv:
            store_issues_to_csv(issues, output_folder / scene_name.replace(".json", ".issues.csv"))


if __name__ == "__main__":
    run_raillabel_providerkit()
