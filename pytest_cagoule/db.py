import os
import sqlite3

DB_FILE = '.cagoule.db'


def db_exists():
    return os.path.exists(DB_FILE)


def get_connection():
    connection = sqlite3.connect(DB_FILE)
    connection.text_factory = bytes
    return connection
