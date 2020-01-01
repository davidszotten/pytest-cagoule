from __future__ import print_function

import sys

from .git_parser import get_changes
from .select import get_node_ids


def main():
    if len(sys.argv) < 2:
        print("Usage: cagoule filename[:line number]")
        return

    spec = sys.argv[1]

    if spec == "--git":
        specs = get_changes(*sys.argv[2:])
    else:
        specs = [spec]

    node_ids = get_node_ids(specs)

    if node_ids:
        print("\n".join(node_ids))
