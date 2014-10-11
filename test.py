#!/usr/bin/env python

import re

import fileinput
stream = fileinput.input()
# for line in

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


filename = None
while True:
    try:
        marker = get_next_marker(stream)
        if marker is None:
            break

        if isinstance(marker, basestring):
            filename = marker
        elif isinstance(marker, dict):
            del_start = int(marker['del_start'])
            del_count = int(marker['del_count'] or 1)
            print '{}:{}-{}'.format(
                filename, del_start, del_start + del_count)

    except StopIteration:
        break


