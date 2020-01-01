pytest-cagoule
==============

**pytest-cagoule** is a pytest plugin to find which tests interact with the
code you've just changed.


Usage
-----

Collect coverage information using ``--pytest-cov`` coverage contexts.

::

    py.test --cov --cov-context=test

Then, to run the subset of tests that touch a particular file, use
``cagoule-select=<filename>[:line number]``, e.g.

::

    py.test --cagoule-select=path/to/file.py

If you are using ``git``, cagoule can find the files and lines that have changes
in the current working directory::

    py.test --diff

or for any other diff spec that git can parse, using ``--diff=<spec>``, e.g.

::

    py.test --diff=head~1..head


You probably want to configure your CI server to handle capturing.


Installing
----------

Install **pytest-cagoule** using ``pip``::

    pip install pytest-cagoule


Caveats
^^^^^^^

Only lines executed *during individual test runs* are captured. This often
excludes module level code, which is executed at *import* time, before the test
starts.  Also, tests are of course registered against the code as it was when
data was captured, so if using ``--diff``, no new tests will be included.


Inspiration
^^^^^^^^^^^

Idea from ``nose-knows``


License
-------

MIT. See ``LICENSE`` for details
