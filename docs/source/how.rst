How it works
============

1. Point Yuno at a program.
2. Make a test repository—just a folder.
3. Add some tests.

Then choose which ones to run by name, by history, by parent folder, by excluding certain paths, or loading from a custom suite. The simplest test case has two parts:

An input file (example.rc):

.. code-block:: c

   int x = 5 + false;

And the expected output (example.ans.out)::

    Error, "example.rc":
      Incompatible type bool to binary operator +, numeric expected.
    Compile: failure.

Yuno feeds each test case to your program, verifies the output, and reports what passed and failed.

