Creating tests
==============

Depending on your preference, you might want to create your source files in a temporary place and only move them to the repo when you're sure they're good; or you might just add them right away and work on them in place. Either way, ``yuno certify`` will help you make the answer files so you can ``yuno run`` and share them if you want to.

Scary warning
-------------

Yuno is extremely stupid. It has no idea what your tests should do. If any answer files are wrong, it's possible you won't find out until you're getting angry emails from your friends and no one speaks to you in lab. Or worse—until your grades come back and everything was broken.

That's why this feature is called ``certify``: by running it, you certify your compiler's output for these cases will be right. Let typing the pretentious name remind you to be careful.

Signatures
----------

.. |br| raw:: html

   <br />

``yuno certify files <glob>`` |br|\
``<newline-delimited stream> | yuno certify -``

Options
-------

.. |--| raw:: html

   --

|--|\ overwrite
    If an answer file already exists, overwrite it without asking. Use with caution.

|--|\ correct
    Don't ask if output is correct before accepting. Use with terror.

Creating by glob
----------------

This feature works the same as ``yuno run files``: the ``<glob>`` should match specific file names, including full paths and extensions, except the output will be answer files instead of test results. You'll be prompted every time it tries to overwrite a file unless you use ``--overwrite``.

To generate an answer file for ``my-first-test.rc``::

    yuno certify files phase1/check1/my-first-test.rc

Creating by pipe
----------------

As with ``yuno run``, users with nice shells get extra power here. For example, Unix users can generate answers for any tests that were skipped because of missing answer files::

    grep ^s data/last-run.txt | yuno certify -

