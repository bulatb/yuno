import os
import posixpath
import re
import sys

from yuno import core
from yuno.core import testing, errors, util
from yuno.core.config import config

import cli
import diff_routines
import text


def _build_regex_filter(regex):
    regex = re.compile(regex)

    def filter_function(test_case):
        return re.match(test_case.source.path)

    return filter_function


# TODO: This function was designed before the diff feature was added. Having to
# pass [options] sucks.
def _run_tests(options, test_set=None, glob=None):
    def pause_controller(test_result):
        if test_result in (options.pause_on or []):
            raw_input("Paused. Press Enter to continue.\n")


    if glob is not None:
        test_set = core.testing.load_from_glob(glob)

    harness = core.testing.Harness(
        diff_routine=diff_routines.__dict__.get(options.diff_mode),
        pause_controller=pause_controller if options.pause_on else None
    )
    harness.run_set(test_set or [])

    return (harness, test_set)


def _run_regex(options, pattern):
    """Runs every test in the repo whose path matches [pattern]. Expects a
    compiled regex.

    TODO: Expose this via --regex flag.
    """
    test_set = core.testing.load_all(
        filter_fn=(lambda test: pattern.match(test.source.path))
    )

    return _run_tests(options, test_set=test_set)


def _run_all(options):
    """$ yuno run all
    """
    print "Running all tests in %s\n" % config.test_folder
    return _run_tests(
        options, test_set=core.testing.load_all()
    )


def _run_glob(options):
    """$ yuno run <glob>
    """
    print "Running tests in {} and subfolders:\n".format(options.glob)

    glob = options.glob.strip()
    return _run_tests(
        options, glob=posixpath.join(glob, '**', '*' + config.source_extension)
    )


def _run_pipe(options):
    """$ <stream> | yuno run -
    """
    print "Running tests from pipe:\n"

    test_set = core.testing.load_from_file(
        sys.stdin, line_filter=util.strip_line_labels
    )
    return _run_tests(options, test_set=test_set)


def _run_phase(options):
    """$ yuno run phase <#>
    """
    print "Running phase %s:\n" % options.phase

    options.check = '*'
    return _run_phase_and_check(options)


def _run_check(options):
    """$ yuno run check <#>
    """
    print "Running check %s:\n" % options.check

    options.phase = '*'
    return _run_phase_and_check(options)


def _run_phase_and_check(options):
    """$ yuno run phase <#> check <#>
    """
    phase = options.phase.strip() if options.phase else '*'
    check = options.check.strip() if options.check else '*'
    valid_arg = re.compile(r'^\d+[a-z]?(-\d+[a-z]?)?$|^\d+[a-z]-[a-z]$|^\*$')
    send_to_globber = re.compile(
        #  3, 12a      6a-c            6a-6c                 *
        r'^\d+[a-z]?$|^\d+[a-z]-[a-z]$|^(\d+)[a-z]-\1[a-z]$|^\*$'
    )

    # Convert the 6a-6z form to the 6a-z short form for globbing. This also
    # cuts out some unnecessary processing in regex mode, so win-win.
    phase = re.sub(r'^(\d+)([a-z])-\1([a-z])$', r'\1\2-\3', phase)
    check = re.sub(r'^(\d+)([a-z])-\1([a-z])$', r'\1\2-\3', check)

    # Keep the * option undocumented. It's a quirk and not particularly helpful.
    if not valid_arg.match(phase) or not valid_arg.match(check):
        raise core.errors.YunoError(text.BAD_PHASE_OR_CHECK)

    # Loading files by glob is faster, but the globber only takes single-digit
    # or -character ranges and can't do optional sequences. Exact matches (6a)
    # and ranges within a single check number (6a-6c, 6a-c) can be globbed;
    # others like 5-7 (5[a-z]?|6[a-z]?|7[a-z]?) and 5b-6a (5[b-z]|6[a-a]) have
    # to go through regex matching.
    if not send_to_globber.match(phase) or not send_to_globber.match(check):
        search_path = core.testing.build_regex(phase=phase, check=check)
        test_set = core.testing.load_by_walking(search_path)
        return _run_tests(options, test_set=test_set)
    else:
        glob = core.testing.build_glob(phase=phase, check=check)
        return _run_tests(options, glob=glob)


def _run_failed(options):
    """$ yuno run failed
    """
    def is_failed(test_path):
        return test_path[2:] if test_path.startswith('f ') else False


    print "Running tests that failed last time:\n"

    try:
        test_set = core.testing.load_from_file(
            'data/last-run.txt', line_filter=is_failed
        )
        return _run_tests(options, test_set=test_set)
    except core.errors.DataFileError as e:
        e.message = 'Unreadable or missing run log. Have you run any tests?'
        raise e


def _run_failing(options):
    """$ yuno run failing
    """
    print "Running all tests currently failing:\n"
    return _run_suite(options, filename='data/failing.txt')


