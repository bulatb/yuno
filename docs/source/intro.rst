Yuno: Y U NO have testing framework?
====================================

If you're still running test cases by hand, stop everything you're doing and *read this right now*.

No, stop eating that. Hold your breath. It'll be worth it.

Yuno is a framework that will run whatever tests you want and tell you what exploded. It was made for `Compilers <http://cseweb.ucsd.edu/~ricko/CSE131/>`_ at UCSD, but it's good for any case where lots of different inputs need to run against a spec. It's cross-platform, customizable, and helps you get a better grade.


A few features
--------------------
Run all the tests in Phase 1, with diff output for failures::

    yuno run phase 1 --diff

Run a custom set of tests, then save them as a suite for later::

    yuno run files phase*/**/*-good.rc --save known_good

Run a suite you made earlier (or got from someone else)::

    yuno run suite crazy_edge_cases

See everything that still needs fixing::

    yuno show failing

And if your perhaps-not-sober partner made some changes, it can help you with regressions::

    $ yuno run all
    ....output....
    --------------
    Ran 100 tests

      2 passed
      98 failed
          yuno (show|run) failed

    - 62 regressions
          (list)

