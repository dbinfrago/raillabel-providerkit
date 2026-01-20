# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

"""GUI application for RailLabel Providerkit validation."""

import sys
import warnings
from pathlib import Path

try:
    from PyQt6.QtCore import QThread, pyqtSignal
    from PyQt6.QtWidgets import (
        QApplication,
        QComboBox,
        QFileDialog,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError as e:
    warnings.warn(
        "PyQt6 is not installed. Install with: pip install 'raillabel-providerkit[gui]'",
        stacklevel=2,
    )
    raise SystemExit(1) from e

from raillabel_providerkit import list_available_ontologies, validate
from raillabel_providerkit.ontologies import get_ontology_path


class ValidationWorker(QThread):
    """Worker thread for running validation in the background."""

    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(dict)  # results
    error = pyqtSignal(str)

    def __init__(self, input_folder: Path, output_folder: Path, ontology_path: Path | None) -> None:
        """Initialize the validation worker.

        Parameters
        ----------
        input_folder : Path
            Folder containing scene JSON files
        output_folder : Path
            Folder to write validation results
        ontology_path : Path | None
            Path to ontology YAML file, or None for no ontology validation
        """
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.ontology_path = ontology_path

    def run(self) -> None:
        """Run the validation process."""
        try:
            # Find all JSON files
            scene_files = list(self.input_folder.glob("**/*.json"))
            scene_files = [f for f in scene_files if not f.parent.name.startswith(".")]

            if not scene_files:
                self.error.emit("No JSON files found in the selected folder.")
                return

            # Create output folder
            self.output_folder.mkdir(parents=True, exist_ok=True)

            results = {"total": len(scene_files), "processed": 0, "errors": 0, "issues": 0}

            for i, scene_path in enumerate(scene_files):
                try:
                    issues = validate(scene_path, self.ontology_path)

                    # Write results to JSON
                    output_file = self.output_folder / scene_path.name.replace(
                        ".json", ".issues.json"
                    )
                    import json

                    with output_file.open("w") as f:
                        json.dump([issue.serialize() for issue in issues], f, indent=2)

                    results["processed"] += 1
                    results["issues"] += len(issues)

                except (OSError, ValueError, KeyError) as e:
                    results["errors"] += 1
                    warnings.warn(f"Error processing {scene_path}: {e}", stacklevel=2)

                self.progress.emit(i + 1, len(scene_files))

            self.finished.emit(results)

        except (OSError, ValueError) as e:
            self.error.emit(str(e))


class RailLabelGUI(QMainWindow):
    """Main GUI window for RailLabel Providerkit."""

    def __init__(self) -> None:  # noqa: PLR0915
        """Initialize the GUI."""
        super().__init__()
        self.setWindowTitle("RailLabel Providerkit - Validation Tool")
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("RailLabel Providerkit - Scene Validation")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Input folder selection
        input_group = QGroupBox("Input Folder (Scenes)")
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Select folder containing scene JSON files...")
        input_browse = QPushButton("Browse...")
        input_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Output folder selection
        output_group = QGroupBox("Output Folder (Results)")
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select folder for validation results...")
        output_browse = QPushButton("Browse...")
        output_browse.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_browse)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Ontology selection
        ontology_group = QGroupBox("Ontology / Parameter File")
        ontology_layout = QVBoxLayout()

        # Built-in ontology dropdown
        builtin_layout = QHBoxLayout()
        builtin_layout.addWidget(QLabel("Built-in Ontology:"))
        self.ontology_dropdown = QComboBox()
        self.ontology_dropdown.addItem("(No ontology validation)", None)
        for ont in list_available_ontologies():
            self.ontology_dropdown.addItem(ont, ont)
        self.ontology_dropdown.currentIndexChanged.connect(self.on_builtin_selected)
        builtin_layout.addWidget(self.ontology_dropdown)
        ontology_layout.addLayout(builtin_layout)

        # Custom ontology file
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom Ontology:"))
        self.custom_ontology = QLineEdit()
        self.custom_ontology.setPlaceholderText("Or select a custom ontology YAML file...")
        custom_browse = QPushButton("Browse...")
        custom_browse.clicked.connect(self.browse_ontology)
        custom_layout.addWidget(self.custom_ontology)
        custom_layout.addWidget(custom_browse)
        ontology_layout.addLayout(custom_layout)

        ontology_group.setLayout(ontology_layout)
        layout.addWidget(ontology_group)

        # Validate button
        self.validate_btn = QPushButton("Start Validation")
        self.validate_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 14px; padding: 10px;"
        )
        self.validate_btn.clicked.connect(self.start_validation)
        layout.addWidget(self.validate_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status/Log area
        status_label = QLabel("Status:")
        layout.addWidget(status_label)
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        layout.addWidget(self.status_text)

        # Initialize
        self.worker = None
        self.log("Ready. Select input/output folders and start validation.")

    def log(self, message: str) -> None:
        """Add a message to the status log."""
        self.status_text.append(message)

    def browse_input(self) -> None:
        """Open folder browser for input folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_path.setText(folder)

    def browse_output(self) -> None:
        """Open folder browser for output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path.setText(folder)

    def browse_ontology(self) -> None:
        """Open file browser for custom ontology."""
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Ontology File", "", "YAML Files (*.yaml *.yml)"
        )
        if file:
            self.custom_ontology.setText(file)
            self.ontology_dropdown.setCurrentIndex(0)  # Reset dropdown

    def on_builtin_selected(self, index: int) -> None:
        """Handle built-in ontology selection."""
        if index > 0:  # Not "(No ontology validation)"
            self.custom_ontology.clear()

    def start_validation(self) -> None:
        """Start the validation process."""
        # Validate inputs
        if not self.input_path.text():
            QMessageBox.warning(self, "Missing Input", "Please select an input folder.")
            return

        if not self.output_path.text():
            QMessageBox.warning(self, "Missing Output", "Please select an output folder.")
            return

        input_folder = Path(self.input_path.text())
        output_folder = Path(self.output_path.text())

        if not input_folder.exists():
            QMessageBox.warning(self, "Invalid Input", "Input folder does not exist.")
            return

        # Determine ontology path
        ontology_path = None
        if self.custom_ontology.text():
            ontology_path = Path(self.custom_ontology.text())
            if not ontology_path.exists():
                QMessageBox.warning(self, "Invalid Ontology", "Ontology file does not exist.")
                return
        elif self.ontology_dropdown.currentIndex() > 0:
            ont_name = self.ontology_dropdown.currentData()
            ontology_path = get_ontology_path(ont_name)

        # Disable UI during validation
        self.validate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Clear log
        self.status_text.clear()
        self.log(f"Starting validation of: {input_folder}")
        if ontology_path:
            self.log(f"Using ontology: {ontology_path.name}")
        else:
            self.log("No ontology validation enabled")

        # Start worker thread
        self.worker = ValidationWorker(input_folder, output_folder, ontology_path)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, current: int, total: int) -> None:
        """Update progress bar."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.log(f"Processing: {current}/{total}")

    def on_finished(self, results: dict) -> None:
        """Handle validation completion."""
        self.validate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        self.log("=" * 50)
        self.log("Validation Complete!")
        self.log(f"Total files: {results['total']}")
        self.log(f"Processed: {results['processed']}")
        self.log(f"Errors: {results['errors']}")
        self.log(f"Issues found: {results['issues']}")
        self.log(f"Results saved to: {self.output_path.text()}")

        QMessageBox.information(
            self,
            "Validation Complete",
            f"Processed {results['processed']} files.\n"
            f"Found {results['issues']} issues.\n"
            f"Results saved to {self.output_path.text()}",
        )

    def on_error(self, error_msg: str) -> None:
        """Handle validation error."""
        self.validate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.log(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Validation Error", error_msg)


def launch_gui() -> None:
    """Launch the RailLabel Providerkit GUI."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern look on all platforms

    window = RailLabelGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()
