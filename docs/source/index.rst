.. Yuno documentation master file, created by
   sphinx-quickstart on Sat Mar 22 00:11:17 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Y U NO have automated tests?
============================

If you're running tests by hand, you're missing bugs and wasting time. Use Yuno.

Yuno lets you run more tests, much faster, much more often. Run a full regression suite for each commit. Run any test you want at any time. Let Yuno figure out what's broken, what's **still** broken, what you fixed, and what your fix just broke. Designed for `CSE 131 <http://cseweb.ucsd.edu/~ricko/CSE131/>`_, it's customizable, cross-platform, and it helps you get a better grade.


A few features
--------------
Run every test in Phase 1, with diff output for failures::

    yuno run phase 1 --diff

Run a custom set of tests, then save them as a suite for later::

    yuno run all --ignore mallory/ eve/ --save trusted

Run a suite you made earlier (or got from someone else)::

    yuno run suite crazy_edge_cases

See everything that still needs fixing::

    yuno show failing

If your not-so-sober partner made some changes, it can help you find regressions::

    $ yuno run all
     ... snip ...
    --------------
    Ran 100 tests

      2 passed
      98 failed

    - 91 regressions
         phase1/check1/simplest.rc
         phase1/check1/worked-last-night.rc
         phase1/check1/what-did-you-do.rc
      ... snip ...


Manual Contents:
----------------

Introduction
............

.. toctree::

   how

Download and Install
....................

.. toctree::

   install

Working With Tests
..................

.. toctree::

   test-repositories
   run-tests
   testing-remotely
   create-tests

Test History
............

.. toctree::

   show-info
   clean-up

Customize Yuno
..............

.. toctree::

   customize

