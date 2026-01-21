<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: MIT
 -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Horizon Validation Tolerance (NEW)
- **Configurable Tolerance Buffer**: Reduce false positives from horizon calculations
  - `horizon_tolerance_percent` parameter in `validate()` and `validate_horizon()`
  - CLI option: `--horizon-tolerance FLOAT` (percentage above horizon line)
  - **Default: 10.0%** - sensible default to account for typical calibration variations
  - Annotations within tolerance buffer are considered valid
  - Example: `--horizon-tolerance 15.0` accepts annotations up to 15% above calculated horizon
  - **Applies only to track and transition annotations** - other object types are not checked
  - Useful when horizon calculations are slightly inaccurate due to calibration variations

### Fixed

#### Horizon Calculation (CRITICAL FIX)
- **Complete rewrite of horizon calculation algorithm**
  - Previous implementation had fundamental bugs causing 96%+ false positives
  - New implementation uses camera pitch angle directly from extrinsics rotation matrix
  - Works correctly with all calibration formats (OSDAR23, OSDAR26, etc.)
  - No longer requires calibration-specific workarounds
  - Horizon is now correctly positioned based on camera tilt angle
  - Removed complex and incorrect 3D point projection approach
  - Results: 140 issues at 0% tolerance (was 2435), 4 issues at 10% tolerance

#### Multi-Scene Export (NEW)
- **Batch Export Functionality**: Export multiple scenes to different formats at once
  - `export_scenes(input_folder, output_folder, formats)`: Core export function
  - Supported formats: JSON (raillabel format), CSV (annotations, metadata, sensors, objects)
  - Recursive processing of all scene files in input folder
  - Progress bar with export statistics
- **CLI Export Subcommand**: `python -m raillabel_providerkit export`
  - `--format json`: Export to JSON format
  - `--format csv`: Export to CSV format (4 separate files per scene)
  - Supports multiple formats: `--format json --format csv`
- **CSV Export Structure**:
  - `{scene}_annotations.csv`: All annotations with attributes
  - `{scene}_metadata.csv`: Scene metadata
  - `{scene}_objects.csv`: Object definitions
  - `{scene}_sensors.csv`: Sensor configurations

#### OSDAR26 Sensor Support
- **Full OSDAR26 sensor coverage**: All OSDAR26 sensors now recognized and validated
  - 12MP RGB cameras: `rgb_12mp_left`, `rgb_12mp_middle`, `rgb_12mp_right`
  - 5MP RGB cameras: `rgb_5mp_left`, `rgb_5mp_middle`, `rgb_5mp_right`
  - Infrared cameras: `ir_left`, `ir_middle`, `ir_right`
  - Merged lidar: `lidar_merged`
  - Cartesian radar: `radar_cartesian`

#### Ontology Management
- **Built-in Ontology Files**: Three pre-configured ontology files now bundled with the package
  - `osdar26`: Extended railway environment ontology with 25 object classes
  - `automatedtrain`: Safety-critical classes for automated train perception
  - `osdar23`: Original OSDAR23 dataset ontology
- **New API Functions**:
  - `get_ontology_path(ontology_name)`: Retrieve path to built-in ontology files
  - `list_available_ontologies()`: List all available built-in ontologies
- **Package Distribution**: Ontology files included in package via `MANIFEST.in`

#### GUI Application (NEW)
- **PyQt6-based GUI** for users who prefer graphical interfaces over CLI
  - Easy folder selection for input scenes and output results
  - Built-in ontology dropdown (OSDAR26, AutomatedTrain, OSDAR23)
  - Custom ontology file browser support
  - Real-time progress tracking with visual progress bar
  - Multi-threaded validation (non-blocking UI)
  - Detailed status logging
- **Installation**: `pip install raillabel-providerkit[gui]`
- **Launch**: `python -m raillabel_providerkit.gui`
- **Platform Support**: macOS, Windows, and Linux

#### OSDAR26 Ontology
- **25 Object Classes** for comprehensive railway environment annotation:
  - Persons: `person`, `crowd`
  - Personal Mobility: `personal_item`, `pram`, `scooter`, `wheelchair`
  - Vehicles: `bicycle`, `group_of_bicycles`, `motorcycle`, `road_vehicle`
  - Animals: `animal`, `group_of_animals`
  - Railway Vehicles: `train`, `wagon`, `drag_shoe`
  - Track Infrastructure: `track`, `transition`, `switch`
  - Signaling: `signal`, `signal_pole`, `signal_bridge`, `catenary_pole`, `buffer_stop`
  - Hazards: `flame`, `smoke`
