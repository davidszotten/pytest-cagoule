import os
import sqlite3

from cagoule import DB_FILE


def get_node_ids(spec):
    if ':' in spec:
        filename, line_number = spec.split(':')
        return nodes_by_file_and_line(filename, line_number)
    else:
        return nodes_by_file(spec)


def nodes_by_file(filename):
    abs_filename = os.path.abspath(filename)

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT(node_id) FROM coverage
        WHERE filename = ?
        order by node_id
    """, (abs_filename,))

    return list(node_id for (node_id,) in cursor.fetchall())


def nodes_by_file_and_line(filename, line_number):
    abs_filename = os.path.abspath(filename)

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT(node_id) FROM coverage
        WHERE filename = ? AND line = ?
        order by node_id
    """, (abs_filename, line_number))

    return list(node_id for (node_id,) in cursor.fetchall())
