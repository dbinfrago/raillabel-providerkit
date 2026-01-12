..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: MIT

===========================
3 Using the GUI Application
===========================

Overview
########

For users who prefer a graphical interface over the command line, RailLabel Providerkit provides a PyQt6-based GUI application. The GUI offers an intuitive way to validate railway annotation scenes without writing code or using terminal commands.

.. note::
   The GUI provides folder selection, built-in ontology support, progress tracking, and detailed validation results.

Installation
############

The GUI requires PyQt6, which is not included in the base installation. Install it using:

.. code-block:: bash

   pip install raillabel-providerkit[gui]

For development environments:

.. code-block:: bash

   pip install -e '.[gui]'

Launching the GUI
#################

There are multiple ways to launch the GUI:

From Command Line
=================

.. code-block:: bash

   python -m raillabel_providerkit.gui

From Python
===========

.. code-block:: python

   from raillabel_providerkit.gui import launch_gui
   launch_gui()

Features
########

The GUI provides the following features:

Input/Output Management
=======================

- **Input Folder Selection**: Browse and select folders containing scene JSON files
- **Output Folder Selection**: Choose where validation results should be saved
- **Recursive Processing**: Automatically finds all JSON files in subdirectories

Ontology Selection
==================

Built-in Ontologies
-------------------

Select from three pre-configured ontologies via dropdown:

- **OpenDataset v2**: Extended railway environment (25 classes)
- **AutomatedTrain**: Safety-critical automated train perception
- **OSDAR23**: Original OSDAR23 dataset ontology

Custom Ontologies
-----------------

Browse and select custom YAML ontology files for project-specific validation requirements.

Validation Process
==================

- **Real-time Progress**: Visual progress bar showing current file being processed
- **Status Log**: Detailed logging of validation steps and results
- **Multi-threaded**: Validation runs in background thread, keeping UI responsive

Results
=======

- **JSON Output**: Validation issues saved as `*.issues.json` files
- **Summary Statistics**: Total files processed, issues found, errors encountered
- **Error Handling**: Clear error messages for invalid inputs or processing failures

User Interface Components
#########################

Input Section
=============

- **Input Path Field**: Displays selected input folder path
- **Browse Button**: Opens folder selection dialog

Output Section
==============

- **Output Path Field**: Displays selected output folder path
- **Browse Button**: Opens folder selection dialog

Ontology Section
================

- **Built-in Dropdown**: Quick selection of pre-configured ontologies
- **Custom Path Field**: Manual entry or browsing for custom ontology files
- **Custom Browse Button**: Opens file selection dialog (YAML files only)

Validation Controls
===================

- **Start Validation Button**: Initiates the validation process
- **Progress Bar**: Shows validation progress (appears during processing)
- **Status Log**: Scrollable text area displaying validation steps and results

Usage Guide
###########

Step-by-Step Validation
========================

1. **Launch the Application**

   .. code-block:: bash

      python -m raillabel_providerkit.gui

2. **Select Input Folder**

   Click "Browse..." next to "Input Folder" and select the directory containing your scene JSON files.

3. **Select Output Folder**

   Click "Browse..." next to "Output Folder" and choose where results should be saved.

4. **Choose Ontology**

   - For built-in ontologies: Select from dropdown (e.g., "OpenDataset v2")
   - For custom ontologies: Click "Browse..." under "Custom Ontology" and select your YAML file

5. **Start Validation**

   Click the green "Start Validation" button. The progress bar will appear and update as files are processed.

6. **Review Results**

   - Check the status log for detailed information
   - Find validation results in the output folder as `*.issues.json` files
   - A summary dialog appears when validation completes

Example Workflow
================

**Validating OpenDataset v2 Scenes**:

1. Input folder: ``/path/to/scenes/``
2. Output folder: ``/path/to/results/``
3. Ontology: Select "OpenDataset v2" from dropdown
4. Click "Start Validation"

**Using Custom Ontology**:

1. Input folder: ``/path/to/project/scenes/``
2. Output folder: ``/path/to/project/validation/``
3. Custom ontology: Browse to ``/path/to/custom_ontology.yaml``
4. Click "Start Validation"

Troubleshooting
###############

GUI Won't Start
===============

**Issue**: PyQt6 import error

**Solution**:

.. code-block:: bash

   pip install 'raillabel-providerkit[gui]'

Make sure to use quotes around ``raillabel-providerkit[gui]`` in zsh/bash.

No Files Found
==============

**Issue**: "No JSON files found in the selected folder"

**Solution**:

- Verify the input folder contains JSON files
- Check that files have ``.json`` extension
- Ensure you selected the correct folder (not a subfolder)

Validation Errors
=================

**Issue**: Validation fails with errors

**Solution**:

- Check the status log for specific error messages
- Verify JSON files are valid RailLabel format
- Ensure ontology file (if custom) is valid YAML
- Check file permissions (read access for input, write access for output)

Performance Tips
################

Large Datasets
==============

For validating hundreds or thousands of scenes:

- Use SSD storage for faster I/O
- Ensure sufficient disk space for results
- Monitor the status log for individual file errors
- Consider splitting very large datasets into batches

Memory Usage
============

The GUI processes files sequentially to manage memory usage. If you encounter memory issues:

- Close other applications
- Process smaller batches
- Use the command-line interface for very large datasets

Technical Details
#################

Architecture
============

- **Framework**: PyQt6 6.4.0+
- **Threading**: QThread for background validation
- **Signals**: Qt signals/slots for UI updates
- **Error Handling**: Try-except with user-friendly messages

Platform Support
================

- **macOS**: Fully supported (tested on macOS 11.0+)
- **Windows**: Fully supported (tested on Windows 10+)
- **Linux**: Supported (requires X11 or Wayland display server)

Dependencies
============

.. code-block:: text

   PyQt6>=6.4.0
   raillabel-providerkit (base package)

Advanced Usage
##############

Scripted GUI Launch
===================

You can launch the GUI from Python scripts:

.. code-block:: python

   #!/usr/bin/env python3
   from raillabel_providerkit.gui import launch_gui

   if __name__ == "__main__":
       launch_gui()

Batch Processing
================

For automated batch processing with GUI monitoring, consider:

1. Use GUI for initial validation and result review
2. Use CLI for automated/scripted batch processing
3. Use API for integration into larger workflows

See :doc:`1 Validating Scenes` for CLI and API usage.
