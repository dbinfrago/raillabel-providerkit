# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from uuid import UUID

from raillabel.format import (
    Bbox,
    Camera,
    Cuboid,
    Lidar,
    Poly2d,
    Poly3d,
    Radar,
    Scene,
    Seg3d,
)

from raillabel_providerkit.validation import IssueIdentifiers

from ._sensor_type import _SensorType


@dataclass
class _AnnotationWithMetadata:
    annotation_id: UUID
    frame_id: int
    scene: Scene

    @property
    def annotation(self) -> Bbox | Cuboid | Poly2d | Poly3d | Seg3d:
        return self.scene.frames[self.frame_id].annotations[self.annotation_id]

    @property
    def object_type(self) -> str:
        return self.scene.objects[self.annotation.object_id].type

    @property
    def sensor_type(self) -> _SensorType | None:
        sensor = self.scene.sensors[self.annotation.sensor_id]

        if isinstance(sensor, Camera):
            return _SensorType.CAMERA
        if isinstance(sensor, Lidar):
            return _SensorType.LIDAR
        if isinstance(sensor, Radar):
            return _SensorType.RADAR
        return None

    def to_identifiers(self, attribute: str | None = None) -> IssueIdentifiers:
        return IssueIdentifiers(
            annotation=self.annotation_id,
            annotation_type=self.annotation.__class__.__name__,
            frame=self.frame_id,
            sensor=self.annotation.sensor_id,
            object=self.annotation.object_id,
            object_type=self.object_type,
            attribute=attribute,
        )
