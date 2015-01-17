from collections import defaultdict
from functools import partial
from itertools import count

from coverage import coverage
import six

from .db import get_connection
from .git_parser import get_changes
from .select import get_node_ids

# generates a stream of integers when called
filename_ids = partial(next, count())
nodeid_ids = partial(next, count())
filename_map = defaultdict(filename_ids)
nodeid_map = defaultdict(nodeid_ids)


def pytest_addoption(parser):
    parser.addoption(
        '--cagoule-capture', action='store_true', dest='cagoule_capture',
        help='capture coverage info for cagoule',
    )

    # TODO: better help text
    parser.addoption(
        '--cagoule-select', metavar='spec', action='store',
        dest='cagoule_select', help='run only tests that cover the spec',
    )
    parser.addoption(
        '--cagoule-git', '--diff', nargs='?', dest='cagoule_git', const='HEAD',
        help='run only tests that cover files with git changes',
    )
    # coverage params, at least concurrency


class CagouleCapturePlugin(object):
    def __init__(self):
        self.cov = coverage(source='.')
        self.tracing = False

    def setup_db(self):
        connection = self.connection
        connection.execute("DROP TABLE IF EXISTS coverage;")
        connection.execute("DROP TABLE IF EXISTS nodeids;")
        connection.execute("DROP TABLE IF EXISTS files;")
        connection.execute("DROP INDEX IF EXISTS coverage_nodeid;")
        connection.execute("DROP INDEX IF EXISTS coverage_fileid;")
        connection.execute("""
            CREATE TABLE files (
                id INTEGER PRIMARY KEY,
                filename TEXT
            );
        """)
        connection.execute("""
            CREATE TABLE nodeids (
                id INTEGER PRIMARY KEY,
                nodeid TEXT
            );
        """)
        connection.execute("""
            CREATE TABLE coverage (
                nodeid_id INTEGER REFERENCES nodeids,
                file_id INTEGER REFERENCES files,
                line INTEGER,
                PRIMARY KEY(nodeid_id, file_id, line)
            );
        """)
        connection.execute("""
            CREATE INDEX coverage_nodeid ON coverage(nodeid_id);
        """)
        connection.execute("""
            CREATE INDEX coverage_file ON coverage(file_id);
        """)

    def filename_values(self, cov_data):
        for filename, lines in six.iteritems(cov_data.lines):
            file_id = filename_map[filename]
            yield file_id, filename

    def nodeid_values(self, nodeid):
        nodeid_id = nodeid_map[nodeid]
        yield nodeid_id, nodeid

    def coverage_values(self, nodeid, cov_data):
        nodeid_id = nodeid_map[nodeid]
        for filename, lines in six.iteritems(cov_data.lines):
            file_id = filename_map[filename]
            for line in lines:
                yield nodeid_id, file_id, line

    def write_results(self, nodeid, cov_data):
        connection = self.connection
        connection.executemany(
            "REPLACE INTO nodeids VALUES (?, ?)",
            self.nodeid_values(nodeid)
        )
        connection.executemany(
            "REPLACE INTO files VALUES (?, ?)",
            self.filename_values(cov_data)
        )
        connection.executemany(
            "REPLACE INTO coverage VALUES (?, ?, ?)",
            self.coverage_values(nodeid, cov_data)
        )

    def pytest_sessionstart(self):
        self.connection = get_connection()
        self.setup_db()

    def vacuum_db(self):
        connection = self.connection
        connection.execute("vacuum")

    def pytest_runtest_setup(self, item):
        cov = self.cov
        cov.erase()
        cov.start()
        self.tracing = True

    def pytest_runtest_teardown(self, item):
        cov = self.cov
        if not self.tracing:
            return
        cov.stop()
        self.tracing = False
        cov._harvest_data()

        self.write_results(item.nodeid, cov.data)

    def pytest_sessionfinish(self):
        self.vacuum_db()
        self.connection.close()


class CagouleSelectPlugin(object):
    def __init__(self, spec=None, git_spec=None):
        if spec is not None:
            specs = [spec]
        elif git_spec is not None:
            specs = get_changes(git_spec)

        selected = get_node_ids(specs)
        self.selected = set(selected)

    def pytest_collection_modifyitems(self, session, config, items):
        covered = []
        uncovered = []
        for item in items:
            if item.nodeid in self.selected:
                covered.append(item)
            else:
                uncovered.append(item)

        items[:] = covered
        config.hook.pytest_deselected(items=uncovered)


def pytest_configure(config):
    if (
        config.getvalue('cagoule_capture') and
        not config.pluginmanager.hasplugin('_cagoule_capture')
    ):
        plugin = CagouleCapturePlugin()
        config.pluginmanager.register(plugin, '_cagoule_capture')

    spec = config.getvalue('cagoule_select')
    if (
        spec and
        not config.pluginmanager.hasplugin('_cagoule_select')
    ):
        plugin = CagouleSelectPlugin(spec=spec)
        config.pluginmanager.register(plugin, '_cagoule_select')

    git_spec = config.getvalue('cagoule_git')
    if (
        git_spec and
        not config.pluginmanager.hasplugin('_cagoule_select')
    ):
        plugin = CagouleSelectPlugin(git_spec=git_spec)
        config.pluginmanager.register(plugin, '_cagoule_select')
