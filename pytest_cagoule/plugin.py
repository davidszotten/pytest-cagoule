from collections import defaultdict
from functools import partial
from itertools import count

from .git_parser import get_changes
from .select import get_node_ids

# generates a stream of integers when called
filename_ids = partial(next, count())
nodeid_ids = partial(next, count())
filename_map = defaultdict(filename_ids)
nodeid_map = defaultdict(nodeid_ids)


def pytest_addoption(parser):
    # TODO: better help text
    parser.addoption(
        "--cagoule-select",
        metavar="spec",
        action="store",
        dest="cagoule_select",
        help="run only tests that cover the spec",
    )
    parser.addoption(
        "--cagoule-git",
        "--diff",
        nargs="?",
        dest="cagoule_git",
        const="HEAD",
        help="run only tests that cover files with git changes",
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
    spec = config.getvalue("cagoule_select")
    if spec and not config.pluginmanager.hasplugin("_cagoule_select"):
        plugin = CagouleSelectPlugin(spec=spec)
        config.pluginmanager.register(plugin, "_cagoule_select")

    git_spec = config.getvalue("cagoule_git")
    if git_spec and not config.pluginmanager.hasplugin("_cagoule_select"):
        plugin = CagouleSelectPlugin(git_spec=git_spec)
        config.pluginmanager.register(plugin, "_cagoule_select")
