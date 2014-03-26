Getting information
===================

Most of the info Yuno keeps track of can be accessed with ``show``. It always takes one argument and ignores any options or flags.

Signatures
----------

Tests that failed last time | tests that haven't passed since they last failed:
``yuno show failed`` | ``failing``

Tests that passed last time | tests that haven't failed since they last passed:
``yuno show passed`` | ``passing``

Tests that were skipped on the last run: ``yuno show skipped``

Tests that raised warnings on the last run: ``yuno show warned``

.. All available suites: ``yuno show suites``

.. A detailed log of the last run: ``yuno show last``
