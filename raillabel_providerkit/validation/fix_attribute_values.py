# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path

import yaml  # type: ignore[import-untyped]

_MIN_ANNOTATION_NAME_PARTS = 3


@dataclass
class _FixContext:
    """Groups parameters needed during fix traversal."""

    option_lookup: dict[str, dict[str, set[str]]]
    fixes: list[str]


def fix_attribute_values(scene_data: dict, ontology_source: dict | Path) -> tuple[dict, list[str]]:
    """Fix attribute values with whitespace mismatches in a scene dictionary.

    Walks through all annotations in the scene and compares attribute values against
    ontology options. If a value differs only by whitespace from a valid option,
    it is replaced with the correct ontology value.

    Parameters
    ----------
    scene_data : dict
        The raw OpenLABEL scene data as a dictionary. Will NOT be modified in-place.
    ontology_source : dict | Path
        The ontology as a dictionary or as a Path to the ontology YAML file.

    Returns
    -------
    tuple[dict, list[str]]
        A tuple of (fixed_scene_data, list_of_fix_descriptions).
        The first element is a deep copy of scene_data with fixes applied.
        The second element describes each fix that was applied.
    """
    ontology = _load_ontology(ontology_source)
    option_lookup = _build_option_lookup(ontology)
    if not option_lookup:
        return scene_data, []

    fixed_data = copy.deepcopy(scene_data)
    ctx = _FixContext(option_lookup=option_lookup, fixes=[])

    frames = fixed_data.get("openlabel", fixed_data).get("frames", {})
    for frame_id, frame in frames.items():
        objects = frame.get("objects", {})
        for object_id, obj in objects.items():
            object_data = obj.get("object_data", {})
            _fix_annotations_in_object_data(object_data, ctx, frame_id, object_id)

    return fixed_data, ctx.fixes


def _load_ontology(ontology_source: dict | Path) -> dict:
    if isinstance(ontology_source, Path):
        with ontology_source.open() as f:
            if ontology_source.suffix in (".yaml", ".yml"):
                return yaml.safe_load(f)
            return json.load(f)
    return ontology_source


def _build_option_lookup(ontology: dict) -> dict[str, dict[str, set[str]]]:
    """Build a lookup: {object_type: {attribute_name: set_of_valid_options}}.

    Only includes single-select and multi-select attributes.
    Supports both flat ontology format (class_name → attr_name → attr_def) and
    wrapped format (classes → class_name → attributes → attr_name → attr_def).
    """
    lookup: dict[str, dict[str, set[str]]] = {}
    # Support both flat ontology YAML (top-level keys are class names)
    # and wrapped format ("classes" key wraps class definitions)
    classes = ontology.get("classes", ontology)
    for class_name, class_def in classes.items():
        if not isinstance(class_def, dict):
            continue
        # Support both direct attributes (flat YAML) and nested "attributes" key
        attributes = class_def.get("attributes", class_def)
        attr_lookup: dict[str, set[str]] = {}
        for attr_name, attr_def in attributes.items():
            if not isinstance(attr_def, dict):
                continue
            attr_type = attr_def.get("attribute_type")
            if isinstance(attr_type, dict) and attr_type.get("type") in (
                "single-select",
                "multi-select",
            ):
                options = attr_type.get("options", [])
                attr_lookup[attr_name] = set(options)
        if attr_lookup:
            lookup[class_name] = attr_lookup
    return lookup


def _find_whitespace_match(value: str, options: set[str]) -> str | None:
    """Find an option that matches the value when whitespace is normalized."""
    normalized = "".join(value.split())
    for option in options:
        if "".join(option.split()) == normalized:
            return option
    return None


def _fix_annotations_in_object_data(
    object_data: dict,
    ctx: _FixContext,
    frame_id: str,
    object_id: str,
) -> None:
    """Fix attribute values in all annotation types within object_data."""
    annotation_types = ("bbox", "poly2d", "poly3d", "cuboid", "vec", "num")
    for ann_type in annotation_types:
        for annotation in object_data.get(ann_type, []):
            options = _resolve_options(annotation, ctx.option_lookup)
            if options:
                location = f"Frame {frame_id}, Object {object_id}, {ann_type}"
                _fix_text_attributes(annotation, options, ctx, location)
                _fix_vec_attributes(annotation, options, ctx, location)


def _resolve_options(
    annotation: dict,
    option_lookup: dict[str, dict[str, set[str]]],
) -> dict[str, set[str]]:
    """Resolve valid options for an annotation based on its object type."""
    object_type = _extract_object_type(annotation.get("name", ""))
    if object_type and object_type in option_lookup:
        return option_lookup[object_type]

    merged: dict[str, set[str]] = {}
    for class_options in option_lookup.values():
        for attr_name, opts in class_options.items():
            merged[attr_name] = merged.get(attr_name, set()) | opts
    return merged


def _fix_text_attributes(
    annotation: dict,
    all_options: dict[str, set[str]],
    ctx: _FixContext,
    location: str,
) -> None:
    """Fix single-select text attributes with whitespace mismatches."""
    for attr_entry in annotation.get("attributes", {}).get("text", []):
        attr_name = attr_entry.get("name", "")
        if attr_name not in all_options:
            continue
        val = attr_entry.get("val")
        if not isinstance(val, str) or val in all_options[attr_name]:
            continue
        suggested = _find_whitespace_match(val, all_options[attr_name])
        if suggested is not None:
            attr_entry["val"] = suggested
            ctx.fixes.append(f"{location}: '{attr_name}' value '{val}' -> '{suggested}'")


def _fix_vec_attributes(
    annotation: dict,
    all_options: dict[str, set[str]],
    ctx: _FixContext,
    location: str,
) -> None:
    """Fix multi-select vec attributes with whitespace mismatches."""
    for attr_entry in annotation.get("attributes", {}).get("vec", []):
        attr_name = attr_entry.get("name", "")
        if attr_name not in all_options:
            continue
        val = attr_entry.get("val")
        if not isinstance(val, list):
            continue
        for i, item in enumerate(val):
            if not isinstance(item, str) or item in all_options[attr_name]:
                continue
            suggested = _find_whitespace_match(item, all_options[attr_name])
            if suggested is not None:
                val[i] = suggested
                ctx.fixes.append(f"{location}: '{attr_name}' value '{item}' -> '{suggested}'")


def _extract_object_type(annotation_name: str) -> str | None:
    """Extract object type from annotation name (e.g. 'rgb_center__bbox__person' -> 'person')."""
    parts = annotation_name.split("__")
    if len(parts) >= _MIN_ANNOTATION_NAME_PARTS:
        return parts[2]
    return None
