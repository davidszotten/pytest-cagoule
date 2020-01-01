from itertools import chain
import os
import re

from coverage import numbits

from .db import get_connection, db_exists, get_coverage_config

spec_re = re.compile(r"(?P<filename>[^:]+)(:(?P<start_line>\d+))?(-(?P<end_line>\d+))?")


def parse_spec(spec):
    match = spec_re.match(spec)
    matches = match.groupdict()

    filename = matches["filename"]

    start_line = matches.get("start_line")
    if start_line is not None:
        start_line = int(start_line)

    end_line = matches.get("end_line")
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
        clauses = "\n OR ".join(map("({})".format, query_list))
        filters = """
        WHERE
        {}
        """.format(
            clauses
        )
    else:
        return None, None

    full_params = tuple(chain(*params_list))
    full_query = """
        SELECT DISTINCT(context) FROM
        context
        JOIN line_bits ON line_bits.context_id = context.id
        JOIN file ON line_bits.file_id = file.id
        {}
        ORDER BY context
    """.format(
        filters
    )
    return full_query, full_params


def get_spec_filter(spec):
    # TODO: find where to best do this
    if isinstance(spec, str):
        spec = parse_spec(spec)

    filename, start_line, end_line = spec

    config = get_coverage_config()
    if not config.relative_files:
        filename = os.path.abspath(filename)

    lines_query, line_params = get_line_number_filter(start_line, end_line)
    query = "path = ? " + lines_query
    params = (filename,) + line_params
    return query, params


def get_line_number_filter(start_line, end_line):
    if start_line is None:
        return "", ()

    if end_line is None:
        end_line = start_line

    lines_numbits = numbits.nums_to_numbits(range(start_line, end_line + 1))
    query = "AND numbits_any_intersection(numbits, ?)"
    return query, (lines_numbits,)


def get_node_ids(specs):
    query, params = get_query(specs)
    if query is None:
        return []

    if not db_exists():
        return []

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)

    contexts = [context.decode() for (context,) in cursor.fetchall()]
    node_ids = [context.split("|")[0] for context in contexts]
    return list(node_ids)
