Y U NO have automated tests?
============================

If you're running tests by hand, you're missing bugs and wasting time. Use Yuno.

Yuno lets you run more tests, much faster, much more often. Run a full regression suite for each commit. Run any test you want at any time. Let Yuno figure out what's broken, what's *still* broken, what you fixed, and what your fix just broke. Designed for [CSE 131](http://cseweb.ucsd.edu/~ricko/CSE131/), it's customizable, cross-platform, and it helps you get a better grade.


A few features
--------------
Run every test in Phase 1, with diff output for failures:

    yuno run phase 1 --diff

Run a custom set of tests, then save them as a suite for later:

    yuno run all --ignore mallory/ eve/ --save trusted

Run a suite you made earlier (or got from someone else):

    yuno run suite crazy_edge_cases

See everything that still needs fixing:

    yuno show failing

If your not-so-sober partner made some changes, it can help you find regressions:

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

Using Yuno
----------

Read the [manual on ReadTheDocs](http://yuno.readthedocs.org).

License
-------

[MIT](http://opensource.org/licenses/MIT). Do anything you want.
