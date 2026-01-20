# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import csv
import json
import time
from collections import Counter
from pathlib import Path

import click
import jsonschema
from tqdm import tqdm

from raillabel_providerkit import export_scenes, validate
from raillabel_providerkit.validation.issue import ISSUES_SCHEMA, Issue, IssueIdentifiers


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


# Time constants for duration formatting
_SECONDS_PER_MINUTE = 60
_MINUTES_PER_HOUR = 60


def _format_duration(seconds: float) -> str:
    """Format a duration in seconds to a human-readable string."""
    if seconds < _SECONDS_PER_MINUTE:
        return f"{seconds:.1f}s"
    minutes = int(seconds // _SECONDS_PER_MINUTE)
    remaining_seconds = seconds % _SECONDS_PER_MINUTE
    if minutes < _MINUTES_PER_HOUR:
        return f"{minutes}m {remaining_seconds:.0f}s"
    hours = int(minutes // _MINUTES_PER_HOUR)
    remaining_minutes = minutes % _MINUTES_PER_HOUR
    return f"{hours}h {remaining_minutes}m {remaining_seconds:.0f}s"


def _estimate_duration(num_scenes: int, avg_time_per_scene: float = 1.5) -> str:
    """Estimate and format the expected duration for validation.

    Parameters
    ----------
    num_scenes : int
        Number of scenes to validate
    avg_time_per_scene : float
        Estimated average time per scene in seconds (default: 1.5s)

    Returns
    -------
    str
        Formatted estimated duration
    """
    estimated_seconds = num_scenes * avg_time_per_scene
    return _format_duration(estimated_seconds)


def _print_summary(
    scene_issues: dict[str, list[Issue]], total_scenes: int, elapsed_time: float, quiet: bool
) -> None:
    """Print a summary of all validation issues to the terminal.

    Parameters
    ----------
    scene_issues : dict[str, list[Issue]]
        Dictionary mapping scene names to their list of issues
    total_scenes : int
        Total number of scenes validated
    elapsed_time : float
        Total time elapsed in seconds
    quiet : bool
        If True, skip printing the summary
    """
    if quiet:
        return

    total_issues = sum(len(issues) for issues in scene_issues.values())
    scenes_with_issues = sum(1 for issues in scene_issues.values() if issues)

    click.echo()
    click.echo("=" * 60)
    click.echo("VALIDATION SUMMARY")
    click.echo("=" * 60)
    click.echo(f"Scenes validated: {total_scenes}")
    click.echo(f"Scenes with issues: {scenes_with_issues}")
    click.echo(f"Total issues found: {total_issues}")
    click.echo(f"Time elapsed: {_format_duration(elapsed_time)}")

    if total_issues == 0:
        click.echo()
        click.secho("✓ No issues found!", fg="green", bold=True)
        return

    click.echo()
    click.echo("Issues by type:")
    click.echo("-" * 40)

    # Count issues by type across all scenes
    issue_type_counter: Counter[str] = Counter()
    for issues in scene_issues.values():
        for issue in issues:
            issue_type_counter[issue.type.value] += 1

    # Sort by count (descending) and print
    for issue_type, count in issue_type_counter.most_common():
        click.echo(f"  {count:>5}x {issue_type}")

    # Print detailed breakdown for attribute-related issues
    _print_attribute_details(scene_issues)

    click.echo("=" * 60)


def _print_attribute_details(scene_issues: dict[str, list[Issue]]) -> None:
    """Print detailed breakdown for attribute-related issues.

    Groups issues by type and attribute name for better overview.
    """
    # Issue types that have attribute details worth showing
    attribute_issue_types = {
        "AttributeMissing",
        "AttributeValueIssue",
        "AttributeTypeIssue",
        "AttributeUndefined",
        "AttributeScopeInconsistency",
    }

    # Collect attribute details: {issue_type: {attribute_name: count}}
    attribute_details: dict[str, Counter[str]] = {}

    for issues in scene_issues.values():
        for issue in issues:
            issue_type = issue.type.value
            if (
                issue_type in attribute_issue_types
                and isinstance(issue.identifiers, IssueIdentifiers)
                and issue.identifiers.attribute
            ):
                if issue_type not in attribute_details:
                    attribute_details[issue_type] = Counter()
                attribute_details[issue_type][issue.identifiers.attribute] += 1

    # Print details if any found
    if attribute_details:
        click.echo()
        click.echo("Attribute details:")
        click.echo("-" * 40)

        for issue_type in sorted(attribute_details.keys()):
            click.echo(f"  {issue_type}:")
            for attr_name, count in attribute_details[issue_type].most_common():
                click.echo(f"      {count:>5}x {attr_name}")


@click.group()
def cli() -> None:
    """RailLabel Providerkit - Tools for annotation providers."""


@cli.command(name="validate")
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
def validate_command(  # noqa: PLR0913
    annotations_folder: Path,
    output_folder: Path,
    ontology: Path | None,
    use_csv: bool,
    use_json: bool,
    quiet: bool,
) -> None:
    """Check raillabel scenes' annotations for errors."""
    _run_validation(annotations_folder, output_folder, ontology, use_csv, use_json, quiet)


def _run_validation(  # noqa: PLR0913
    annotations_folder: Path,
    output_folder: Path,
    ontology: Path | None,
    use_csv: bool,
    use_json: bool,
    quiet: bool,
) -> None:
    """Validate all scenes in a folder and output validation results."""
    # Stop early if there is nothing to output
    if not use_csv and not use_json:
        return

    # Ensure output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)

    # Get all scenes (.json files) in the folder and subfolders but ignore hidden folders
    scene_files = list(
        set(annotations_folder.glob("**/*.json")) - set(annotations_folder.glob(".*/**/*"))
    )

    # Print estimated duration
    if not quiet:
        estimated = _estimate_duration(len(scene_files))
        click.echo(f"Found {len(scene_files)} scene(s) to validate")
        click.echo(f"Estimated duration: ~{estimated}")
        click.echo()

    # Start timing
    start_time = time.time()

    # Collect all issues for summary
    scene_issues: dict[str, list[Issue]] = {}

    for scene_path in tqdm(scene_files, desc="Validating files", disable=quiet):
        issues = validate(
            scene_path,
            ontology,
        )

        scene_name = scene_path.name
        scene_issues[scene_name] = issues

        if use_json:
            store_issues_to_json(issues, output_folder / scene_name.replace(".json", ".issues.json"))
        if use_csv:
            store_issues_to_csv(issues, output_folder / scene_name.replace(".json", ".issues.csv"))

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    _print_summary(scene_issues, len(scene_files), elapsed_time, quiet)


@cli.command(name="export")
@click.argument(
    "input_folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument(
    "output_folder",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--format",
    "formats",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    multiple=True,
    default=["json"],
    help="Export format(s). Can be specified multiple times for multiple formats.",
)
@click.option("-q", "--quiet", is_flag=True, help="Disable progress bars")
def export_command(
    input_folder: Path,
    output_folder: Path,
    formats: tuple[str, ...],
    quiet: bool,
) -> None:
    """Export multiple scenes to different formats (JSON, CSV)."""
    if not formats:
        formats = ("json",)

    # Convert tuple to list and cast to ExportFormat list
    from typing import cast

    from raillabel_providerkit.export.export_scenes import ExportFormat

    format_list = cast(list[ExportFormat], list(formats))

    # Start timing
    start_time = time.time()

    if not quiet:
        click.echo(f"Exporting scenes from: {input_folder}")
        click.echo(f"Output folder: {output_folder}")
        click.echo(f"Format(s): {', '.join(format_list)}")
        click.echo()

    # Export scenes
    stats = export_scenes(input_folder, output_folder, format_list, quiet)

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    # Print summary
    if not quiet:
        click.echo()
        click.echo("=" * 60)
        click.echo("EXPORT SUMMARY")
        click.echo("=" * 60)
        click.echo(f"Total scenes found: {stats['total']}")
        click.echo(f"Successfully exported: {stats['exported']}")
        click.echo(f"Failed: {stats['errors']}")
        click.echo(f"Time elapsed: {_format_duration(elapsed_time)}")

        if stats["exported"] > 0:
            click.echo()
            click.secho("✓ Export complete!", fg="green", bold=True)
        elif stats["errors"] > 0:
            click.echo()
            click.secho("✗ Some scenes failed to export", fg="red", bold=True)
        elif stats["total"] == 0:
            click.echo()
            click.secho("⚠ No scenes found in input folder", fg="yellow", bold=True)

        click.echo("=" * 60)


# Maintain backward compatibility - run validate command if no subcommand specified
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
    """Check a raillabel scene's annotations for errors (legacy command)."""
    _run_validation(annotations_folder, output_folder, ontology, use_csv, use_json, quiet)


if __name__ == "__main__":
    import sys

    # Check if we're being called with legacy interface or new CLI
    if len(sys.argv) > 1 and sys.argv[1] in ["validate", "export"]:
        cli()
    else:
        # Legacy mode - backward compatibility
        run_raillabel_providerkit()
