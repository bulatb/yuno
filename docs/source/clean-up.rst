Cleaning up test history
========================

Yuno doesn't watch for changes to the test repo, so references to tests that get deleted or renamed can clutter up your history and suites. Running ``yuno prune`` will sync your records with the current contents of the repo and make sure only tests that still exist are counted.

To clean up your ``passing`` and ``failing`` lists::

    yuno prune

Options
-------

.. |--| raw:: html

   --

|--|\ last-run
    Also prune your last run's log file.

|--|\ suites
    Also prune the suites in your main suite folder.

|--|\ all
    Short for ``--last-run --suites``.

