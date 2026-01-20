# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass

from raillabel_providerkit.validation import Issue, IssueType
from raillabel_providerkit.validation.validate_ontology._ontology_classes._sensor_type import (
    _SensorType,
)

from ._annotation_with_metadata import _AnnotationWithMetadata
from ._attributes._attribute_abc import _Attribute, attribute_classes


@dataclass
class _ObjectClass:
    attributes: dict[str, _Attribute]

    @classmethod
    def fromdict(cls, data: dict) -> _ObjectClass:
        return _ObjectClass(
            attributes={attr_name: cls._attribute_fromdict(attr) for attr_name, attr in data.items()}
        )

    def check(self, annotation_metadata: _AnnotationWithMetadata) -> list[Issue]:
        errors = []

        errors.extend(self._check_undefined_attributes(annotation_metadata))
        errors.extend(self._check_missing_attributes(annotation_metadata))
        errors.extend(self._check_false_attribute_type(annotation_metadata))
        return errors

    @classmethod
    def _attribute_fromdict(cls, attribute: dict) -> _Attribute:
        for attribute_class in attribute_classes():
            if attribute_class.supports(attribute):
                return attribute_class.fromdict(attribute)

        raise ValueError

    def _check_undefined_attributes(
        self, annotation_metadata: _AnnotationWithMetadata
    ) -> list[Issue]:
        return [
            Issue(
                type=IssueType.ATTRIBUTE_UNDEFINED,
                identifiers=annotation_metadata.to_identifiers(attr_name),
            )
            for attr_name in annotation_metadata.annotation.attributes
            if attr_name not in self._compile_applicable_attributes(annotation_metadata.sensor_type)
        ]

    def _check_missing_attributes(self, annotation_metadata: _AnnotationWithMetadata) -> list[Issue]:
        return [
            Issue(
                type=IssueType.ATTRIBUTE_MISSING,
                identifiers=annotation_metadata.to_identifiers(attr_name),
            )
            for attr_name, attr in self._compile_applicable_attributes(
                annotation_metadata.sensor_type
            ).items()
            if attr_name not in annotation_metadata.annotation.attributes and not attr.optional
        ]

    def _check_false_attribute_type(
        self, annotation_metadata: _AnnotationWithMetadata
    ) -> list[Issue]:
        errors = []

        applicable_attributes = self._compile_applicable_attributes(annotation_metadata.sensor_type)
        for attr_name, attr_value in annotation_metadata.annotation.attributes.items():
            if attr_name not in applicable_attributes:
                continue

            errors.extend(
                applicable_attributes[attr_name].check_type_and_value(
                    attr_name,
                    attr_value,
                    annotation_metadata.to_identifiers(attr_name),
                )
            )

        return errors

    def _compile_applicable_attributes(
        self,
        sensor_type: _SensorType,
    ) -> dict[str, _Attribute]:
        return {
            attr_name: attr
            for attr_name, attr in self.attributes.items()
            if sensor_type in [_SensorType(sensor_type_str) for sensor_type_str in attr.sensor_types]
        }
