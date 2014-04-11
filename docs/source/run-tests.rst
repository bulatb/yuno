Running tests
=============

Signatures
----------

.. |br| raw:: html

   <br />

.. |--| raw:: html

   --

``yuno run all`` | ``failed`` | ``failing`` | ``passed`` | ``passing`` | ``<glob>`` |br|\
``yuno run phase <#>`` | ``check <#>`` | ``suite <name>`` | ``files <glob>`` |br|\
``yuno run phase <#> check <#>`` |br|\
``<newline-delimited stream> | yuno run -``


Options
-------

|--|\ diff [mode]
    Print a diff for any tests that fail. The mode can be `context <http://en.wikipedia.org/wiki/Diff#Context_format>`_ or `unified <http://en.wikipedia.org/wiki/Diff#Unified_format>`_, defaulting to ``context``.

|--|\ ignore [regex [regex ...]]
    Don't run tests whose path (including filename) matches any given ``regex``. `Python-style <https://docs.python.org/2/library/re.html#regular-expression-syntax>`_ patterns; takes (?iLmsux) flags; backrefs can be named or ``\1``, ``\2``, etc.

|--|\ pause [event(s)]
    Pause on certain events: ``p`` (test passed), ``f`` (failed), ``s`` (skipped), ``w`` (warned), or any combination (``pf``, ``fsw``, etc). Defaults to ``f``.

|--|\ save <name>
    Save the tests that just ran as a suite called ``<name>``.

-o, |--|\ overwrite
    Use with ``save`` to write over an existing suite with the same name.

Running by folder
-----------------

If ``run`` receives one argument and it doesn't match a special value (all, -, failed, failing, passed, or passing), it's taken as a Unix path `glob <http://wiki.bash-hackers.org/syntax/expansion/globs>`_ representing folders in the repo to be searched recursively. Any files inside that have the right extension (.rc by default) will be run as tests.

Every test in dir1/ or dir2/::

    yuno run dir[1-2]

Every test in every check ending in 2::

    yuno run phase*/check*2

Every test with a Companion Cube::

    yuno run enrichment/chamber17

.. note::
   To better work with Windows, Yuno needs to handle its own glob expansion. Unix users should disable globbing for their session (Bash: ``set -f``) or quote arguments containing globs (``run "**/dir"``) if the shell's expander causes problems.

.. _run-by-phase-and-check:

By phase or check
-----------------

Being a Compilers tool, Yuno gives special treatment to repositories laid out in phases and checks. The ``phase`` and ``check`` commands can be used separately, together, or not at all—they just provide a nicer wrapper over using globs. Each one's ``<#>`` may be a number, a number and a letter, or dash-separated range. (More on that below.)

Any test files inside matching folders or subfolders will be run.

::

    yuno run phase 1-3
    yuno run check 12

    # If check alone would be ambiguous
    yuno run phase 2 check 6a

To support checks with multiple parts, ranges can slice on numbers and letters together. Each end may be one or more digits, optionally followed by a letter. For example, to run every test in every check between ``check6b`` and ``check10`` (inclusive)::

    # Runs 6b, 6c, 7, ... 9a, ..., 9z, ..., 10z
    yuno run check 6b-10

**Note:** If you don't put in a range, Yuno looks for an exact match. Asking it to ``run check 3`` means asking it to run tests in a folder called ``check3``, not to run 3a, b, and c together.

If you want to run them all, use::

    yuno run check 3a-3c

Or if you're lazy::

    yuno run check 3a-c

Yuno always does its best to run no less than what you asked for, only skipping checks if they're specifically excluded by the range. A range endpoint without a letter will include that check and all its subparts. Any checks that fall inside the middle of the range are loaded fully, ``#`` to ``#z``.

::

    # 4, 4a, 4b, ..., 9, ..., 9d, 9e (but not 9f)
    yuno run check 4-9e

    # 5b, 5c, ..., 6, 6a (but not 5 or 5a)
    yuno run check 5b-6a

    # 5, 5a, ..., 10, ..., 10z
    yuno run check 5-10

By status
---------

Like ``all``, ``passed``/``failed`` and ``passing``/``failing`` can be used to run special sets of tests.

Every test that passed (or failed) on the last run::

    yuno run passed
    yuno run failed

Every test that hasn't passed since it last failed::

    yuno run failing

Every test that hasn't failed since it last passed::

    yuno run passing


By suite
--------

Suites are arbitrary sets of tests, grouped together and named. They're handy for creating groups of tests that go together without having to move files around.

To run a suite::

    yuno run suite <name>

To create a suite, either:

- Use the ``--save`` flag with a name (``run <whatever> --save <name>``), which makes a suite from every test that ran this time; or

- By hand, create ``<name>.txt`` in ``settings/suites/`` and add the path for every test you want: one per line, repo-relative, including the file name.

For example, a finished suite accessible as ``pointers`` looks like this::

    $ cat settings/suites/pointers.txt
    phase2/check12/dereference-void.rc
    phase3/check18/pass-pointer-by-reference.rc
    sizeof/pointer-size.rc

By filename
-----------

For more precise control over which tests will run, use ``run files`` with a glob that matches the full path and name you want.

Only tests from people you trust::

    yuno run files public/mallory/*.rc

Tests for printing 5 or fewer lines::

    yuno run files **/cout/print[0-5].rc

From a pipe
-----------

If ``yuno run -`` sees text on ``stdin``, it treats it as a newline-separated list of test files and ignores any positional arguments. Options and flags will still be used if they make sense. See the Data section for more on how to use this to hack in some extra capability.

To re-run every test that raised a warning last time::

    # Find lines that start with w, clean them up, and pipe to Yuno
    $ grep ^w data/last-run.txt | sed 's/^w //' | yuno run -

But no one likes sed, so Yuno knows to strip out its own line labels::

    $ grep ^w data/last-run.txt | yuno run -

