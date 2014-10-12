from functools import partial
import sqlite3

from pytest_cagoule import db
from pytest_cagoule import select

pytest_plugins = "pytester",


def get_test_connection(testdir):
    path = str(testdir.tmpdir.join(db.DB_FILE))
    connection = sqlite3.connect(path)
    return connection


def test_basic(testdir, monkeypatch):
    test_file = testdir.makepyfile("""
        def test_foo():
            assert True
    """)
    testdir.runpytest("--cagoule-capture")

    get_connection = partial(get_test_connection, testdir)
    monkeypatch.setattr(select, 'get_connection', get_connection)
    assert select.get_node_ids([str(test_file)]) == ['test_basic.py::test_foo']
