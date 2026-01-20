..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: Apache-2.0

..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: MIT

===================
1 Validating Scenes
===================

Motivation
##########
The validation of the project requirements should ideally be done as close to the source of the data as possible. This devkit therefore provides functionality to check for basic errors on the supplier side. If you are unsure whether your applications produce valid annotations, simply use the functions provided here to check. **Only send us data, if the methods below say that no errors are present.** If you find any bugs in the code, just hit us up and we will fix them as soon as possible (or you can create a PR).

Usage
#####

.. code-block:: python

    from pathlib import Path

    from raillabel_providerkit import validate

    scene_path = Path("path/to/scene.json")
    ontology_path = Path("path/to/ontology.yaml")  # ontology file that should be provided by us
    issues_in_scene = validate(scene_path, ontology_path)
    assert issues_in_scene == []

If this code does not raise any errors, you are good to go. If it does, read the content of the list `validate` returns carefully. It should tell you where the errors are. If you are unsure, contact your project partner or raise an issue on GitHub.

Under certain circumstances you might want to switch off certain validations. This should only be done if agreed upon with us. In this case, validate excepts use something like this

.. code-block:: python

    from pathlib import Path

    from raillabel_providerkit import validate

    scene_path = Path("path/to/scene.json")
    issues_in_scene = validate(scene_path, validate_for_dimensions=False)

If you have not been provided with an ontology file, just leave the field empty. The scene is then not checked against ontology issues.

Supported Ontologies
####################

Pre-built ontology parameter files are provided in the ``config/parameters/`` directory:

**OSDAR23** (``config/parameters/osdar23.yaml``)
    Original railway environment annotation ontology for the OSDAR23 dataset. Includes standard occlusion ranges (0-25%, 25-50%, 50-75%, 75-99%, 100%) and core railway classes.

**OSDAR26** (``config/parameters/osdar26.yaml``)
    Extended railway environment ontology featuring:

    - **25 object classes** for comprehensive railway environment annotation
    - Comprehensive signal aspects (Hp_0/1/2, Ks_1/2, Vr_0/1/2, Zs_2/2v/3/3v, Sh_0/1/2 in light and shape variants)
    - Updated occlusion ranges: 0-24%, 25-49%, 50-74%, 75-99%, 100%
    - Additional object classes: personal_item (suitcase, backpack, handbag, bag, etc.), pram (stroller, buggy, babySeat), scooter (eScooter, scooter, hoverboard)
    - Enhanced animal species coverage (dog, cat, racoon, badger, swan, sheep, cow, horse, pig, fox, wolf, wildBoar, deer, stork, rabbit, bird)
    - Complete railway infrastructure elements (track, switch, transition, catenary_pole, signal_pole, buffer_stop)
    - Hazard detection (flame, smoke)

**AutomatedTrain** (``config/parameters/automatedtrain.yaml``)
    Specialized ontology for automated train perception and safety-critical railway environment annotation:

    - **Safety-critical classes**: obstacle, platform, level_crossing, speed_sign
    - Switch state tracking (straight, diverging)
    - Emergency vehicle detection
    - Level crossing state monitoring (open, closing, closed, opening)
    - Boolean safety indicators for critical situations

Usage Examples
##############

.. code-block:: python

    from pathlib import Path
    from raillabel_providerkit import validate

    # Using OSDAR26 ontology
    scene_path = Path("path/to/scene.json")
    ontology_path = Path("config/parameters/osdar26.yaml")
    issues = validate(scene_path, ontology_path)

    # Using AutomatedTrain ontology
    ontology_path = Path("config/parameters/automatedtrain.yaml")
    issues = validate(scene_path, ontology_path)

Supported Sensors
#################

The sensor validation checks that all sensors in a scene have recognized names and correct types. Both OSDAR23 and OSDAR26 sensor naming conventions are supported.

**OSDAR23 Sensors:**

- RGB cameras: ``rgb_center``, ``rgb_left``, ``rgb_right``
- High-resolution RGB: ``rgb_highres_center``, ``rgb_highres_left``, ``rgb_highres_right``
- Long-range RGB: ``rgb_longrange_center``, ``rgb_longrange_left``, ``rgb_longrange_right``
- Infrared cameras: ``ir_center``, ``ir_left``, ``ir_right``
- Lidar: ``lidar``
- Radar: ``radar``
- GPS/IMU: ``gps_imu``

**OSDAR26 Sensors:**

- 12MP RGB cameras: ``rgb_12mp_left``, ``rgb_12mp_middle``, ``rgb_12mp_right``
- 5MP RGB cameras: ``rgb_5mp_left``, ``rgb_5mp_middle``, ``rgb_5mp_right``
- Infrared cameras: ``ir_left``, ``ir_middle``, ``ir_right``
- Merged lidar: ``lidar_merged``
- Cartesian radar: ``radar_cartesian``

Adding Custom Sensors
#####################

To add support for additional sensors, edit the ``SENSOR_METADATA`` dictionary in ``raillabel_providerkit/_util/_sensor_metadata.py``:

.. code-block:: python

    from raillabel.format import Camera, Lidar, Radar, GpsImu

    SENSOR_METADATA = {
        # ... existing sensors ...

        # Add your custom sensors
        "my_custom_camera": Camera,
        "my_custom_lidar": Lidar,
    }

Calibration Detection
#####################

The horizon validation automatically detects the calibration format (OSDAR23 vs OSDAR26) based on sensor naming patterns. OSDAR26 uses different extrinsics rotation axis conventions compared to OSDAR23.

The detection is performed once per scene by checking all sensor names. If any sensor matches the OSDAR26 pattern (e.g., ``rgb_12mp_left``, ``ir_middle``), the OSDAR26 calibration is applied to the entire scene.
