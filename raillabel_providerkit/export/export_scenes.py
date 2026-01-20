# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Module for exporting scenes to different formats."""

from __future__ import annotations

import csv
import warnings
from pathlib import Path
from typing import Literal

import raillabel
from tqdm import tqdm

ExportFormat = Literal["json", "csv"]


def export_scenes(  # noqa: C901
    input_folder: Path,
    output_folder: Path,
    formats: list[ExportFormat] | None = None,
    quiet: bool = False,
) -> dict[str, int]:
    """Export multiple scenes from a folder to different formats.

    Parameters
    ----------
    input_folder : Path
        Folder containing scene JSON files to export
    output_folder : Path
        Folder where exported files will be saved
    formats : list[ExportFormat] | None, optional
        List of formats to export to. Can contain 'json', 'csv', or both.
        If None, defaults to ['json'].
    quiet : bool, optional
        If True, disables progress bars. Default is False.

    Returns
    -------
    dict[str, int]
        Dictionary with export statistics:
        - 'total': Total number of scenes found
        - 'exported': Number of successfully exported scenes
        - 'errors': Number of scenes that failed to export

    Raises
    ------
    ValueError
        If formats list is empty or contains invalid format names
    FileNotFoundError
        If input_folder does not exist
    """
    if not input_folder.exists():
        msg = f"Input folder does not exist: {input_folder}"
        raise FileNotFoundError(msg)

    if formats is None:
        formats = ["json"]

    if not formats:
        msg = "At least one export format must be specified"
        raise ValueError(msg)

    valid_formats = {"json", "csv"}
    invalid = set(formats) - valid_formats
    if invalid:
        msg = f"Invalid format(s): {invalid}. Valid formats: {valid_formats}"
        raise ValueError(msg)

    # Create output folder
    output_folder.mkdir(parents=True, exist_ok=True)

    # Find all JSON scene files
    scene_files = list(set(input_folder.glob("**/*.json")) - set(input_folder.glob(".*/**/*")))

    if not scene_files:
        return {"total": 0, "exported": 0, "errors": 0}

    # Export statistics
    stats = {"total": len(scene_files), "exported": 0, "errors": 0}

    # Process each scene
    for scene_path in tqdm(scene_files, desc="Exporting scenes", disable=quiet):
        try:
            scene = raillabel.load(scene_path)

            if "json" in formats:
                _export_to_json(scene, output_folder, scene_path.name)

            if "csv" in formats:
                _export_to_csv(scene, output_folder, scene_path.stem)

            stats["exported"] += 1

        except (OSError, ValueError, KeyError) as e:  # noqa: PERF203
            stats["errors"] += 1
            if not quiet:
                warnings.warn(f"Error exporting {scene_path.name}: {e}", stacklevel=2)

    return stats


def _export_to_json(scene: raillabel.Scene, output_folder: Path, filename: str) -> None:
    """Export a scene to JSON format.

    Parameters
    ----------
    scene : raillabel.Scene
        The scene to export
    output_folder : Path
        Folder where the JSON file will be saved
    filename : str
        Name of the output file
    """
    output_path = output_folder / filename
    raillabel.save(scene, output_path)


def _export_to_csv(scene: raillabel.Scene, output_folder: Path, filename_stem: str) -> None:
    """Export a scene to CSV format.

    Exports annotations to a tabular CSV format for easy analysis.
    Creates separate CSV files for different annotation types if needed.

    Parameters
    ----------
    scene : raillabel.Scene
        The scene to export
    output_folder : Path
        Folder where the CSV file(s) will be saved
    filename_stem : str
        Base name for the output file(s) (without extension)
    """
    # Export annotations to CSV
    annotations_data = []

    for frame_id, frame in scene.frames.items():
        for object_id, annotation in frame.annotations.items():
            row = {
                "frame_id": frame_id,
                "object_id": object_id,
                "annotation_type": annotation.__class__.__name__,
                "sensor_id": getattr(annotation, "sensor_id", ""),
            }

            # Add type-specific data
            if hasattr(annotation, "attributes"):
                for attr_name, attr_value in annotation.attributes.items():
                    row[f"attr_{attr_name}"] = attr_value

            annotations_data.append(row)

    if annotations_data:
        output_path = output_folder / f"{filename_stem}_annotations.csv"
        _write_csv(annotations_data, output_path)

    # Export metadata to CSV
    metadata_data = [
        {
            "schema_version": scene.metadata.schema_version,
            "name": getattr(scene.metadata, "name", ""),
            "annotator": getattr(scene.metadata, "annotator", ""),
            "tagged_file": getattr(scene.metadata, "tagged_file", ""),
        }
    ]
    metadata_path = output_folder / f"{filename_stem}_metadata.csv"
    _write_csv(metadata_data, metadata_path)

    # Export objects to CSV
    objects_data = [
        {"object_id": obj_id, "name": obj.name, "type": obj.type}
        for obj_id, obj in scene.objects.items()
    ]
    if objects_data:
        objects_path = output_folder / f"{filename_stem}_objects.csv"
        _write_csv(objects_data, objects_path)

    # Export sensors to CSV
    sensors_data = [
        {
            "sensor_id": sensor_id,
            "sensor_type": sensor.TYPE,
            "uri": getattr(sensor, "uri", ""),
        }
        for sensor_id, sensor in scene.sensors.items()
    ]
    if sensors_data:
        sensors_path = output_folder / f"{filename_stem}_sensors.csv"
        _write_csv(sensors_data, sensors_path)


def _write_csv(data: list[dict], output_path: Path) -> None:
    """Write a list of dictionaries to a CSV file.

    Parameters
    ----------
    data : list[dict]
        List of dictionaries to write
    output_path : Path
        Path to the output CSV file
    """
    if not data:
        return

    # Collect all unique fieldnames across all rows
    fieldnames: set[str] = set()
    for row in data:
        fieldnames.update(row.keys())

    # Sort fieldnames for consistent output
    fieldnames_sorted = sorted(fieldnames)

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_sorted, restval="")
        writer.writeheader()
        writer.writerows(data)
