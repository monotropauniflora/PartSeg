import warnings

import pytest

from qtpy.QtWidgets import QApplication


@pytest.fixture
def simple_handler(*args):
    pass


@pytest.fixture(autouse=True, scope="session")
def my_fixture(qapp):
    # setup_stuff
    yield
    qapp.quit()
    # teardown_stuff


@pytest.fixture
def qtbot(qtbot):
    """A modified qtbot fixture that makes sure no widgets have been leaked."""
    initial = QApplication.topLevelWidgets()
    yield qtbot
    QApplication.processEvents()
    leaks = set(QApplication.topLevelWidgets()).difference(initial)
    # still not sure how to clean up some of the remaining vispy
    # vispy.app.backends._qt.CanvasBackendDesktop widgets...
    if any([n.__class__.__name__ != "CanvasBackendDesktop" for n in leaks]):
        raise AssertionError(f"Widgets leaked!: {leaks}")
    if leaks:
        warnings.warn(f"Widgets leaked!: {leaks}")
