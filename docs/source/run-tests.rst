Running tests
=============

**Usage note:** For brevity, previous examples have assumed there was a PATH entry or alias named ``yuno`` for ``yuno.py``. While it's nicer to type and makes commands look cleaner, the examples here are written out in full for easy copy-pasting. Aliases are available in `Bash <http://www.thegeekstuff.com/2010/04/unix-bash-alias-examples/>`_ (Linux, OS X), `Windows <http://devblog.point2.com/2010/05/14/setup-persistent-aliases-macros-in-windows-command-prompt-cmd-exe-using-doskey/>`_, and most other shells.

To run Yuno directly as ``yuno.py`` on non-Windows machines, you may need to make it executable::

    $ chmod +x /your/project/yuno/yuno.py

Signatures
----------

.. |br| raw:: html

   <br />

``yuno.py run all`` | ``failed`` | ``failing`` | ``passed`` | ``passing`` | ``<glob>`` |br|\
``yuno.py run phase <#>`` | ``check <#>`` | ``suite <name>`` | ``files <glob>`` |br|\
``yuno.py run phase <#> check <#>`` |br|\
``<newline-delimited stream> | yuno.py run -``

Flags and options
-----------------

  1. ``--diff [routine]`` - Instead of the normal message, print a diff for any tests that fail. The routine can be ``context`` or ``unified``, defaulting to ``context``.

  2. ``--pause [events]`` - Pause on certain events: ``p`` (test passed), ``f`` (failed), ``s`` (skipped), ``w`` (warned), or any combination (``pf``, ``fsw``, etc). Defaults to ``f``.

  3. ``--save <name>`` - Save the tests that just ran as a suite called ``<name>``.

  4. ``-o, --overwrite`` - Use with ``save`` to write over an existing suite with the same name.

Running by folder
-----------------

If ``run`` receives one argument and it doesn't match a special value (all, -, failed, failing, passed, or passing), it's taken as a Unix path `glob <http://wiki.bash-hackers.org/syntax/expansion/globs>`_ representing folders in the repo to be searched recursively. Any files inside that have the right extension (.rc by default) will be run as tests.

Every test in dir1/ or dir2/::

    yuno.py run dir[1-2]

Every test in every check ending in 2::

    yuno.py run phase*/check*2

Every test with a Companion Cube::

    yuno.py run enrichment/chamber17

By phase or check
-----------------

Being a Compilers tool, Yuno gives special treatment to repositories laid out in phases and checks. The ``phase`` and ``check`` commands can be used separately, together, or not at all—they just provide a nicer wrapper over using globs. Each one's ``<#>`` may be a number, a number and a letter, or dash-separated range. (More on that below.)

Any test files inside matching folders or subfolders will be run.

::

    yuno.py run phase 1-3
    yuno.py run check 12

    # If check alone would be ambiguous
    yuno.py run phase 2 check 6a

To support checks with multiple parts, ranges can slice on numbers and letters together. Each end may be one or more digits, optionally followed by a letter. For example, to run every test in every check between ``check6b`` and ``check10`` (inclusive)::

    # Runs 6b, 6c, 7, ... 9a, ..., 9z, ..., 10z
    yuno.py run check 6b-10

**Note:** If you don't put in a range, Yuno looks for an exact match. Asking it to ``run check 3`` means asking it to run tests in a folder called ``check3``, not to run 3a, b, and c together.

If you want to run them all, use::

    yuno.py run check 3a-3c

Or if you're lazy::

    yuno.py run check 3a-c

Yuno always does its best to run no less than what you asked for, only skipping checks if they're specifically excluded by the range. A range endpoint without a letter will include that check and all its subparts. Any checks that fall inside the middle of the range are loaded fully, ``#`` to ``#z``.

::

    # 4, 4a, 4b, ..., 9, ..., 9d, 9e (but not 9f)
    yuno.py run check 4-9e

    # 5b, 5c, ..., 6, 6a (but not 5 or 5a)
    yuno.py run check 5b-6a

    # 5, 5a, ..., 10, ..., 10z
    yuno.py run check 5-10

By status
---------

Like ``all``, ``passed``/``failed`` and ``passing``/``failing`` can be used to run special sets of tests.

Every test that passed (or failed) on the last run::

    yuno.py run passed
    yuno.py run failed

Every test that hasn't passed since it last failed::

    yuno.py run failing

Every test that hasn't failed since it last passed::

    yuno.py run passing


By suite
--------

Suites are arbitrary sets of tests, grouped together and named. They're handy for creating groups of tests that go together without having to move files around.

To run a suite::

    yuno.py run suite <name>

To create a suite, either:

  1. Use the ``--save`` flag with a name (``run <whatever> --save <name>``), which makes a suite from every test that ran this time; or

  2. By hand, create ``<name>.txt`` in ``settings/suites/`` and add the path for every test you want, one per line (relative to the repo, and including the file name).

By filename
-----------

For more precise control over which tests will run, use ``run files`` with a glob that matches the full path and name you want.

Only tests from people you trust::

    yuno.py run files public/good/*-mallory.rc

Let's see how it likes Haskell::

    yuno.py run files phase1/**/*.hs

By pipe
-------

If ``yuno run -`` sees text on ``stdin``, it treats it as a newline-separated list of test files and ignores any positional arguments. Options and flags will still be used if they make sense. See the Data section for more on how to use this to hack in some extra capability.

To re-run every test that raised a warning last time::

    # Find lines that start with w, clean them up, and pipe to Yuno
    $ grep ^w data/last-run.txt | sed 's/^w //' | yuno.py run -

But no one likes sed, so Yuno knows to strip out its own line labels::

    $ grep ^w data/last-run.txt | yuno.py run -

