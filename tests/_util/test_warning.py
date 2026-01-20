# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: MIT

import pytest
from raillabel_providerkit._util._warning import _warning, _WarningsLogger


def test_issue_warning():
    with _WarningsLogger() as logger:
        _warning("lorem ipsum")

    assert logger.warnings == ["lorem ipsum"]


def test_handover_exception():
    with pytest.raises(RuntimeError):
        with _WarningsLogger():
            raise RuntimeError("weewoo something went wrong")


def test_clear_warnings():
    with _WarningsLogger():
        _warning("lorem ipsum")

    with _WarningsLogger() as logger2:
        pass

    assert len(logger2.warnings) == 0


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
