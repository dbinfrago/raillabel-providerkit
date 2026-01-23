# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import glob
import json
import typing as t
from pathlib import Path
from uuid import UUID

import pytest
import raillabel

json_data_directories = [
    Path(__file__).parent / "__assets__",
    Path(__file__).parent.parent / "raillabel_providerkit" / "format",
    Path(__file__).parent.parent / "config" / "schemas",
]


@pytest.fixture
def json_paths(request) -> t.Dict[str, Path]:
    out = _fetch_json_paths_from_cache(request)

    if out is None:
        out = {_get_file_identifier(p): p for p in _collect_json_paths()}

    return out


def _fetch_json_paths_from_cache(request) -> t.Optional[t.Dict[str, Path]]:
    return request.config.cache.get("json_paths", None)


def _collect_json_paths() -> t.List[Path]:
    out = []

    for dir in json_data_directories:
        out.extend([Path(p) for p in glob.glob(str(dir) + "/**/**.json", recursive=True)])

    return out


def _get_file_identifier(path: Path) -> str:
    """Return relative path from test asset dir as string."""

    if "__test_assets__" not in path.parts:
        return path.stem

    test_assets_dir_index = path.parts.index("__test_assets__")

    relative_path = ""
    for part in path.parts[test_assets_dir_index + 1 : -1]:
        relative_path += part + "/"

    relative_path += path.stem

    return relative_path


@pytest.fixture
def json_data(request) -> t.Dict[str, dict]:
    out = _fetch_json_data_from_cache(request)

    if out is None:
        out = {_get_file_identifier(p): _load_json_data(p) for p in _collect_json_paths()}

    return out


def _fetch_json_data_from_cache(request) -> t.Optional[t.Dict[str, Path]]:
    return request.config.cache.get("json_data", None)


def _load_json_data(path: Path) -> dict:
    with path.open() as f:
        out = json.load(f)
    return out


@pytest.fixture
def empty_scene() -> raillabel.Scene:
    return raillabel.Scene(
        metadata=raillabel.format.Metadata(schema_version="1.0.0"),
        sensors={},
        objects={},
        frames={},
    )


@pytest.fixture
def default_frame(empty_annotation) -> raillabel.format.Frame:
    return raillabel.format.Frame(
        timestamp=None,
        sensors={},
        frame_data={},
        annotations={UUID("0fb4fc0b-3eeb-443a-8dd0-2caf9912d016"): empty_annotation},
    )


@pytest.fixture
def empty_frame() -> raillabel.format.Frame:
    return raillabel.format.Frame(timestamp=None, sensors={}, frame_data={}, annotations={})


@pytest.fixture
def empty_annotation() -> raillabel.format.Bbox:
    return raillabel.format.Bbox(
        object_id=UUID("7df959d7-0ec2-4722-8b62-bb2e529de2ec"),
        sensor_id="IGNORE_THIS",
        pos=raillabel.format.Point2d(0.0, 0.0),
        size=raillabel.format.Size2d(0.0, 0.0),
        attributes={},
    )


@pytest.fixture
def ignore_uuid() -> UUID:
    return UUID("00000000-0000-0000-0000-000000000000")


@pytest.fixture
def sample_uuid_1() -> UUID:
    return UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def sample_uuid_2() -> UUID:
    return UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def sample_uuid_3() -> UUID:
    return UUID("00000000-0000-0000-0000-000000000003")


@pytest.fixture
def sample_uuid_4() -> UUID:
    return UUID("00000000-0000-0000-0000-000000000004")


@pytest.fixture
def sample_uuid_5() -> UUID:
    return UUID("00000000-0000-0000-0000-000000000005")
