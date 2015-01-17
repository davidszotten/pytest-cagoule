import pytest
from pytest_cagoule.select import (
    get_line_number_filter, get_spec_filter, get_query
)


@pytest.mark.parametrize(
    ('start', 'end', 'expected_query', 'expected_params'), (
        (None, None, '', ()),
        (None, 'foo', '', ()),  # if start is None, end is ignored
        (3, None, 'AND (line = ?)', (3,)),
        (3, 5, 'AND (line = ? OR line = ? OR line = ?)', (3, 4, 5)),
    )
)
def test_line_get_line_number_filter(
        start, end, expected_query, expected_params):
    query, params = get_line_number_filter(start, end)
    assert query == expected_query
    assert params == expected_params


@pytest.mark.parametrize(
    ('spec', 'expected_query', 'expected_params'), (
        (
            '/tmp/foo.py:3-5',
            'filename = ? AND (line = ? OR line = ? OR line = ?)',
            ('/tmp/foo.py', 3, 4, 5),
        ),
    )
)
def test_get_spec_filter(spec, expected_query, expected_params):
    query, params = get_spec_filter(spec)
    assert query == expected_query
    assert params == expected_params


def test_query():
    query, params = get_query(['/tmp/foo.py:3', '/tmp/bar.py:3-5'])
    query_lines = [
        line.strip() for line in query.split('\n') if line.strip()
    ]
    expected_query = """
        SELECT DISTINCT(nodeid) FROM coverage
            JOIN nodeids on coverage.nodeid_id = nodeids.id
            JOIN files on coverage.file_id = files.id
        WHERE
            (filename = ? AND (line = ?))
            OR (filename = ? AND (line = ? OR line = ? OR line = ?))
        ORDER BY nodeid
    """
    expected_lines = [
        line.strip() for line in expected_query.split('\n') if line.strip()
    ]
    expected_params = (
        '/tmp/foo.py', 3, '/tmp/bar.py', 3, 4, 5
    )
    assert query_lines == expected_lines
    assert params == expected_params
