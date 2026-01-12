# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import raillabel

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def validate_empty_frames(scene: raillabel.Scene) -> list[Issue]:
    """Validate whether all frames of a scene have at least one annotation.

    Parameters
    ----------
    scene : raillabel.Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all empty frame errors in the scene. If an empty list is returned, then there
        are no errors present.
    """
    errors = []

    for frame_uid, frame in scene.frames.items():
        if _is_frame_empty(frame):
            errors.append(
                Issue(
                    type=IssueType.EMPTY_FRAMES,
                    identifiers=IssueIdentifiers(frame=frame_uid),
                )
            )

    return errors


def _is_frame_empty(frame: raillabel.format.Frame) -> bool:
    return len(frame.annotations) == 0
