# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from uuid import UUID

import pytest
from raillabel.format import Point2d, Scene
from raillabel.scene_builder import SceneBuilder

from raillabel_providerkit.validation.validate_rail_side.validate_rail_side import (
    validate_rail_side,
    _count_rails_per_track_in_frame,
)
from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def add_left_rails(
    builder: SceneBuilder, n: int, object_name: str = "track_0001", sensor_id: str = "rgb_center"
) -> SceneBuilder:
    """Add a specified number of left rails to a SceneBuilder."""
    for _ in range(n):
        builder = builder.add_poly2d(
            frame_id=1,
            points=[
                Point2d(0, 0),
                Point2d(0, 1),
            ],
            attributes={"railSide": "leftRail"},
            object_name=object_name,
            sensor_id=sensor_id,
        )
    return builder


def add_right_rails(
    builder: SceneBuilder, n: int, object_name: str = "track_0001", sensor_id: str = "rgb_center"
) -> SceneBuilder:
    """Add a specified number of left rails to a SceneBuilder."""
    for _ in range(n):
        builder = builder.add_poly2d(
            frame_id=1,
            points=[
                Point2d(1, 0),
                Point2d(1, 1),
            ],
            attributes={"railSide": "rightRail"},
            object_name=object_name,
            sensor_id=sensor_id,
        )
    return builder


def get_object_id_from_object_name(scene: Scene, object_name: str) -> UUID:
    """Return the uuid of an object in a scene given its name."""
    for object_id, object_ in scene.objects.items():
        if object_.name == object_name:
            return object_id
    raise KeyError


def test_count_rails_per_track_in_frame__empty(empty_frame):
    frame = empty_frame
    results = _count_rails_per_track_in_frame(frame)
    assert len(results) == 0


def test_count_rails_per_track_in_frame__many_rails_for_one_track():
    builder = SceneBuilder.empty()
    builder = add_left_rails(builder, 32, "track_0001")
    builder = add_right_rails(builder, 42, "track_0001")
    scene = builder.result

    actual = _count_rails_per_track_in_frame(scene.frames[1])
    assert actual == {get_object_id_from_object_name(scene, "track_0001"): (32, 42)}


def test_count_rails_per_track_in_frame__many_rails_for_two_tracks():
    builder = SceneBuilder.empty()

    builder = add_left_rails(builder, 32, "track_0001")
    builder = add_right_rails(builder, 42, "track_0001")

    builder = add_left_rails(builder, 12, "track_0002")
    builder = add_right_rails(builder, 22, "track_0002")

    scene = builder.result

    actual = _count_rails_per_track_in_frame(scene.frames[1])
    assert actual == {
        get_object_id_from_object_name(scene, "track_0001"): (32, 42),
        get_object_id_from_object_name(scene, "track_0002"): (12, 22),
    }


def test_validate_rail_side__no_errors():
    builder = SceneBuilder.empty()
    builder = add_left_rails(builder, n=1)
    builder = add_right_rails(builder, n=1)

    scene = builder.result

    actual = validate_rail_side(scene)
    assert len(actual) == 0


def test_validate_rail_side__rail_sides_switched():
    scene = (
        SceneBuilder.empty()
        .add_poly2d(
            frame_id=1,
            points=[
                Point2d(0, 0),
                Point2d(0, 1),
            ],
            attributes={"railSide": "rightRail"},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .add_poly2d(
            frame_id=1,
            points=[
                Point2d(1, 0),
                Point2d(1, 1),
            ],
            attributes={"railSide": "leftRail"},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert actual == [
        Issue(
            type=IssueType.RAIL_SIDE,
            reason="The left and right rails of this track are swapped.",
            identifiers=IssueIdentifiers(
                frame=1,
                sensor="rgb_center",
                object=get_object_id_from_object_name(scene, "track_0001"),
            ),
        )
    ]


def test_validate_rail_side__rail_sides_intersect_at_top():
    scene = (
        SceneBuilder.empty()
        .add_poly2d(
            frame_id=1,
            points=[
                Point2d(20, 0),
                Point2d(20, 10),
                Point2d(10, 20),
                Point2d(10, 100),
            ],
            attributes={"railSide": "leftRail"},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .add_poly2d(
            frame_id=1,
            points=[
                Point2d(10, 0),
                Point2d(10, 10),
                Point2d(20, 20),
                Point2d(20, 100),
            ],
            attributes={"railSide": "rightRail"},
            object_name="track_0001",
            sensor_id="rgb_center",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert actual == [
        Issue(
            type=IssueType.RAIL_SIDE,
            reason="The left and right rails of this track intersect.",
            identifiers=IssueIdentifiers(
                frame=1,
                sensor="rgb_center",
                object=get_object_id_from_object_name(scene, "track_0001"),
            ),
        )
    ]


def test_validate_rail_side__rail_sides_correct_with_early_end_of_one_side():
    scene = (
        SceneBuilder.empty()
        .add_poly2d(
            points=[
                Point2d(70, 0),
                Point2d(30, 20),
                Point2d(15, 40),
                Point2d(10, 50),
                Point2d(10, 100),
            ],
            attributes={"railSide": "leftRail"},
            object_name="track_0001",
        )
        .add_poly2d(
            points=[
                Point2d(20, 50),
                Point2d(20, 100),
            ],
            attributes={"railSide": "rightRail"},
            object_name="track_0001",
        )
        .result
    )

    actual = validate_rail_side(scene)
    assert len(actual) == 0


def test_validate_rail_side__two_left_rails():
    builder = SceneBuilder.empty()
    builder = add_left_rails(builder, n=2, object_name="track_0001", sensor_id="rgb_center")
    scene = builder.result

    actual = validate_rail_side(scene)
    assert actual == [
        Issue(
            type=IssueType.RAIL_SIDE,
            reason="This track has 2 left rails.",
            identifiers=IssueIdentifiers(
                frame=1,
                sensor="rgb_center",
                object=get_object_id_from_object_name(scene, "track_0001"),
            ),
        )
    ]


def test_validate_rail_side__two_right_rails():
    builder = SceneBuilder.empty()
    builder = add_right_rails(builder, n=2, object_name="track_0001", sensor_id="rgb_center")
    scene = builder.result

    actual = validate_rail_side(scene)
    assert actual == [
        Issue(
            type=IssueType.RAIL_SIDE,
            reason="This track has 2 right rails.",
            identifiers=IssueIdentifiers(
                frame=1,
                sensor="rgb_center",
                object=get_object_id_from_object_name(scene, "track_0001"),
            ),
        )
    ]


def test_validate_rail_side__two_sensors_with_two_right_rails_each():
    builder = SceneBuilder.empty()
    builder = add_right_rails(builder, n=2, object_name="track_0001", sensor_id="rgb_center")
    builder = add_right_rails(builder, n=2, object_name="track_0001", sensor_id="ir_center")
    scene = builder.result

    actual = validate_rail_side(scene)
    assert len(actual) == 2


def test_validate_rail_side__two_sensors_with_one_right_rail_each():
    builder = SceneBuilder.empty()
    builder = add_right_rails(builder, n=1, object_name="track_0001", sensor_id="rgb_center")
    builder = add_right_rails(builder, n=1, object_name="track_0001", sensor_id="ir_center")
    scene = builder.result

    actual = validate_rail_side(scene)
    assert len(actual) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
