# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel.scene_builder import SceneBuilder

from raillabel_providerkit.validation import IssueType
from raillabel_providerkit.validation import validate_transition


def test_validate_transition__no_transitions():
    """No errors when scene has no transition objects."""
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="track")
        .add_poly2d(object_name="track_0000", sensor_id="rgb_center", attributes={"trackID": 0})
        .result
    )

    actual = validate_transition(scene)
    assert actual == []


def test_validate_transition__valid_transition():
    """No errors when transition has different start and end tracks."""
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="transition", object_name="transition_0001")
        .add_poly2d(
            object_name="transition_0001",
            sensor_id="rgb_center",
            attributes={"startTrack": "track_a", "endTrack": "track_b", "railSide": "leftRail"},
        )
        .result
    )

    actual = validate_transition(scene)
    assert actual == []


def test_validate_transition__identical_start_and_end():
    """Error when transition has identical start and end tracks."""
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="transition", object_name="transition_0001")
        .add_poly2d(
            object_name="transition_0001",
            sensor_id="rgb_center",
            attributes={"startTrack": "track_a", "endTrack": "track_a", "railSide": "leftRail"},
        )
        .result
    )

    actual = validate_transition(scene)
    assert len(actual) == 1
    assert actual[0].type == IssueType.TRANSITION_IDENTICAL_START_END
    assert actual[0].identifiers.attribute == "startTrack"


def test_validate_transition__multiple_errors():
    """Multiple errors for multiple transitions with identical start/end."""
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="transition", object_name="transition_0001")
        .add_poly2d(
            object_name="transition_0001",
            sensor_id="rgb_center",
            attributes={"startTrack": "track_a", "endTrack": "track_a", "railSide": "leftRail"},
        )
        .add_object(object_type="transition", object_name="transition_0002")
        .add_poly2d(
            object_name="transition_0002",
            sensor_id="rgb_center",
            attributes={"startTrack": "track_b", "endTrack": "track_b", "railSide": "rightRail"},
        )
        .result
    )

    actual = validate_transition(scene)
    assert len(actual) == 2
    for issue in actual:
        assert issue.type == IssueType.TRANSITION_IDENTICAL_START_END


def test_validate_transition__missing_attributes():
    """No error when transition is missing startTrack or endTrack (handled by ontology validator)."""
    scene = (
        SceneBuilder.empty()
        .add_sensor("rgb_center")
        .add_object(object_type="transition", object_name="transition_0001")
        .add_poly2d(
            object_name="transition_0001",
            sensor_id="rgb_center",
            attributes={"railSide": "leftRail"},
        )
        .result
    )

    actual = validate_transition(scene)
    assert actual == []


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])
