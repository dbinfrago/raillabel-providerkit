# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import typing as t

import numpy as np
import raillabel
from scipy.spatial.transform import Rotation


def _generate_line_function(
    p1: raillabel.format.Point2d, p2: raillabel.format.Point2d
) -> t.Callable[[float], float]:
    """Generate a callable line function from two given points in 2D space.

    Parameters
    ----------
    p1 : raillabel.format.Point2d
        The first point.
    p2 : raillabel.format.Point2d
        The second point. Please note that p2.x has to be different from p1.x.

    Returns
    -------
    t.Callable[[float], float]
        A callable line function f(x: float) -> float that returns the y for a given x.
        The calculated line is the line that connects p1 and p2 so that y = f(x) = mx + n.
    """
    if p2.x == p1.x:
        msg = "The two points must have different x values!"
        raise ValueError(msg)

    m: float = (p2.y - p1.y) / (p2.x - p1.x)
    n: float = p1.y - m * p1.x

    def f(x: float) -> float:
        return float(m * x + n)

    return f


class _HorizonCalculator:
    extrinsics: np.ndarray
    extrinsics_inv: np.ndarray
    intrinsics: np.ndarray
    distortion_coefficients: np.ndarray
    sensor_resolution: np.ndarray
    alternative_calibration_workaround: bool

    def __init__(
        self,
        camera: raillabel.format.Camera,
        alternative_calibration_workaround: bool = False,
    ) -> None:
        # Apply workarounds
        self.alternative_calibration_workaround = alternative_calibration_workaround

        if camera.extrinsics is None:
            msg = "Only sensors with extrinsics != None are supported."
            raise ValueError(msg)

        if camera.intrinsics is None or not isinstance(
            camera.intrinsics, raillabel.format.IntrinsicsPinhole
        ):
            msg = "Only sensors with intrinsics != None with IntrinsicsPinhole format are supported."
            raise ValueError(msg)

        extrinsics: raillabel.format.Transform = camera.extrinsics
        intrinsics: raillabel.format.IntrinsicsPinhole = camera.intrinsics

        # Store extrinsics/intrinsics/distortion as numpy matrices
        self.extrinsics = np.zeros((4, 4))
        self.intrinsics = np.zeros((3, 3))
        self.distortion_coefficients = np.zeros((1, 5))

        # Get extrinsics translation vector
        extrinsics_translation: np.ndarray = np.array(
            [[extrinsics.pos.x], [extrinsics.pos.y], [extrinsics.pos.z]]
        )
        # Get extrinsics rotation matrix (from quaternion)
        extrinsics_rotation: np.ndarray = Rotation.from_quat(
            [
                extrinsics.quat.x,
                extrinsics.quat.y,
                extrinsics.quat.z,
                extrinsics.quat.w,
            ]
        ).as_matrix()
        # Combine extrinsics rotation matrix and translation vector into extrinsics matrix
        extrinsics_helper = np.zeros((3, 4))
        extrinsics_helper = np.hstack((extrinsics_rotation, extrinsics_translation))
        self.extrinsics = np.vstack((extrinsics_helper, np.array([0, 0, 0, 1])))
        self.extrinsics_inv = np.linalg.inv(self.extrinsics)

        # Get intrinsics matrix and convert it into 3x3
        cm: tuple = intrinsics.camera_matrix
        self.intrinsics = np.array(
            [[cm[0], cm[1], cm[2]], [cm[4], cm[5], cm[6]], [cm[8], cm[9], cm[10]]]
        )

        # Get distortion coefficients and convert to numpy array
        distortion_coefficients = intrinsics.distortion
        self.distortion_coefficients = np.array(distortion_coefficients)

        # Store sensor resolution for future use
        self.sensor_resolution = np.array([intrinsics.width_px, intrinsics.height_px])

    def transform_coordinates_from_world_to_camera(
        self, world_coordinates: raillabel.format.Point3d
    ) -> raillabel.format.Point3d:
        # Convert world coordinates into vector (numpy 4x1 matrix)
        world_coordinates_converted: np.ndarray = np.array(
            [world_coordinates.x, world_coordinates.y, world_coordinates.z, 1.0]
        )

        # Transform coordinates from world to camera coordinates
        camera_coordinates: np.ndarray = self.extrinsics_inv.dot(world_coordinates_converted)

        # Convert camera coordinates back into raillabel Point3d format and return them
        return raillabel.format.Point3d(
            camera_coordinates[0], camera_coordinates[1], camera_coordinates[2]
        )

    def transform_coordinates_from_camera_to_image(
        self, camera_coordinates: raillabel.format.Point3d
    ) -> raillabel.format.Point2d:
        # Convert camera coordinates into vector (numpy 1x3 matrix)
        # x forward, y left, z up
        camera_coordinates_converted: np.ndarray = np.array(
            [camera_coordinates.x, camera_coordinates.y, camera_coordinates.z]
        )

        # For OSDaR23, adjust/flip axes
        # so that it matches the conventions used for the following calculations
        # x right, y down, z forward
        if not self.alternative_calibration_workaround:
            camera_coordinates_converted = np.array(
                [
                    -camera_coordinates_converted[1],
                    -camera_coordinates_converted[2],
                    camera_coordinates_converted[0],
                ]
            )

        # Transform coordinates from camera to image coordinates 3d (u',v',w')
        image_coordinates_3d: np.ndarray = self.intrinsics.dot(camera_coordinates_converted)

        # Get the corresponding 2d image coordinates (u,v), where u=u'/w' and v=v'/w'
        image_coordinates_2d: np.ndarray = np.array(
            [
                image_coordinates_3d[0] / image_coordinates_3d[2],
                image_coordinates_3d[1] / image_coordinates_3d[2],
            ]
        )

        # NOTE: Distortion coefficients are ignored

        # Return the 2d image coordinates as Point2d
        return raillabel.format.Point2d(image_coordinates_2d[0], image_coordinates_2d[1])

    def get_translation_vector_from_extrinsics(self) -> np.ndarray:
        translation_vector: np.ndarray = np.array(
            [self.extrinsics[0][3], self.extrinsics[1][3], self.extrinsics[2][3]]
        )
        return translation_vector

    def get_rotation_matrix_from_extrinsics(self) -> np.ndarray:
        rotation_matrix: np.ndarray = np.array(
            [
                [self.extrinsics[0][0], self.extrinsics[0][1], self.extrinsics[0][2]],
                [self.extrinsics[1][0], self.extrinsics[1][1], self.extrinsics[1][2]],
                [self.extrinsics[2][0], self.extrinsics[2][1], self.extrinsics[2][2]],
            ]
        )
        return rotation_matrix

    def get_sensor_position_in_world_coordinates_flat(self) -> np.ndarray:
        # Get the translation vector
        sensor_position: np.ndarray = self.get_translation_vector_from_extrinsics()

        # Negate the vector (thus making it the position of the sensor
        # in the world coordinate system)
        sensor_position *= -1

        # Discard the z axis (flat world assumption)
        sensor_position[2] = 0

        # Return the vector
        return sensor_position

    def get_sensor_orientation_vector_in_world_coordinates_flat(self) -> np.ndarray:
        # The orientation vector shall be the vector that, in the world coordinate system,
        # points in the direction that the sensor is facing
        # Assumes flat world assumption, so z is thrown away (set to 0)

        # Create a vector that points directly foward (in the world coordinate system)
        front_vector_world: np.ndarray = np.array([1, 0, 0])

        # Get the rotation matrix
        rotation_matrix: np.ndarray = self.get_rotation_matrix_from_extrinsics()
        if rotation_matrix.shape != (3, 3):
            raise AssertionError

        # Rotate the front vector using the rotation matrix from the extrinsics
        # (without the translation vector)
        rotated_front_vector: np.ndarray = rotation_matrix.dot(front_vector_world)

        # Swap/flip rotation vector if alternative calibration conventions are used
        if self.alternative_calibration_workaround:
            rotated_front_vector = np.array(
                [
                    -rotated_front_vector[1],
                    -rotated_front_vector[0],
                    rotated_front_vector[2],
                ]
            )

        # Mirror the vector along the x axis (by negating y)
        rotated_front_vector[1] *= -1

        # Discard the z axis (flat world assumption)
        rotated_front_vector[2] = 0

        # Normalize the vector to unit length (length = 1)
        normalized_orientation_vector: np.ndarray = rotated_front_vector / np.linalg.norm(
            rotated_front_vector
        )

        # Return the vector (that, in the world coordinate system,
        # should now point inthe orientation that the sensor is facing)
        return normalized_orientation_vector

    def calculate_horizon(
        self,
        center_distance: float,
        side_distance: float,
        inclination: float = 0.0,
    ) -> t.Callable[[float], float]:
        # Select points in the distance (within world, aka lidar coordinate system)

        # Calculate a center point of the horizon that is far away (10km)
        # based on the camera's position and orientation
        camera_position: np.ndarray = self.get_sensor_position_in_world_coordinates_flat()
        camera_orientation_vector: np.ndarray = (
            self.get_sensor_orientation_vector_in_world_coordinates_flat()
        )
        horizon_center_point_far_away: np.ndarray = camera_position + (
            center_distance * camera_orientation_vector
        )

        # Add buffer height based on the maximum inclination a train can have
        horizon_center_point_far_away[2] += inclination * center_distance

        # In 2D, given the orientation vector (a,b), the normal vectors (orthogonal to the
        # orientation vector) are left=(-b,a) and right=(b,-a).
        # Remember that z is ignored because of the flat world assumption.
        left_vector: np.ndarray = np.array(
            [
                -camera_orientation_vector[1],
                camera_orientation_vector[0],
                camera_orientation_vector[2],
            ]
        )
        right_vector: np.ndarray = np.array(
            [
                camera_orientation_vector[1],
                -camera_orientation_vector[0],
                camera_orientation_vector[2],
            ]
        )

        # Calculate two points left and right of the center point of the horizon (e.g. 1km each)
        horizon_left_point_far_away: np.ndarray = horizon_center_point_far_away + (
            side_distance * left_vector
        )
        horizon_right_point_far_away: np.ndarray = horizon_center_point_far_away + (
            side_distance * right_vector
        )

        # Convert points into raillabel Point3d format
        p1_world: raillabel.format.Point3d = raillabel.format.Point3d(
            horizon_left_point_far_away[0],
            horizon_left_point_far_away[1],
            horizon_left_point_far_away[2],
        )
        p2_world: raillabel.format.Point3d = raillabel.format.Point3d(
            horizon_right_point_far_away[0],
            horizon_right_point_far_away[1],
            horizon_right_point_far_away[2],
        )

        # Convert points from world to camera coordinate system
        p1_camera: raillabel.format.Point3d = self.transform_coordinates_from_world_to_camera(
            p1_world
        )
        p2_camera: raillabel.format.Point3d = self.transform_coordinates_from_world_to_camera(
            p2_world
        )

        # Convert points from camera to image coordinate system
        p1_image: raillabel.format.Point2d = self.transform_coordinates_from_camera_to_image(
            p1_camera
        )
        p2_image: raillabel.format.Point2d = self.transform_coordinates_from_camera_to_image(
            p2_camera
        )

        # Calculate line function between selected points in the image coordinate system
        horizon_line: t.Callable[[float], float] = _generate_line_function(p1_image, p2_image)

        return horizon_line
