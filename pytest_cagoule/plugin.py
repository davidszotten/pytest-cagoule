import sqlite3

from coverage import coverage
import six

from . import DB_FILE
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
        self.data = {}

    def pytest_runtest_setup(self, item):
        cov = self.cov
        cov.erase()
        cov.start()

    def pytest_runtest_teardown(self, item):
        cov = self.cov
        cov.stop()
        cov._harvest_data()

        data = []
        for filename, lines in six.iteritems(cov.data.lines):
            for line in lines:
                data.append((filename, line))
        self.data[item.nodeid] = data

    def write_results(self):
        cursor = sqlite3.connect(DB_FILE)
        with cursor:
            cursor.execute("DROP TABLE IF EXISTS coverage;")

            cursor.execute("""
                CREATE TABLE coverage (
                    node_id text,
                    filename text,
                    line int,
                    PRIMARY KEY(node_id, filename, line)
                );
            """)
            cursor.execute("DELETE FROM coverage")
            # TODO: bulk insert
            for node_id, lines in six.iteritems(self.data):
                for filename, line in lines:
                    cursor.execute(
                        "INSERT INTO coverage VALUES (?, ?, ?)",
                        (node_id, filename, line)
                    )

    def pytest_sessionfinish(self):
        self.write_results()


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
