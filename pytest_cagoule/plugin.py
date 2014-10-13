from coverage import coverage
import six

from .db import get_connection
from .git_parser import get_changes
from .select import get_node_ids


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
        self.setup_db()


    def setup_db(self):
        connection = get_connection()
        with connection:
            connection.execute("DROP TABLE IF EXISTS coverage;")
            connection.execute("""
                CREATE TABLE coverage (
                    node_id text,
                    filename text,
                    line int,
                    PRIMARY KEY(node_id, filename, line)
                );
            """)

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

    def data_for_insert(self, node_id, cov_data):
        for filename, lines in six.iteritems(cov_data.lines):
            for line in lines:
                yield node_id, filename, line

    def write_results(self, node_id, cov_data):
        connection = get_connection()
        with connection:
            connection.executemany(
                "INSERT INTO coverage VALUES (?, ?, ?)",
                self.data_for_insert(node_id, cov_data)
            )


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
