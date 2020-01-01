from __future__ import unicode_literals

from pytest_cagoule.git_parser import get_diff_changes


diff1 = """diff --git a/README.rst b/README.rst
index 8902dc2..9de8bf2 100644
--- README.rst
+++ README.rst
@@ -3,0 +4 @@ pytest-cagoule
+
"""

diff2 = """diff --git a/README.rst b/README.rst
index 8902dc2..f39170e 100644
--- README.rst
+++ README.rst
@@ -3,0 +4 @@ pytest-cagoule
+
@@ -29,4 +28,0 @@ Install **cagoule** using ``pip``::
-License
--------
-
-MIT. See ``LICENSE`` for details
diff --git a/setup.py b/setup.py
index bbe47a8..e83a1a7 100644
--- setup.py
+++ setup.py
@@ -0,0 +1 @@
+
diff --git a/MANIFEST.in b/MANIFEST.in
new file mode 100644
index 0000000..0c73842
--- /dev/null
+++ MANIFEST.in
@@ -0,0 +1 @@
+include README.rst LICENSE
"""


def test_get_diff_changes_simple():
    expected = (("README.rst", 3, 3),)
    assert tuple(get_diff_changes(diff1)) == expected


def test_get_diff_changes_multiple():
    expected = (
        ("README.rst", 3, 3),
        ("README.rst", 29, 33),
        ("setup.py", 0, 0),
        # new files are ignored
    )
    assert tuple(get_diff_changes(diff2)) == expected


def test_malformed_diff():
    assert tuple(get_diff_changes("diff foo\nbar")) == ()
