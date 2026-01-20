# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from dataclasses import dataclass

from raillabel.format import Cuboid


@dataclass
class _DimensionRange:
    min: float
    max: float


@dataclass
class _TypeDimensions:
    type: str | list[str]
    attributes: dict[str, str | list[str]] | None = None
    height: _DimensionRange | None = None
    width: _DimensionRange | None = None

    def applies(self, type_: str, annotation: Cuboid) -> bool:
        """Return True if this _TypeDimensions instance applies to the given annotation."""
        self._preprocess_variables()

        if type_ not in self.type:
            return False

        if self.attributes is None:
            return True

        for attr_name, attr_val in self.attributes.items():
            if attr_name not in annotation.attributes:
                return False

            if annotation.attributes[attr_name] not in attr_val:
                return False

        return True

    def _preprocess_variables(self) -> None:
        if isinstance(self.type, str):
            self.type = [self.type]

        if self.attributes is None:
            return

        for attribute in self.attributes:
            if isinstance(self.attributes[attribute], str):
                self.attributes[attribute] = [self.attributes[attribute]]


DIMENSIONS = [
    _TypeDimensions(
        type="person",
        attributes={
            "age": "adult",
            "pose": "upright",
        },
        height=_DimensionRange(1.1, 2.7),
        width=_DimensionRange(0.1, 2.0),
    ),
    _TypeDimensions(
        type="person",
        attributes={
            "age": "adult",
            "pose": "sitting",
        },
        height=_DimensionRange(0.5, 2.5),
        width=_DimensionRange(0.1, 2.0),
    ),
    _TypeDimensions(
        type="person",
        attributes={
            "age": "adult",
            "pose": "lying",
        },
        height=_DimensionRange(0.1, 0.6),
        width=_DimensionRange(0.1, 2.5),
    ),
    _TypeDimensions(
        type="person",
        attributes={
            "age": "child",
            "pose": "upright",
        },
        height=_DimensionRange(0.5, 1.6),
        width=_DimensionRange(0.1, 1.5),
    ),
    _TypeDimensions(
        type="person",
        attributes={
            "age": "child",
            "pose": "sitting",
        },
        height=_DimensionRange(0.5, 1.4),
        width=_DimensionRange(0.1, 1.5),
    ),
    _TypeDimensions(
        type="person",
        attributes={
            "age": "adult",
            "pose": "lying",
        },
        height=_DimensionRange(0.1, 0.6),
        width=_DimensionRange(0.1, 1.6),
    ),
    _TypeDimensions(  # catchall for person
        type="person",
        height=_DimensionRange(0.1, 2.7),
        width=_DimensionRange(0.1, 2.0),
    ),
    _TypeDimensions(
        type="personal_item",
        height=_DimensionRange(0.2, 3.5),
        width=_DimensionRange(0.2, 3.5),
    ),
    _TypeDimensions(
        type="pram",
        height=_DimensionRange(0.3, 1.6),
        width=_DimensionRange(0.4, 2.0),
    ),
    _TypeDimensions(
        type="crowd",
        height=_DimensionRange(0.5, 2.5),
    ),
    _TypeDimensions(
        type="scooter",
        height=_DimensionRange(0.3, 1.6),
        width=_DimensionRange(0.1, 2.5),
    ),
    _TypeDimensions(
        type="bicycle",
        height=_DimensionRange(0.3, 1.6),
        width=_DimensionRange(0.1, 2.5),
    ),
    _TypeDimensions(
        type="group_of_bicycles",
        height=_DimensionRange(0.3, 1.6),
    ),
    _TypeDimensions(
        type="wheelchair",
        height=_DimensionRange(0.6, 1.6),
        width=_DimensionRange(0.5, 1.6),
    ),
    _TypeDimensions(
        type=["train", "rail_vehicle", "wagons"],
        height=_DimensionRange(0.9, 6.0),
        width=_DimensionRange(1.7, 900.0),
    ),
    _TypeDimensions(
        type="motorcycle",
        height=_DimensionRange(0.9, 3.0),
        width=_DimensionRange(0.1, 3.0),
    ),
    _TypeDimensions(
        type="road_vehicle",
        attributes={"type": "bus"},
        height=_DimensionRange(1.5, 8.0),
        width=_DimensionRange(1.5, 25.0),
    ),
    _TypeDimensions(
        type="road_vehicle",
        height=_DimensionRange(0.5, 8.0),
        width=_DimensionRange(1.5, 25.0),
    ),
    _TypeDimensions(
        type="animal",
        attributes={"size": "small"},
        height=_DimensionRange(0.1, 0.6),
        width=_DimensionRange(0.1, 1.5),
    ),
    _TypeDimensions(
        type="animal",
        attributes={"size": "medium"},
        height=_DimensionRange(0.4, 1.3),
        width=_DimensionRange(0.3, 2.0),
    ),
    _TypeDimensions(
        type="animal",
        attributes={"size": "large"},
        height=_DimensionRange(1.2, 3.0),
        width=_DimensionRange(0.3, 4.0),
    ),
    _TypeDimensions(  # catchall for animal
        type="animal",
        height=_DimensionRange(1.2, 3.0),
        width=_DimensionRange(0.3, 4.0),
    ),
    _TypeDimensions(  # catchall for animal
        type="group_of_animals",
        height=_DimensionRange(0.1, 3.0),
    ),
    _TypeDimensions(
        type="drag_shoe",
        height=_DimensionRange(0.08, 0.7),
        width=_DimensionRange(0.08, 0.7),
    ),
    _TypeDimensions(
        type=["track", "transition", "switch"],
        height=_DimensionRange(0.1, 0.8),
    ),
    _TypeDimensions(
        type="catenary_pole",
        height=_DimensionRange(3.0, 21.0),
        width=_DimensionRange(0.1, 3.0),
    ),
    _TypeDimensions(
        type="signal",
        height=_DimensionRange(0.1, 4.0),
        width=_DimensionRange(0.1, 4.0),
    ),
    _TypeDimensions(
        type="signal_pole",
        height=_DimensionRange(1.0, 14.0),
        width=_DimensionRange(0.1, 4.0),
    ),
    _TypeDimensions(
        type="signal_bridge",
        height=_DimensionRange(0.1, 10.0),
        width=_DimensionRange(0.1, 30.0),
    ),
    _TypeDimensions(
        type="buffer_stop",
        height=_DimensionRange(0.9, 4.0),
        width=_DimensionRange(0.5, 4.5),
    ),
]