- **Enhanced Signal Aspects**: 29 variants (Hp_0/1/2, Ks_1/2, Vr_0/1/2, Zs_2/2v/3/3v, Sh_0/1/2 in light/shape)
- **Updated Occlusion Ranges**: 0-24%, 25-49%, 50-74%, 75-99%, 100%
- **Extended Animal Species**: 17+ species including racoon, badger, swan, sheep, cow, horse, pig, fox, wolf, wildBoar, deer, stork, rabbit

#### AutomatedTrain Ontology
- **Safety-Critical Classes** for automated train operation:
  - `obstacle`: Debris, rocks, trees, construction materials on track
  - `platform`: Platform detection and side identification
  - `level_crossing`: Crossing state monitoring (open, closing, closed, opening)
  - `speed_sign`: Speed limit detection with value attribute
- **Enhanced Switch Tracking**: State attribute (straight, diverging)
- **Emergency Detection**: `isEmergency` attribute for road_vehicle class
- **Boolean Safety Indicators**: Critical safety flags throughout ontology

#### Documentation
- **API Reference Documentation**: Comprehensive Sphinx documentation for new APIs
- **GUI User Guide**: Complete GUI documentation with screenshots and troubleshooting
- **Usage Examples**: Python and CLI examples for all new features
- **How-To Guides**: Updated validation guides with ontology selection examples

#### Tests
- **15 New Tests** for ontology manager functionality:
  - `test_ontologies.py`: Comprehensive test suite for `get_ontology_path()` and `list_available_ontologies()`
  - Content validation tests for all three ontologies
  - Integration tests with validation system
- **All 380 Tests Passing** (365 existing + 15 new)

### Changed

#### License Migration
- **BREAKING**: Migrated from Apache-2.0 to MIT License
  - More permissive for commercial and open-source use
  - Minimal restrictions on usage, modification, and distribution
- **Dual Licensing**: Configuration files remain CC0-1.0 (public domain)
- **Updated Headers**: All 89 Python files updated to MIT license
- **Documentation**: LICENSE file and all SPDX headers updated

#### API Changes
- **New Exports** in `raillabel_providerkit.__init__.py`:
  - `get_ontology_path`
  - `list_available_ontologies`
- **Backward Compatible**: All existing APIs remain unchanged

#### Package Structure
- **New Modules**:
  - `raillabel_providerkit/ontologies/`: Built-in ontology files
  - `raillabel_providerkit/ontologies/manager.py`: Ontology management API
  - `raillabel_providerkit/gui/`: GUI application module
- **Distribution**: `MANIFEST.in` ensures ontology YAML files are included

#### Documentation
- **README.md**:
  - Added GUI usage instructions
  - Enhanced ontology documentation with comparison table
  - Programmatic API examples
  - Dual-license information
- **Sphinx Docs**:
  - New API reference page
  - GUI tutorial (How-To #3)
  - Updated validation guides

### Fixed
- None in this release

### Deprecated
- None in this release

### Removed
- Apache-2.0 as primary license (replaced with MIT)

### Security
- None in this release

## Installation & Migration

### New Installation

```bash
# Base package
pip install raillabel-providerkit

# With GUI support
pip install raillabel-providerkit[gui]
```

### Upgrading from Previous Version

```bash
pip install --upgrade raillabel-providerkit

# Add GUI support
pip install --upgrade raillabel-providerkit[gui]
```

### Breaking Changes

1. **License Change**: The project is now licensed under MIT instead of Apache-2.0. If your project has specific license requirements, please review the new license terms.

2. **Python API Additions Only**: No breaking changes to existing APIs. All new functionality is additive.

## Usage Examples

### Using Built-in Ontologies (NEW)

```python
from raillabel_providerkit import validate, get_ontology_path

# Old way (still works)
issues = validate("scene.json", ontology="path/to/ontology.yaml")

# New way (recommended)
ontology_path = get_ontology_path("osdar26")
issues = validate("scene.json", ontology=ontology_path)
```

### GUI Application (NEW)

```bash
# Launch GUI
python -m raillabel_providerkit.gui
```

```python
# Or from Python
from raillabel_providerkit.gui import launch_gui
launch_gui()
```

### List Available Ontologies (NEW)

```python
from raillabel_providerkit import list_available_ontologies

print(list_available_ontologies())
# ['osdar26', 'automatedtrain', 'osdar23']
```

## Contributors

- DB InfraGO AG and contributors

## License

Copyright DB InfraGO AG, licensed under MIT License.

See [LICENSE](LICENSE) for full text.
