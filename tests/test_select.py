import pytest
from pytest_cagoule.select import (
    get_line_number_filter, get_spec_filter, get_query
)


@pytest.mark.parametrize(
    ('start', 'end', 'expected_query', 'expected_params'), (
        (None, None, '', ()),
        (None, 'foo', '', ()),  # if start is None, end is ignored
        (3, None, 'AND numbits_any_intersection(numbits, ?)', (b'\x08',)),
        (3, 5, 'AND numbits_any_intersection(numbits, ?)', (b'\x38',)),
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
            'path = ? AND numbits_any_intersection(numbits, ?)',
            ('/tmp/foo.py', b'\x38'),
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
        SELECT DISTINCT(context) FROM
            context
            JOIN line_bits ON line_bits.context_id = context.id
            JOIN file ON line_bits.file_id = file.id
        WHERE
            (path = ? AND numbits_any_intersection(numbits, ?))
            OR (path = ? AND numbits_any_intersection(numbits, ?))
        ORDER BY context
    """
    expected_lines = [
        line.strip() for line in expected_query.split('\n') if line.strip()
    ]
    expected_params = (
        '/tmp/foo.py', b'\x08', '/tmp/bar.py', b'\x38'
    )
    assert query_lines == expected_lines
    assert params == expected_params
