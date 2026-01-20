<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: MIT
 -->

# RailLabel Providerkit

<!-- prettier-ignore -->
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/dbinfrago/raillabel-providerkit/releases)
![Build](https://github.com/dbinfrago/raillabel-providerkit/actions/workflows/build-test-publish.yml/badge.svg)
![Lint](https://github.com/dbinfrago/raillabel-providerkit/actions/workflows/lint.yml/badge.svg)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)

A library for annotation providers of raillabel-formatted data.

# Documentation

<!-- prettier-ignore -->
Read the [full documentation on Github pages](https://dbinfrago.github.io/raillabel-providerkit).

# Installation

You can install the latest released version directly from PyPI.

```zsh
pip install raillabel-providerkit
```

For users who prefer a graphical interface (Mac and Windows):

```zsh
pip install raillabel-providerkit[gui]
```

To set up a development environment, clone the project and install it into a
virtual environment.

```zsh
# Note that contributors should clone via ssh instead as GitHub does not allow pushing via https!
git clone https://github.com/dbinfrago/raillabel-providerkit
cd raillabel-providerkit
python -m venv .venv

source .venv/bin/activate.sh  # for Linux / Mac
.venv\Scripts\activate  # for Windows

pip install -U pip pre-commit
pip install -e '.[docs,test,gui]'
pre-commit install
```

# Usage

## GUI Application (Recommended for Non-CLI Users)

For users who prefer a graphical interface instead of the command line, launch the GUI with:

```zsh
python -m raillabel_providerkit.gui
```

Or from Python:

```python
from raillabel_providerkit.gui import launch_gui
launch_gui()
```

The GUI provides:
- 📁 Easy folder selection for input scenes and output results
- 🎯 Built-in ontology selection (OSDAR26, AutomatedTrain, OSDAR23)
- 📊 Real-time progress tracking
- ✅ Visual validation results

**Requirements**: Install with `pip install raillabel-providerkit[gui]`

## Command Line Usage

You can use the validation functionality directly from the command line. To get a list of supported arguments, use this command:

```zsh
python -m raillabel_providerkit --help
```

To simply validate all scenes in a folder and output any detected issues to an output folder (in .json format), use this command:

```zsh
python -m raillabel_providerkit /path/to/folder_containing_scenes/ /path/to/output_folder
```

If you want to output in .csv format instead of .json format, you can use this command:

```zsh
python -m raillabel_providerkit /path/to/folder_containing_scenes/ /path/to/output_folder --use-csv --no-json
```

## Using Built-in Ontologies

RailLabel Providerkit comes with pre-built ontology parameter files that can be used directly:

```zsh
# Using OSDAR26 ontology
python -m raillabel_providerkit /path/to/scenes/ /path/to/output/ --ontology config/parameters/osdar26.yaml

# Using AutomatedTrain ontology
python -m raillabel_providerkit /path/to/scenes/ /path/to/output/ --ontology config/parameters/automatedtrain.yaml
```

Or programmatically from Python:

```python
from raillabel_providerkit import validate, get_ontology_path

# Using a built-in ontology
ontology_path = get_ontology_path("osdar26")
issues = validate("path/to/scene.json", ontology=ontology_path)

# List available ontologies
from raillabel_providerkit import list_available_ontologies
print(list_available_ontologies())  # ['osdar23', 'osdar26', 'automatedtrain']
```

You can also provide a custom ontology file:

```zsh
python -m raillabel_providerkit /path/to/folder_containing_scenes/ /path/to/output_folder --ontology /path/to/custom-ontology.yaml
```

## Supported Ontologies / Parameter Files

Pre-built ontology parameter files are provided and accessible via the API:

| Ontology | Name | Dataset | Description |
|----------|------|---------|-------------|
| `osdar23` | OSDAR23 | OSDAR23 | Original railway environment annotation ontology. Includes standard occlusion ranges (0-25%, 25-50%, 50-75%, 75-99%, 100%) and core railway classes. |
| `osdar26` | OSDAR26 | OSDAR26 | Extended railway environment ontology with 25 object classes. Features comprehensive signal aspects (Hp, Ks, Vr, Zs, Sh variants), updated occlusion ranges (0-24%, 25-49%, 50-74%, 75-99%, 100%), and additional classes. |
| `automatedtrain` | AutomatedTrain | AutomatedTrain | Specialized ontology for automated train perception and safety-critical annotation. Includes obstacle detection, platform recognition, level crossings, speed signs. |

### OSDAR26 Classes (25 total)
- **Persons**: `person`, `crowd`
- **Personal Mobility**: `personal_item`, `pram`, `scooter`, `wheelchair`
- **Vehicles**: `bicycle`, `group_of_bicycles`, `motorcycle`, `road_vehicle`
- **Animals**: `animal`, `group_of_animals`
- **Railway Vehicles**: `train`, `wagon`, `drag_shoe`
- **Track Infrastructure**: `track`, `transition`, `switch`
- **Signaling**: `signal`, `signal_pole`, `signal_bridge`, `catenary_pole`, `buffer_stop`
- **Hazards**: `flame`, `smoke`

### AutomatedTrain Classes

The AutomatedTrain ontology supports safety-critical classes for automated train operation:
- **Core Classes**: `person`, `crowd`, `train`, `wagon`, `track`, `transition`, `switch`
- **Signaling**: `signal`, `signal_pole`, `signal_bridge`, `catenary_pole`, `buffer_stop`
- **Vehicles**: `road_vehicle`, `bicycle`, `motorcycle`, `animal`
- **Safety-Critical**: `obstacle`, `platform`, `level_crossing`, `speed_sign`

## Supported Sensors

RailLabel Providerkit supports sensors from both OSDAR23 and OSDAR26 datasets. The sensor validation checks that all sensors in a scene have recognized names and correct types.

### OSDAR23 Sensors

| Sensor ID | Type | Description |
|-----------|------|-------------|
| `rgb_center`, `rgb_left`, `rgb_right` | Camera | Standard RGB cameras |
| `rgb_highres_center`, `rgb_highres_left`, `rgb_highres_right` | Camera | High-resolution RGB cameras |
| `rgb_longrange_center`, `rgb_longrange_left`, `rgb_longrange_right` | Camera | Long-range RGB cameras |
| `ir_center`, `ir_left`, `ir_right` | Camera | Infrared cameras |
| `lidar` | Lidar | Single lidar sensor |
| `radar` | Radar | Single radar sensor |
| `gps_imu` | GpsImu | GPS/IMU sensor |

### OSDAR26 Sensors

| Sensor ID | Type | Description |
|-----------|------|-------------|
| `rgb_12mp_left`, `rgb_12mp_middle`, `rgb_12mp_right` | Camera | 12 megapixel RGB cameras |
| `rgb_5mp_left`, `rgb_5mp_middle`, `rgb_5mp_right` | Camera | 5 megapixel RGB cameras |
| `ir_left`, `ir_middle`, `ir_right` | Camera | Infrared cameras |
| `lidar_merged` | Lidar | Merged lidar data |
| `radar_cartesian` | Radar | Radar in cartesian coordinates |

### Adding Custom Sensors

To add support for additional sensors, edit the `SENSOR_METADATA` dictionary in `raillabel_providerkit/_util/_sensor_metadata.py`:

```python
from raillabel.format import Camera, Lidar, Radar, GpsImu

SENSOR_METADATA = {
    # ... existing sensors ...
    
    # Add your custom sensors
    "my_custom_camera": Camera,
    "my_custom_lidar": Lidar,
}
```

## Calibration Detection

The horizon validation automatically detects the calibration format (OSDAR23 vs OSDAR26) based on sensor naming patterns. OSDAR26 uses different extrinsics rotation axis conventions compared to OSDAR23. The detection is performed once per scene by checking all sensor names - if any sensor matches the OSDAR26 pattern (e.g., `rgb_12mp_left`, `ir_middle`), the OSDAR26 calibration is applied to the entire scene.

# Contributing

We'd love to see your bug reports and improvement suggestions! Please take a
look at our [guidelines for contributors](CONTRIBUTING.md) for details.

# Licenses

This project is compliant with the
[REUSE Specification Version 3.0](https://git.fsfe.org/reuse/docs/src/commit/d173a27231a36e1a2a3af07421f5e557ae0fec46/spec.md).

Copyright DB InfraGO AG, licensed under MIT (see full text in [LICENSE](LICENSE))

**Dual Licensing**:
- **Main code (MIT)**: Permissive open-source license allowing commercial use, modification, and distribution with minimal restrictions
- **Configuration files (CC0-1.0)**: Public domain dedication for ontology files and configuration data
- **Documentation**: Available under both MIT and Apache 2.0 where applicable

See individual files for their specific licenses.