def _run_passed(options):
    """$ yuno run passed
    """
    def is_passed(test_path):
        return test_path[2:] if test_path.startswith('p ') else False


    print "Running all tests that passed last time:\n"

    try:
        test_set = core.testing.load_from_file(
            'data/last-run.txt', line_filter=is_passed
        )
        return _run_tests(options, test_set=test_set)
    except core.errors.DataFileError as e:
        e.message = 'Unreadable or missing run log. Have you run any tests?'
        raise e


def _run_passing(options):
    """$ yuno run passing
    """
    print "Running all tests currently passing:\n"
    return _run_suite(options, filename='data/passing.txt')


def _run_files(options):
    """$ yuno run files <glob>
    """
    print "Running any test that matches {}:\n".format(options.files)
    return _run_tests(options, glob=options.files.strip())


def _run_suite(options, filename=None):
    """$ yuno run suite <name>
    """
    if filename is None:
        suite_name = options.suite.strip()
        suite = core.testing.Suite.from_name(suite_name)
        print "Running {0} ({1.filename}):\n".format(suite_name, suite)

    else:
        suite = core.testing.Suite.from_file(filename)

    return _run_tests(options, test_set=suite.tests)


def _save_suite(name, tests, overwrite=False):
    filename = posixpath.join(config.suite_folders[0], name + '.txt')

    if os.path.isfile(filename) and not overwrite:
        print "\nSuite %s already exists. Use --save %s -o to overwrite." % (
            name, name
        )
        return

    try:
        core.testing.Suite(name, filename, tests).save()
        print "\nSaved these tests as %s (%s.txt)." % (
            name, posixpath.join(config.suite_folders[0], name)
        )
    except core.errors.SuiteSaveError as e:
        print e.for_console()
        print "Please try again or check the permissions."


def _display_results(harness):
    num_passed = len(harness.passed)
    num_failed = len(harness.failed)
    num_skipped = len(harness.skipped)
    num_warned = len(harness.warned)
    num_regressions = len(harness.regressions)
    num_fixes = len(harness.fixes)
    total = num_passed + num_failed + num_skipped

    print "=" * 80
    print "Ran %d tests\n" % total
    print "  %d passed" % num_passed
    print "  %d failed" % num_failed

    if num_failed > 0:
        print "      View?   yuno.py show failed"
        print "      Re-run? yuno.py run failed"
        # note about diff files goes here

    if num_skipped > 0:
        print "  %d skipped" % num_skipped
        print "      View? yuno.py show skipped"

    if num_warned > 0:
        print "  %d warned" % num_warned
        print "      View? yuno.py show warned"

    if num_regressions > 0:
        print "\n- %d %s\n   " % (
            num_regressions,
            util.nice_plural(num_regressions, 'regression', 'regressions')
        ),
        print "\n    ".join([str(test) for test in sorted(harness.regressions)])

    if num_fixes > 0:
        print "\n+ %d fixed :)\n   " % num_fixes,
        print "\n    ".join([str(test) for test in sorted(harness.fixes)])


def main(argv=sys.argv):
    options, parser = cli.get_cli_args(argv)

    if options.command is None:
        parser.print_help()
        sys.exit(2)

    command_handlers = {
        cli.RUN_ALL: _run_all,
        cli.RUN_FAILED: _run_failed,
        cli.RUN_FAILING: _run_failing,
        cli.RUN_PASSED: _run_passed,
        cli.RUN_PASSING: _run_passing,
        cli.RUN_GLOB: _run_glob,
        cli.RUN_PHASE: _run_phase,
        cli.RUN_CHECK: _run_check,
        cli.RUN_PHASE_AND_CHECK: _run_phase_and_check,
        cli.RUN_SUITE: _run_suite,
        cli.RUN_FILES: _run_files,
        cli.RUN_PIPE: _run_pipe
    }

    try:
        harness, test_set = command_handlers[options.command](options)
        _display_results(harness)

        if options.save_as:
            _save_suite(options.save_as, test_set, overwrite=options.overwrite)

    except core.errors.SuiteLoadError as e:
        print e.for_console()
        print "To see what suites are available, use:"
        print "    yuno.py show suites"

    except core.errors.EmptyTestSet as e:
        print e.for_console()

        if options.command == cli.RUN_GLOB:
            print "To run specific tests, use:"
            print "    yuno.py run files path/to/test*.rc"

        commands_using_globs = (cli.RUN_GLOB, cli.RUN_FILES)
        if options.command in commands_using_globs and os.name == 'posix':
            print text.SHELL_GLOB_EXPANSION_WARNING
        # TODO: this.
        # if options.command == cli.RUN_SUITE:
        #     print "To see its contents, use:"
        #     print "    yuno.py show suite {}".format(options.suite)

    except core.errors.YunoError as e:
        print e.for_console()

    except KeyboardInterrupt:
        print "Run stopped. Results were not recorded."
