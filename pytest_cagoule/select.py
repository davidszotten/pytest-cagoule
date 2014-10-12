from itertools import chain
import os
import re
import sqlite3

import six

from . import DB_FILE

spec_re = re.compile(
    r'(?P<filename>[^:]+)(:(?P<start_line>\d+))?(-(?P<end_line>\d+))?'
)


def parse_spec(spec):
    match = spec_re.match(spec)
    if match is None:
        return []
    matches = match.groupdict()

    filename = matches['filename']

    start_line = matches.get('start_line')
    if start_line is not None:
        start_line = int(start_line)

    end_line = matches.get('end_line')
    if end_line is not None:
        end_line = int(end_line)

    return filename, start_line, end_line


def get_query(specs):
    query_list = []
    params_list = []
    for spec in specs:
        query, params = get_spec_filter(spec)
        query_list.append(query)
        params_list.append(params)

    if query_list:
        clauses = '\n OR '.join(map("({})".format, query_list))
        filters = """
            WHERE
            {}
        """.format(clauses)
    else:
        return None, None

    full_params = tuple(chain(*params_list))
    full_query = """
        SELECT DISTINCT(node_id) FROM coverage
        {}
        ORDER BY node_id
    """.format(filters)
    return full_query, full_params


def get_spec_filter(spec):
    # TODO: find where to best do this
    if isinstance(spec, six.string_types):
        spec = parse_spec(spec)

    filename, start_line, end_line = spec

    filename = os.path.abspath(filename)

    lines_query, line_params = get_line_number_filter(start_line, end_line)
    query = 'filename = ? ' + lines_query
    params = (filename,) + line_params
    return query, params


def get_line_number_filter(start_line, end_line):
    if start_line is None:
        return '', ()

    if end_line is None:
        end_line = start_line

    lines = tuple(range(start_line, end_line + 1))
    query = 'AND ({})'.format(
        ' OR '.join('line = ?' for line in lines)
    )
    return query, lines


def get_nodes_from_db(specs):
    query, params = get_query(specs)
    if query is None:
        return []

    if not os.path.exists(DB_FILE):
        return []

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute(query, params)
    return list(node_id for (node_id,) in cursor.fetchall())


def get_node_ids(specs):
    return get_nodes_from_db(specs)
