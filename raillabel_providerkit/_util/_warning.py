# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import typing as t
from io import StringIO
from types import TracebackType


class _WarningsLogger:
    warnings: t.ClassVar[list[str]] = []

    def __enter__(self) -> None:
        logger = logging.getLogger("loader_warnings")
        warnings_stream = StringIO()
        handler = logging.StreamHandler(warnings_stream)
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)

        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        logger = logging.getLogger("loader_warnings")
        stream = logger.handlers[-1].stream
        stream.seek(0)

        warnings_list = stream.getvalue().split("\n")

        if len(warnings_list) > 0:
            warnings_list = warnings_list[:-1]

        self.warnings = warnings_list


def _warning(message: str) -> logging.Logger:
    """Create a loader warning."""
    logging.getLogger("loader_warnings").warning(message)
