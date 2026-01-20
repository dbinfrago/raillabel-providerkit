# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import raillabel


class LoaderABC(ABC):
    """Abstract base class of the annotation file loaders.

    For every annotation format, that can be loaded via raillabel, a loader class should exists,
    that inherites from this class.

    Attributes
    ----------
    scene: raillabel.Scene
        Loaded raillabel.Scene with the data.
    warnings: t.List[str]
        List of warning strings, that have been found during the execution of load().
    SCHEMA_PATH: Path
        Absolute path to the JSON schema.

    """

    scene: raillabel.Scene
    warnings: list[str]
    SCHEMA_PATH: Path

    @abstractmethod
    def load(self, data: dict, validate: bool = True) -> raillabel.Scene:
        """Load JSON-data into a raillabel.Scene.

        Any non-critical errors are stored in the warnings-property.

        Parameters
        ----------
        data: dict
            A dictionary loaded from a JSON-file.
        validate: bool
            If True, the annotation data is validated via the respective schema. This is highly
            recommended, as not validating the data may lead to Errors during loading or while
            handling the scene. However, validating may increase the loading time. Default is True.

        Returns
        -------
        scene: raillabel.Scene
            The loaded scene with the data.

        """
        raise NotImplementedError

    @abstractmethod
    def supports(self, data: dict) -> bool:
        """Determine if the loader class is suitable for the data.

        This is performed based on hints in the data structure and can therefore be done
        efficiently.

        Parameters
        ----------
        data: dict
            A dictionary loaded from a JSON-file.

        Returns
        -------
        bool:
            If True, the Loader class is suitable for the data.

        """
        raise NotImplementedError
