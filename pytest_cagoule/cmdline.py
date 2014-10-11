import sys

from .select import get_node_ids


def main():
    if len(sys.argv) < 2:
        print "Usage: cagoule filename[:line number]"
        return

    spec = sys.argv[1]
    node_ids = get_node_ids(spec)

    print '\n'.join(node_ids)
