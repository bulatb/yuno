Cleaning up test history
========================

Yuno doesn't watch for changes to the test repo, so references to tests that get deleted or renamed can clutter up your history and suites. Since those now-missing tests will never pass if they were failing, or vice-versa, there's no way for ``yuno run`` to flush them out. Running ``yuno prune`` will synchronize your records with the current contents of the repo and make sure only tests that still exist are counted.

To clean up your ``passing`` and ``failing`` lists::

    yuno.py prune

Flags and options
-----------------

  1. ``--last-run`` - Also prune your last run's log file. Usually not needed, but it can help if missing tests are bouncing back and forth between skipped and passed/failed.

  2. ``--suites`` - Also prune the suites in your main suite folder.

  3. ``--all`` - Short for ``--last-run --suites``.

