# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from raillabel.format import Cuboid, Scene

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

from ._dimensions import DIMENSIONS, _TypeDimensions


def validate_dimensions(scene: Scene) -> list[Issue]:
    """Validate whether any annotations exceed the predefined bounds.

    Parameters
    ----------
    scene : Scene
        Scene that should be validated.

    Returns
    -------
    list[Issue]
        List of all dimension errors in the scene. If an empty list is returned, then there
        are no errors present.
    """
    issues = []
    for annotation, identifiers in _get_annotations_with_identifiers(scene):
        type_dimensions = _identify_applicable_type_dimension(annotation, identifiers)
        if type_dimensions is None:
            continue

        issues.extend(_validate_height(annotation, identifiers, type_dimensions))
        issues.extend(_validate_width(annotation, identifiers, type_dimensions))

    return issues


def _get_annotations_with_identifiers(scene: Scene) -> list[tuple[Cuboid, IssueIdentifiers]]:
    annotations_with_identfiers = []
    for frame_id, frame in scene.frames.items():
        for annotation_id, annotation in frame.annotations.items():
            if not isinstance(annotation, Cuboid):
                continue

            annotations_with_identfiers.append(
                (
                    annotation,
                    IssueIdentifiers(
                        annotation=annotation_id,
                        annotation_type=annotation.__class__.__name__,
                        frame=frame_id,
                        object=annotation.object_id,
                        object_type=scene.objects[annotation.object_id].type,
                    ),
                )
            )

    return annotations_with_identfiers


def _identify_applicable_type_dimension(
    annotation: Cuboid, identifiers: IssueIdentifiers
) -> _TypeDimensions | None:
    for type_dimensions in DIMENSIONS:
        if type_dimensions.applies(identifiers.object_type, annotation):
            return type_dimensions
    return None


def _validate_height(
    annotation: Cuboid, identifiers: IssueIdentifiers, type_dimensions: _TypeDimensions
) -> list[Issue]:
    if type_dimensions.height is None:
        return []

    if annotation.size.z < type_dimensions.height.min:
        return [
            Issue(
                type=IssueType.DIMENSION_INVALID,
                identifiers=identifiers,
                reason=f"Height is too small ({annotation.size.z} < {type_dimensions.height.min}).",
            )
        ]

    if annotation.size.z > type_dimensions.height.max:
        return [
            Issue(
                type=IssueType.DIMENSION_INVALID,
                identifiers=identifiers,
                reason=f"Height is too large ({annotation.size.z} > {type_dimensions.height.max}).",
            )
        ]

    return []


def _validate_width(
    annotation: Cuboid, identifiers: IssueIdentifiers, type_dimensions: _TypeDimensions
) -> list[Issue]:
    if type_dimensions.width is None:
        return []

    if min(annotation.size.x, annotation.size.y) < type_dimensions.width.min:
        return [
            Issue(
                type=IssueType.DIMENSION_INVALID,
                identifiers=identifiers,
                reason=(
                    "Width is too small "
                    f"({min(annotation.size.x, annotation.size.y)} < {type_dimensions.width.min})."
                ),
            )
        ]

    if max(annotation.size.x, annotation.size.y) > type_dimensions.width.max:
        return [
            Issue(
                type=IssueType.DIMENSION_INVALID,
                identifiers=identifiers,
                reason=(
                    "Width is too large "
                    f"({max(annotation.size.x, annotation.size.y)} > {type_dimensions.width.max})."
                ),
            )
        ]

    return []
