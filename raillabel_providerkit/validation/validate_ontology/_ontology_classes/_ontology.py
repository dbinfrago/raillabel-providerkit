# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass

import raillabel

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

from ._annotation_with_metadata import _AnnotationWithMetadata
from ._object_classes import _ObjectClass


@dataclass
class _Ontology:
    classes: dict[str, _ObjectClass]
    errors: list[Issue]

    @classmethod
    def fromdict(cls, data: dict) -> _Ontology:
        return _Ontology(
            {class_id: _ObjectClass.fromdict(class_) for class_id, class_ in data.items()}, []
        )

    def check(self, scene: raillabel.Scene) -> list[Issue]:
        self.errors = []

        self._check_class_validity(scene)
        annotations = _Ontology._compile_annotations(scene)
        for annotation_metadata in annotations:
            if annotation_metadata.object_type not in self.classes:
                continue

            self.errors.extend(
                self.classes[annotation_metadata.object_type].check(annotation_metadata)
            )

        self.errors.extend(self._check_attribute_scopes(annotations))

        return self.errors

    def _check_class_validity(self, scene: raillabel.Scene) -> None:
        for obj_uid, obj in scene.objects.items():
            object_class = obj.type
            if object_class not in self.classes:
                self.errors.append(
                    Issue(
                        type=IssueType.OBJECT_TYPE_UNDEFINED,
                        identifiers=IssueIdentifiers(object=obj_uid, object_type=object_class),
                    )
                )

    def _check_attribute_scopes(
        self, annotations_with_metadata: list[_AnnotationWithMetadata]
    ) -> list[Issue]:
        errors: list[Issue] = []
        checked_attributes_by_object_type: dict[str, list[str]] = {}

        for annotation_with_metadata in annotations_with_metadata:
            object_type_name = annotation_with_metadata.object_type

            if object_type_name not in self.classes:
                # NOTE: This is an UNEXPECTED_CLASS issue and handled elsewhere.
                continue
            object_class = self.classes[object_type_name]

            if object_type_name not in checked_attributes_by_object_type:
                checked_attributes_by_object_type[object_type_name] = []

            for (
                attribute_name,
                attribute_value,
            ) in annotation_with_metadata.annotation.attributes.items():
                attribute = object_class.attributes.get(attribute_name)
                if attribute is None:
                    continue

                if attribute_name in checked_attributes_by_object_type[object_type_name]:
                    continue
                checked_attributes_by_object_type[object_type_name].append(attribute_name)

                for other_annotation_with_metadata in annotations_with_metadata:
                    if (
                        other_annotation_with_metadata is annotations_with_metadata
                        or other_annotation_with_metadata.object_type != object_type_name
                    ):
                        continue

                    if attribute_name not in other_annotation_with_metadata.annotation.attributes:
                        return []
                    other_attribute_value = other_annotation_with_metadata.annotation.attributes[
                        attribute_name
                    ]

                    errors.extend(
                        attribute.check_scope_for_two_annotations(
                            attribute_name,
                            attribute_value,
                            other_attribute_value,
                            annotation_with_metadata.to_identifiers(attribute_name),
                            other_annotation_with_metadata.to_identifiers(attribute_name),
                        )
                    )

        return errors

    @classmethod
    def _compile_annotations(cls, scene: raillabel.Scene) -> list[_AnnotationWithMetadata]:
        return [
            _AnnotationWithMetadata(annotation_id, frame_id, scene)
            for frame_id, frame in scene.frames.items()
            for annotation_id in frame.annotations
        ]
