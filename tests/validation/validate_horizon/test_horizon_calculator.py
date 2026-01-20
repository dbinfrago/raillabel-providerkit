# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest

from raillabel.format import Point2d
from raillabel_providerkit.validation.validate_horizon._horizon_calculator import (
    _HorizonCalculator,
    _generate_line_function,
)


def test_generate_line_function__same_x():
    with pytest.raises(ValueError):
        _generate_line_function(Point2d(3.0, 1.0), Point2d(3.0, 2.0))


def test_generate_line_function__same_y():
    line = _generate_line_function(Point2d(3.0, 42.0), Point2d(5.0, 42.0))
    assert line(3.0) == 42.0
    assert line(5.0) == 42.0
    assert line(1337.0) == 42.0


def test_generate_line_function__4x():
    line = _generate_line_function(Point2d(1.0, 4.0), Point2d(3.0, 12.0))
    assert line(1.0) == 4.0
    assert line(3.0) == 12.0
    assert line(73.0) == 4 * 73.0
