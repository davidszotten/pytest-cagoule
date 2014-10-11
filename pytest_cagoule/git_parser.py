#!/usr/bin/env python

import re
import subprocess

import fileinput
stream = fileinput.input()


def get_next_marker(stream):
    for line in stream:
        if line.startswith('diff'):
            # skip "index"
            next(stream)
            # grab "---" line
            line = next(stream)
            filename = line[6:]
            # consume '+++' line
            next(stream)
            return filename.strip()

        elif line.startswith('@@'):
            pattern = (
                r'@@ -(?P<del_start>\d+)(,(?P<del_count>\d+))? '
                r'\+(?P<add_start>\d+)(,(?P<add_count>\d+))? .*'
            )
            match = re.match(pattern, line)
            return match.groupdict()


def get_diff_changes(diff):
    filename = None
    stream = iter(diff.splitlines())
    while True:
        # we could probably just not catch StopIteration, and rely on it
        # bubbling to stop the iteration over get_changes higher up
        # too tricky?
        try:
            marker = get_next_marker(stream)
            if marker is None:
                break

            if isinstance(marker, basestring):
                filename = marker
            elif isinstance(marker, dict):
                del_start = int(marker['del_start'])
                del_count = int(marker['del_count'] or 1)
                del_end = del_start + del_count
                yield filename, del_start, del_end

        except StopIteration:
            break


def get_changes():
    diff = subprocess.check_output(['git', 'diff', '--unified=0'])
    for filename, start, end in get_diff_changes(diff):
        yield filename, start, end


if __name__ == '__main__':
    for filename, start, end in get_changes():
        print '{}:{}-{}'.format(filename, start, end)
