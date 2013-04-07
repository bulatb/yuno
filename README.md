Yuno: Y U NO have testing framework?
====================================

If you're still running test cases by hand, stop everything you're doing and *read this right now*.

No, stop eating that. Hold your breath. It'll be worth it.

Yuno is a framework that will run whatever tests you want and tell you what exploded. It was made for [Compilers](http://cseweb.ucsd.edu/~ricko/CSE131/) at UCSD, but it's good for any case where lots of different inputs need to run against a spec. It's cross-platform, customizable, and helps you get a better grade.


A few features
--------------------
Run all the tests in Phase 1, with diff output for failures:

    yuno run phase 1 --diff

Run a custom set of tests, then save them as a suite for later:

    yuno run files phase*/**/*-good.rc --save known_good

Run a suite you made earlier (or got from someone else):

    yuno run suite crazy_edge_cases

See everything that still needs fixing:

    yuno show failing

And if your perhaps-not-sober partner made some changes, it can help you with regressions:
```
$ yuno run all
....output....
--------------
Ran 100 tests

  2 passed
  98 failed
      yuno (show|run) failed

- 62 regressions
      (list)
```


How it works
------------

A Yuno test case has two parts: a source file (testname.rc) fed to the compiler and an answer file (testname.ans.out) to be compared with the compiler's output. If the two files match, the test case passes. If not, it fails.

Each pair of files lives somewhere in the test repo, arranged in whatever structure you want. For Compilers, the layout usually looks like this:

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

When you want to run your tests, give `yuno run` the right command to find them and remember the results are all your fault.

Download and install
--------------------

### Python check

Yuno requires Python 2.7.x (not 2.6 or 3.x). It's a long, sad, highly fragmented story. If you don't already have it, or you have a different version, you should [get a copy](http://www.python.org/download/releases/2.7/) and install it somewhere nice. You can check your default Python install's version like this: `$ python --version`. ProTip: for ieng6 users, Python 2.7 lives in `/software/common/python-2.7/bin/python2.7`.

If you have multiple Python installs and don't want to fiddle with shebangs, it might be good to make an alias for the runtime you want:

    # Just one of many ways to do this
    $ alias yuno="/path/to/python2.7 yuno.py"

### The framework

If you're using Git, just:

    $ cd /your/project
    $ git clone https://github.com/bulatb/yuno.git

If not, download the [project zip](https://github.com/bulatb/yuno/archive/master.zip) and extract it wherever you want.

**Note**: For a hassle-free install that works out of the box, your folder structure should look like this:

    /your/project/ (anywhere)
        .eclipsecrap, etc/
        bin/
            (.class files)
        testcases/
            (test repo; see below)
        yuno/
            (yuno.py, etc)

### CSE 131: the test repo

Historically it's been a good idea to maintain a central, class-wide test repo for everyone to share their tests. Someone usually steps up to manage it and make sure everything stays good. To get yourself a working copy, or just see the folder structure it should have, see the [GitHub project here](https://github.com/bulatb/compilers-testcases).

If your care cup is [especially empty](http://pinterest.com/pin/135178426287092414/), clone that repo next to Yuno and skip down down to the manual.

    $ cd /your/project
    $ git clone https://github.com/bulatb/compilers-testcases.git


Running tests
-------------
**Usage note:** For brevity, previous examples have assumed there was a PATH entry or alias named `yuno` for `yuno.py`. While it's nicer to type and makes commands look cleaner, the examples here are written out in full for easy copy-pasting. Aliases are available in [Bash](http://www.thegeekstuff.com/2010/04/unix-bash-alias-examples/) (Linux, OS X), [Windows](http://devblog.point2.com/2010/05/14/setup-persistent-aliases-macros-in-windows-command-prompt-cmd-exe-using-doskey/), and most other shells.

To run Yuno directly as `yuno.py` on non-Windows machines, you may need to make it executable:

    $ chmod +x /your/project/yuno/yuno.py

### Signatures

`yuno.py run all` | `failed` | `failing` | `<glob>`<br/>
`yuno.py run phase <#>` | `check <#>` | `suite <name>` | `files <glob>`<br/>
`yuno.py run phase <#> check <#>`<br/>
`<newline-delimited stream> | yuno.py run -`<br/>

### Flags and options

  1. `--diff [routine]` - Instead of the normal message, print a diff for any tests that fail. The routine can be `context` or `unified`, defaulting to `context`.

  2. `--pause [events]` - Pause on certain events: `p` (test passed), `f` (failed), `s` (skipped), `w` (warned), or any combination (`pf`, `fsw`, etc). Defaults to `f`.

  3. `--save <name>` - Save the tests that just ran as a suite called `<name>`.

  4. `-o, --overwrite` - Use with `save` to write over an existing suite with the same name.

### Running by folder

If `run` receives one argument and it doesn't match a special value (all, -, failed, failing, passed, or passing), it's taken as a Unix path [glob](http://wiki.bash-hackers.org/syntax/expansion/globs) representing folders in the repo to be searched recursively. Any files inside that have the right extension (.rc by default) will be run as tests.

Every test in dir1/ or dir2/:

    yuno.py run dir[1-2]

Every test in every check ending in 2:

    yuno.py run phase*/check*2

Every test with a Companion Cube:

    yuno.py run enrichment/chamber17

### By phase or check

Being a Compilers tool, Yuno gives special treatment to repositories laid out in phases and checks. The `phase` and `check` commands can be used separately, together, or not at all. The `<#>` may be a number, string, or dash-separated number range.

Any test files inside matching folders or subfolders will be run.

    yuno.py run phase 1-3
    yuno.py run check 12

    # If check alone would be ambiguous
    yuno.py run phase 2 check 5

### By status

Like `all`, `passed`/`failed` and `passing`/`failing` can be used to run special sets of tests.

Every test that passed (or failed) on the last run:

    yuno.py run passed
    yuno.py run failed

Every test that hasn't passed since it last failed:

    yuno.py run failing

Every test that hasn't failed since it last passed:

    yuno.py run passing


### By suite

Suites are arbitrary sets of tests, grouped together and named. They're handy for creating groups of tests that go together without having to move files around.

To run a suite:

    yuno.py run suite <name>

To create a suite, either:

  1. Use the `--save` flag with a name (`run <whatever> --save <name>`), which makes a suite from every test that ran this time; or

  2. By hand, create `<name>.txt` in `settings/suites/` and add the path for every test you want, one per line (relative to the repo, and including the file name).

### By filename

For more precise control over which tests will run, use `run files` with a glob that matches the full path and name you want.

Only tests from people you trust:

    yuno.py run files public/good/*-mallory.rc

Let's see how it likes Haskell:

    yuno.py run files phase1/**/*.hs

### By pipe

If `yuno run -` sees text on `stdin`, it treats it as a newline-separated list of test files and ignores any positional arguments. Options and flags will still be used if they make sense. See the Data section for more on how to use this to hack in some extra capability.

To re-run every test that raised a warning last time:

    # Find lines that start with w, clean them up, and pipe to Yuno
    $ grep ^w data/last-run.txt | sed 's/^w //' | yuno.py run -

But no one likes sed, so Yuno knows to strip out its own line labels:

    $ grep ^w data/last-run.txt | yuno.py run -


Getting information
-------------------

Most of the info Yuno keeps track of can be accessed with `show`. It always takes one argument and ignores any options or flags.

### Signatures

Tests that failed last time | tests that haven't passed since they last failed:
`yuno show failed` | `failing`

Tests that passed last time | tests that haven't failed since they last passed:
`yuno show passed` | `passing`

Tests that were skipped on the last run: `yuno show skipped`

Tests that raised warnings on the last run: `yuno show warned`

All available suites: `yuno show suites`

A detailed log of the last run: `yuno show last`

Creating tests
--------------

Depending on your preference, you might want to create your source files in a temporary place and only move them to the repo when you're sure they're good; or you might just add them right away and work on them in place. Either way, `yuno certify` will help you make the answer files so you can `yuno run` and share them if you want to.

### A word of warning

Yuno is stupid, like a brick. Bricks don't know if your tests should be passing. If your answer files are wrong, tests could pass when they should fail and you may not catch the problem til your grades come back. That's why this feature is called `certify`: by running it, you certify your compiler's output for these cases will be right. Let typing the pretentious name remind you to be careful.

### Signatures

`yuno.py certify files <glob>`<br/>
`<newline-delimited stream> | yuno.py certify -`<br/>

### Flags

  1. `--overwrite` - If an answer file already exists, overwrite it without asking. Use with caution.

  2. `--correct` - Don't ask if output is correct before accepting. Use with even more caution.

### Creating by glob

This feature works the same as `yuno run files`: the `<glob>` should match specific file names, including full paths and extensions, except the output will be answer files instead of test results. You'll be prompted every time it tries to overwrite a file unless you use `--overwrite`.

To generate an answer file for `my-first-test.rc`:

    yuno.py certify files phase1/check1/my-first-test.rc

### Creating by pipe

As with `yuno run`, users with nice shells get extra power here. For example, Unix users can generate answers for any tests that were skipped because of missing answer files:

    grep ^s data/last-run.txt | yuno.py certify -


Customizing Yuno
----------------

### Configuration

The settings you can change are documented and defined in `settings/config.json`. Yuno comes pre-configured to work with the standard repo layout described above, but you're free to use whatever you prefer. The defaults are saved in `settings/config.json.default`.

Except for the comments (lines starting with `//`), the config syntax is [standard JSON](http://en.wikipedia.org/wiki/JSON#Data_types.2C_syntax_and_example). Intrepid editors will find that Yuno's comment stripping code is very stupid, so comments at the ends of lines will be treated not so much like comments but like syntax errors. Complaints may be addressed to:

  > ATTN: Roundfile Group -
  > 127 Wontfix Road -
  > Devnull, CA 92122 -

### Customizing output

Most messages that end up at the console (not yet all) are built from plaintext template files whose paths are set in `failure_message`, `diff_message`, and so on in the settings file. You can either change the paths or just edit the defaults in-place. What you see is what you get, newlines and all.


Changes
-------

This is version 0.2. If you want a version that won't change during the quarter, check out the `featurefreeze` branch when it becomes available to get no updates except bug fixes. [Issues](https://github.com/bulatb/yuno/issues), suggestions, and pull requests welcome.
