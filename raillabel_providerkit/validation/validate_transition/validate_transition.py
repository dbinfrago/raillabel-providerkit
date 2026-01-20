# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import raillabel
from raillabel.filter import IncludeObjectTypeFilter

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_transition(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether transition annotations have different start and end tracks.

    This matches the behavior of the legacy annotation-checks TransitionValidator.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all transition errors in the scene. If an empty list is returned, then there
        are no errors present.
    """
    issues = []

    # Filter scene for transition objects only
    filtered_scene = scene.filter([IncludeObjectTypeFilter(["transition"])])

    for frame_id, frame in filtered_scene.frames.items():
        for annotation_id, annotation in frame.annotations.items():
            # Get startTrack and endTrack attributes
            start_track = annotation.attributes.get("startTrack", None)
            end_track = annotation.attributes.get("endTrack", None)

            # Flag issue if startTrack == endTrack and both are not None
            if start_track == end_track and start_track is not None:
                reason = f"This transition's startTrack and endTrack are identical: {start_track}."
                issues.append(
                    Issue(
                        type=IssueType.TRANSITION_IDENTICAL_START_END,
                        identifiers=IssueIdentifiers(
                            annotation=annotation_id,
                            frame=frame_id,
                            object=annotation.object_id,
                            sensor=annotation.sensor_id,
                            attribute="startTrack",
                        ),
                        reason=reason,
                    )
                )

    return issues
