import re
import subprocess

from .compat import string_types

NULL = object()


def get_next_marker(stream):
    for line in stream:
        if line.startswith("diff"):
            # skip ahead until the '---' line
            while not line.startswith("---"):
                line = next(stream, None)
                if line is None:
                    return None

            # consume '+++' line
            next(stream, None)
            if line == "--- /dev/null":
                return NULL
            else:
                filename = line[4:]
                return filename.strip()

        elif line.startswith("@@"):
            pattern = (
                r"@@ -(?P<del_start>\d+)(,(?P<del_count>\d+))? "
                r"\+(?P<add_start>\d+)(,(?P<add_count>\d+))? .*"
            )
            match = re.match(pattern, line)
            return match.groupdict()


def get_diff_changes(diff):
    filename = None
    stream = iter(diff.splitlines())
    while True:
        # Bad input could cause get_next_marker to raise StopIteration,
        # but that will just (correctly) be equivalient to a return here.
        marker = get_next_marker(stream)
        if marker is None:
            break

        if marker is NULL:
            filename = None
        if isinstance(marker, string_types):
            filename = marker
        elif isinstance(marker, dict):
            del_start = int(marker["del_start"])
            del_count = int(marker["del_count"] or 1)
            del_end = del_start + del_count
            if filename is not None:
                yield filename, del_start, del_end


def get_changes(*git_diff_args):
    diff = subprocess.check_output(
        ["git", "diff", "--unified=0", "--no-prefix"] + list(git_diff_args),
        universal_newlines=True,
    )
    for filename, start, end in get_diff_changes(diff):
        yield filename, start, end
