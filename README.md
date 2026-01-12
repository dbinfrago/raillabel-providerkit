<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# RailLabel Providerkit

<!-- prettier-ignore -->
![image](https://github.com/dbinfrago/raillabel-providerkit/actions/workflows/build-test-publish.yml/badge.svg)
![image](https://github.com/dbinfrago/raillabel-providerkit/actions/workflows/lint.yml/badge.svg)

A library for annotation providers of raillabel-formatted data.

# Documentation

<!-- prettier-ignore -->
Read the [full documentation on Github pages](https://dbinfrago.github.io/raillabel-providerkit).

# Installation

You can install the latest released version directly from PyPI.

```zsh
pip install raillabel-providerkit
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
pip install -e '.[docs,test]'
pre-commit install
```

# Command Line Usage

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

Note that you need to provide a project-specific ontology (in .yaml format) to make use of the ontology validation functionality! You can point raillabel_providerkit at it like this:

```zsh
python -m raillabel_providerkit /path/to/folder_containing_scenes/ /path/to/output_folder --ontology /path/to/project-ontology.yaml
```

## Supported Ontologies / Parameter Files

Pre-built ontology parameter files are provided in the `config/parameters/` directory:

| File | Dataset | Description |
|------|---------|-------------|
| `osdar23.yaml` | OSDAR23 | Original railway environment annotation ontology for the OSDAR23 dataset. Includes standard occlusion ranges (0-25%, 25-50%, 50-75%, 75-99%, 100%) and core railway classes. |
| `opendataset_v2.yaml` | Open Dataset v2 | Extended railway environment ontology with 25 object classes. Features comprehensive signal aspects (Hp, Ks, Vr, Zs, Sh variants), updated occlusion ranges (0-24%, 25-49%, 50-74%, 75-99%, 100%), and additional classes (personal_item, pram, scooter, flame, smoke). |
| `automatedtrain.yaml` | AutomatedTrain | Specialized ontology for automated train perception and safety-critical annotation. Includes additional classes for autonomous operation: obstacle detection, platform recognition, level crossings, and speed signs. Uses boolean attributes for safety-critical indicators. |

### Usage Instructions

To validate scenes against a specific ontology, specify the parameter file:

```zsh
# Using OpenDataset v2 ontology
python -m raillabel_providerkit /path/to/scenes/ /path/to/output/ --ontology config/parameters/opendataset_v2.yaml

# Using AutomatedTrain ontology
python -m raillabel_providerkit /path/to/scenes/ /path/to/output/ --ontology config/parameters/automatedtrain.yaml

# Using OSDAR23 ontology
python -m raillabel_providerkit /path/to/scenes/ /path/to/output/ --ontology config/parameters/osdar23.yaml
```

### OpenDataset v2 Classes

The OpenDataset v2 ontology supports the following 25 classes:
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

# Contributing

We'd love to see your bug reports and improvement suggestions! Please take a
look at our [guidelines for contributors](CONTRIBUTING.md) for details.

# Licenses

This project is compliant with the
[REUSE Specification Version 3.0](https://git.fsfe.org/reuse/docs/src/commit/d173a27231a36e1a2a3af07421f5e557ae0fec46/spec.md).

Copyright DB InfraGO AG, licensed under Apache 2.0 (see full text in
[LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt))

Dot-files are licensed under CC0-1.0 (see full text in
[LICENSES/CC0-1.0.txt](LICENSES/CC0-1.0.txt))
