import sqlite3

from coverage.control import Coverage

from cagoule import DB_FILE


def pytest_addoption(parser):
    parser.addoption(
        '--cagoule-collect', action='store_true', dest='cagoule_collect',
        help='collect coverage info for cagoule',
    )


class CagoulePlugin(object):
    cov = None

    def __init__(self):
        self.cov = Coverage(source='.')
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
        for filename, lines in cov.data.lines.iteritems():
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
            for node_id, lines in self.data.iteritems():
                for filename, line in lines:
                    cursor.execute(
                        "INSERT INTO coverage VALUES (?, ?, ?)",
                        (node_id, filename, line)
                    )

    def pytest_sessionfinish(self):
        self.write_results()


def pytest_configure(config):
    if not config.getvalue('cagoule_collect'):
        return

    if config.pluginmanager.hasplugin('_cagoule'):
        return

    plugin = CagoulePlugin() #config.option, config.pluginmanager,
    config.pluginmanager.register(plugin, '_cagoule')
