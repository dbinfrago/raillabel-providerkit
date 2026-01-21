# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel.format import Camera, IntrinsicsPinhole, Point3d, Quaternion, Transform

from raillabel_providerkit.validation.validate_horizon._horizon_calculator import (
    _HorizonCalculator,
)


def _create_simple_camera(
    image_size: tuple[int, int] = (1920, 1080),
    focal_length: float = 1000.0,
    quat: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
) -> Camera:
    """Create a camera with identity rotation (or specified quaternion)."""
    return Camera(
        extrinsics=Transform(
            pos=Point3d(x=0.0, y=0.0, z=2.0),
            quat=Quaternion(x=quat[0], y=quat[1], z=quat[2], w=quat[3]),
        ),
        intrinsics=IntrinsicsPinhole(
            camera_matrix=(
                focal_length,
                0.0,
                image_size[0] / 2,
                0.0,
                focal_length,
                image_size[1] / 2,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
            ),
            distortion=(0.0, 0.0, 0.0, 0.0, 0.0),
            width_px=image_size[0],
            height_px=image_size[1],
        ),
        uri=None,
        description=None,
    )


def test_horizon_calculator__no_extrinsics():
    """Test that calculator raises error when extrinsics are None."""
    camera = Camera(
        extrinsics=None,
        intrinsics=IntrinsicsPinhole(
            camera_matrix=(1000.0, 0.0, 960.0, 0.0, 1000.0, 540.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0),
            distortion=(0.0, 0.0, 0.0, 0.0, 0.0),
            width_px=1920,
            height_px=1080,
        ),
        uri=None,
        description=None,
    )
    with pytest.raises(ValueError, match="extrinsics"):
        _HorizonCalculator(camera)


def test_horizon_calculator__no_intrinsics():
    """Test that calculator raises error when intrinsics are None."""
    camera = Camera(
        extrinsics=Transform(
            pos=Point3d(x=0.0, y=0.0, z=2.0),
            quat=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        ),
        intrinsics=None,
        uri=None,
        description=None,
    )
    with pytest.raises(ValueError, match="intrinsics"):
        _HorizonCalculator(camera)


def test_horizon_calculator__returns_callable():
    """Test that calculate_horizon returns a callable function."""
    camera = _create_simple_camera()
    calc = _HorizonCalculator(camera)

    horizon_fn = calc.calculate_horizon()

    # Should be callable and return a float
    result = horizon_fn(960)
    assert isinstance(result, float)


def test_horizon_calculator__horizon_is_horizontal():
    """Test that horizon line is horizontal (same Y for all X)."""
    camera = _create_simple_camera()
    calc = _HorizonCalculator(camera)

    horizon_fn = calc.calculate_horizon()

    # Horizon should return same Y for all X values
    y_left = horizon_fn(0)
    y_center = horizon_fn(960)
    y_right = horizon_fn(1920)

    assert y_left == y_center == y_right


def test_horizon_calculator__pitch_property_exists():
    """Test that pitch_degrees property exists and returns a float."""
    camera = _create_simple_camera()
    calc = _HorizonCalculator(camera)

    assert isinstance(calc.pitch_degrees, float)


def test_horizon_calculator__inclination_moves_horizon():
    """Test that inclination parameter affects horizon position."""
    camera = _create_simple_camera()
    calc = _HorizonCalculator(camera)

    horizon_no_incl = calc.calculate_horizon(inclination=0.0)(960)
    horizon_with_incl = calc.calculate_horizon(inclination=0.1)(960)

    # Positive inclination should move horizon (exact direction depends on camera orientation)
    assert horizon_no_incl != horizon_with_incl


def test_horizon_calculator__realistic_quaternion():
    """Test with a realistic camera quaternion from OSDAR23."""
    # This quaternion is from camera_mid_range from OSDAR23
    # The actual extrinsics from the scene file
    camera = Camera(
        extrinsics=Transform(
            pos=Point3d(x=0.099, y=-0.190, z=2.073),
            quat=Quaternion(x=0.5448, y=-0.5400, z=0.4494, w=-0.4578),
        ),
        intrinsics=IntrinsicsPinhole(
            camera_matrix=(
                6685.371,
                0.0,
                2736.0,
                0.0,
                6685.371,
                1824.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
            ),
            distortion=(0.0, 0.0, 0.0, 0.0, 0.0),
            width_px=5472,
            height_px=3648,
        ),
        uri=None,
        description=None,
    )
    calc = _HorizonCalculator(camera)

    horizon_fn = calc.calculate_horizon()
    horizon_y = horizon_fn(2736)

    # Horizon should return a valid float
    assert isinstance(horizon_y, float)
    # Pitch should be a valid angle
    assert isinstance(calc.pitch_degrees, float)
