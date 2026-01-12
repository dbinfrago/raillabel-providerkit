..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: MIT

====================
API Reference
====================

Validation
##########

.. automodule:: raillabel_providerkit.validation.validate
   :members:
   :undoc-members:
   :show-inheritance:

Ontologies
##########

Built-in Ontology Management
=============================

.. automodule:: raillabel_providerkit.ontologies.manager
   :members:
   :undoc-members:
   :show-inheritance:

The ``raillabel_providerkit`` provides built-in ontology files that can be used for validation without managing external files.

Available Ontologies
--------------------

**OpenDataset v2** (``opendataset_v2``)
    Extended railway environment ontology with 25 object classes. Features comprehensive signal aspects 
    (Hp, Ks, Vr, Zs, Sh variants), updated occlusion ranges (0-24%, 25-49%, 50-74%, 75-99%, 100%), 
    and classes for personal_item, pram, scooter, flame, smoke.

**AutomatedTrain** (``automatedtrain``)
    Specialized ontology for automated train perception and safety-critical annotation. 
    Includes obstacle detection, platform recognition, level crossings, and speed signs.

**OSDAR23** (``osdar23``)
    Original railway environment annotation ontology for the OSDAR23 dataset. 
    Standard occlusion ranges (0-25%, 25-50%, 50-75%, 75-99%, 100%).

Usage Examples
--------------

.. code-block:: python

   from raillabel_providerkit import validate, get_ontology_path, list_available_ontologies

   # List available ontologies
   ontologies = list_available_ontologies()
   print(ontologies)  # ['opendataset_v2', 'automatedtrain', 'osdar23']

   # Get ontology path and validate
   ontology_path = get_ontology_path("opendataset_v2")
   issues = validate("scene.json", ontology=ontology_path)

   # Validate with AutomatedTrain ontology
   ontology_path = get_ontology_path("automatedtrain")
   issues = validate("scene.json", ontology=ontology_path)

Conversion
##########

.. automodule:: raillabel_providerkit.convert.convert
   :members:
   :undoc-members:
   :show-inheritance:

Format Handling
###############

Understand.AI Format
====================

.. automodule:: raillabel_providerkit.format.understand_ai
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
##########

.. automodule:: raillabel_providerkit.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
