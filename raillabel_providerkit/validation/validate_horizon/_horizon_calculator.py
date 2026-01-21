# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""Horizon calculation for camera sensors based on extrinsics and intrinsics."""

import typing as t

import numpy as np
import raillabel
from scipy.spatial.transform import Rotation


class _HorizonCalculator:
    """Calculate the horizon line position in camera images.

    The horizon is calculated based on the camera's pitch angle (tilt) derived
    from the extrinsics rotation matrix. This approach is robust across different
    calibration conventions (OSDAR23, OSDAR26, etc.) as it directly uses the
    geometric relationship between camera orientation and the image plane.

    The horizon line in the image represents where points at camera height
    in the far distance would project. Points above this line in the image
    represent real-world points above camera height (sky, distant hills, etc.).
    Track annotations should always be below the horizon since rails are on
    the ground below camera height.
    """

    def __init__(
        self,
        camera: raillabel.format.Camera,
        alternative_calibration_workaround: bool = False,  # noqa: ARG002
    ) -> None:
        """Initialize the horizon calculator with camera parameters.

        Parameters
        ----------
        camera : raillabel.format.Camera
            The camera sensor with extrinsics and intrinsics.
        alternative_calibration_workaround : bool, optional
            Legacy parameter kept for backwards compatibility.
            The new implementation handles all calibration formats automatically.
        """
        if camera.extrinsics is None:
            msg = "Only sensors with extrinsics != None are supported."
            raise ValueError(msg)

        if camera.intrinsics is None or not isinstance(
            camera.intrinsics, raillabel.format.IntrinsicsPinhole
        ):
            msg = "Only sensors with intrinsics != None with IntrinsicsPinhole format are supported."
            raise ValueError(msg)

        extrinsics = camera.extrinsics
        intrinsics = camera.intrinsics

        # Get rotation matrix from quaternion
        self._rotation_matrix: np.ndarray = Rotation.from_quat(
            [extrinsics.quat.x, extrinsics.quat.y, extrinsics.quat.z, extrinsics.quat.w]
        ).as_matrix()

        # Get intrinsics parameters
        cm = intrinsics.camera_matrix
        self._fy: float = float(cm[5])  # Focal length in y direction (pixels)
        self._cy: float = float(cm[6])  # Principal point y coordinate

        # Calculate camera forward direction in world coordinates
        # Camera Z-axis (optical axis) in camera frame is [0, 0, 1]
        # In world coordinates: R^T @ [0, 0, 1]
        self._camera_forward_world: np.ndarray = self._rotation_matrix.T @ np.array([0.0, 0.0, 1.0])

        # Calculate pitch angle (angle below horizontal)
        # Negative Z component of forward vector means looking down
        self._pitch_radians: float = float(np.arcsin(-self._camera_forward_world[2]))

    def calculate_horizon(
        self,
        center_distance: float = 10000.0,  # noqa: ARG002
        side_distance: float = 1000.0,  # noqa: ARG002
        inclination: float = 0.0,
    ) -> t.Callable[[float], float]:
        """Calculate a function that returns the horizon Y coordinate for any X.

        The horizon is calculated based on the camera's pitch angle. For a camera
        pointing horizontally (pitch=0), the horizon is at the principal point (cy).
        For a camera tilted down, the horizon moves up in the image (smaller Y).

        Parameters
        ----------
        center_distance : float, optional
            Legacy parameter, kept for backwards compatibility. Not used.
        side_distance : float, optional
            Legacy parameter, kept for backwards compatibility. Not used.
        inclination : float, optional
            Additional angular offset to add to the horizon calculation (in radians).
            Positive values move the horizon up (more permissive for tracks).
            This represents the expected maximum track inclination.
            Default is 0.0.

        Returns
        -------
        Callable[[float], float]
            A function that takes an X coordinate and returns the horizon Y coordinate.
            Since the pitch-based horizon is horizontal in the image, this returns
            the same Y value for all X coordinates.
        """
        # Calculate horizon Y position based on pitch angle
        # If camera looks down by pitch radians, horizon is above cy by tan(pitch) * fy
        # The inclination parameter adds additional upward shift for tolerance
        total_angle = self._pitch_radians + inclination
        horizon_y = float(self._cy - np.tan(total_angle) * self._fy)

        # Return a function that gives the same horizon_y for all x
        # (horizon line is horizontal in image for level cameras)
        def horizon_function(x: float) -> float:  # noqa: ARG001
            return horizon_y

        return horizon_function

    @property
    def pitch_degrees(self) -> float:
        """Return the camera pitch angle in degrees.

        Positive values mean the camera is pointing downward.
        """
        return float(np.degrees(self._pitch_radians))
