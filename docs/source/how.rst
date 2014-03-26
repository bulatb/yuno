How it works
============

A Yuno test case has two parts: a source file (testname.rc) fed to the compiler and an answer file (testname.ans.out) to be compared with the compiler's output. If the two files match, the test case passes. If not, it fails.

Each pair of files lives somewhere in the test repo, arranged in whatever structure you want. For Compilers, the layout usually looks like this::

    testcases/
        phase1/
            check1/
                MyFirstTest.rc
                MyFirstTest.ans.out
            check2/
                (etc)
        phase2/
            (etc)

This layout also works with older testing frameworks, so the repo can be versioned independently and no one is locked in to a specific tester.

When you want to run your tests, give ``yuno run`` the right command to find them and remember the results are all your fault.

