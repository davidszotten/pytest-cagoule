pytest-cagoule
==============

**pytest-cagoule** is a pytest plugin to find which tests interact with the
code you've just changed.


Usage
-----

Collect coverage information using ``--cagoule-capture``::

    py.test --cagoule-capture

Then, to run the subset of tests that touch a particular file, use
``cagoule-select=<filename>[:line number]``, e.g.::

    py.test --cagoule-select=path/to/file.py


You probably want to configure your CI server to handle capturing.


Installing
----------

Install **cagoule** using ``pip``::

    pip install pytest-cagoule


License
-------

MIT. See ``LICENSE`` for details
