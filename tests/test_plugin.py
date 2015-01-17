# coding: utf-8

from functools import partial
import sqlite3

import pytest

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


@pytest.mark.parametrize('val', ('foo', 'föö'))
def test_nonascii(val):
    # make sure plugin captures nodeid ok
    pass


@pytest.mark.parametrize('val', ('1', 1))
def test_same_as_strings(val):
    # make sure plugin captures nodeid ok
    pass
