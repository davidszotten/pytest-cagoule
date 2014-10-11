import sqlite3
import os
import sys

from cagoule import DB_FILE


def main():
    if len(sys.argv) < 2:
        print "Usage:"
        return

    if len(sys.argv) > 2:
        print_nodes_by_file_and_line(sys.argv[1:3])
    else:
        print_nodes_by_file(sys.argv[1])


def print_nodes_by_file(filename):
    abs_filename = os.path.abspath(filename)

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT(node_id) FROM coverage
        WHERE filename = ?
    """, (abs_filename,))

    print '\n'.join(node_id for (node_id,) in cursor.fetchall())

def print_nodes_by_file_and_line(filename, line_number):
    abs_filename = os.path.abspath(filename)

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT DISTINCT(node_id) FROM coverage
        WHERE filename = ? AND line = ?
    """, (abs_filename, line_number))

    print '\n'.join(node_id for (node_id,) in cursor.fetchall())
