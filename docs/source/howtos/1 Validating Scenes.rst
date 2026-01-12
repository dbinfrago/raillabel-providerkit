..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: Apache-2.0

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

**OpenDataset v2** (``config/parameters/opendataset_v2.yaml``)
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

    # Using OpenDataset v2 ontology
    scene_path = Path("path/to/scene.json")
    ontology_path = Path("config/parameters/opendataset_v2.yaml")
    issues = validate(scene_path, ontology_path)

    # Using AutomatedTrain ontology
    ontology_path = Path("config/parameters/automatedtrain.yaml")
    issues = validate(scene_path, ontology_path)
