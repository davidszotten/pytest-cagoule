import os
import sqlite3

from coverage import Coverage
from coverage.numbits import register_sqlite_functions


def get_coverage_config():
    cov = Coverage()
    return cov.config


def get_data_file():
    config = get_coverage_config()
    return config.data_file


def db_exists():
    return os.path.exists(get_data_file())


def get_connection():
    connection = sqlite3.connect(get_data_file())
    register_sqlite_functions(connection)
    connection.text_factory = bytes
    return connection
