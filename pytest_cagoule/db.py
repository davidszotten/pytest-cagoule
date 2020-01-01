import os
import sqlite3

from coverage import CoverageData
from coverage.numbits import register_sqlite_functions


def db_exists():
    coverage_data = CoverageData()
    return os.path.exists(coverage_data.data_filename())


def get_connection():
    coverage_data = CoverageData()
    connection = sqlite3.connect(coverage_data.data_filename())
    register_sqlite_functions(connection)
    connection.text_factory = bytes
    return connection
