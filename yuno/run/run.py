from __future__ import print_function

from functools import partial
import os
import posixpath
import re
import sys

from yuno import core
from yuno.core import testing, errors, util
from yuno.core.config import config

from . import cli
from . import diff_routines
from . import text


def _build_regex_filter(regex):
    regex = re.compile(regex)

    def filter_function(test_case):
        return re.match(test_case.source.path)

    return filter_function


def _data_file(filename):
    return posixpath.join(config.data_folder, filename)


def _run_regex(options, pattern):
    """Runs every test in the repo whose path matches [pattern]. Expects a
    compiled regex.

    TODO: Expose this via --regex flag.
    """
    test_set = core.testing.load_all(
        filter_fn=(lambda test: pattern.match(test.source.path)),
        test_class=TEST_CLASS
    )

    return run(harness, test)


def _all_tests(test_class, options):
    """$ yuno run all
    """
    message = "everything (%s)" % config.test_folder
    return (core.testing.load_all(test_class=test_class), message)


def _tests_matching_path_glob(test_class, options):
    """$ yuno run <glob>
    """
    message = "tests in {} and subfolders".format(options.glob)

    glob = posixpath.join(options.glob, '**', '*' + config.source_extension)
    test_set = core.testing.load_from_glob(glob, test_class=test_class)

    return (test_set, message)


def _tests_from_pipe(test_class, options):
    """$ <stream> | yuno run -
    """
    message = "tests from pipe"

    test_set = core.testing.load_from_file(
        sys.stdin, line_filter=util.strip_line_labels, test_class=test_class)

    return (test_set, message)


def _tests_in_phase(test_class, options):
    """$ yuno run phase <#>
    """
    message = "phase %s" % options.phase

    options.check = '*'
    return (_tests_in_phase_and_check(test_class, options)[0], message)


def _tests_in_check(test_class, options):
    """$ yuno run check <#>
    """
    message = "check %s" % options.check

    options.phase = '*'
    return (_tests_in_phase_and_check(test_class, options)[0], message)


def _tests_in_phase_and_check(test_class, options):
    """$ yuno run phase <#> check <#>
    """
    phase = options.phase.strip() if options.phase else '*'
    check = options.check.strip() if options.check else '*'
    message = "phase %s, check %s" % (phase, check)
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
        test_set = core.testing.load_by_walking(
            search_path, test_class=test_class)
        return (test_set, message)
    else:
        glob = core.testing.build_glob(phase=phase, check=check)
        test_set = core.testing.load_from_glob(glob, test_class=test_class)
        return (test_set, message)


def _failed_tests(test_class, options):
    """$ yuno run failed
    """
    def is_failed(test_path):
        return test_path[2:] if test_path.startswith('f ') else False


    message = "tests that failed last time"

    try:
        test_set = core.testing.load_from_file(
            _data_file('last-run.txt'),
            line_filter=is_failed,
            test_class=test_class)
        return (test_set, message)
    except core.errors.DataFileError as e:
        e.message = 'Unreadable or missing run log. Have you run any tests?'
        raise e


def _failing_tests(test_class, options):
    """$ yuno run failing
    """
    message = "all tests currently failing"
    test_set = _tests_in_suite(
        test_class, options, filename=_data_file('failing.txt'))[0]
    return (test_set, message)


def _passed_tests(test_class, options):
    """$ yuno run passed
    """
    def is_passed(test_path):
        return test_path[2:] if test_path.startswith('p ') else False


    message = "all tests that passed last time"

    try:
        test_set = core.testing.load_from_file(
            _data_file('last-run.txt'),
            line_filter=is_passed,
            test_class=test_class)
        return (test_set, message)
    except core.errors.DataFileError as e:
        e.message = 'Unreadable or missing run log. Have you run any tests?'
        raise e


def _passing_tests(test_class, options):
    """$ yuno run passing
    """
    message = "all tests currently passing"
    test_set = _tests_in_suite(
        test_class, options, filename=_data_file('passing.txt'))[0]

    return (test_set, message)


def _tests_matching_file_glob(test_class, options):
    """$ yuno run files <glob>
    """
    message = "any test that matches %s" % options.files
    return (core.testing.load_from_glob(
        options.files, test_class=test_class), message)


def _tests_in_suite(test_class, options, filename=None):
    """$ yuno run suite <name>
    """
    if filename is None:
        suite_name = options.suite.strip()
        suite = core.testing.Suite.from_name(suite_name, test_class=test_class)
        message = "{0} ({1.filename})".format(suite_name, suite)
    else:
        message = filename
        suite = core.testing.Suite.from_file(filename, test_class=test_class)

    return (suite.tests, message)


def save_suite(name, tests, overwrite=False):
    filename = posixpath.join(config.suite_folders[0], name + '.txt')

    if os.path.isfile(filename) and not overwrite:
        print(text.SUITE_ALREADY_EXISTS.format(suite_name=name))
        return

    try:
        core.testing.Suite(name, filename, tests).save()
        print("\nSaved these tests as {} ({}.txt).".format(
            name, posixpath.join(config.suite_folders[0], name)))
    except core.errors.SuiteSaveError as e:
        print(e.for_console())
        print("Please try again or check the permissions.")


def build_pauser(to_pause_on):
    def pauser(test_result):
        if test_result in to_pause_on:
            input("Paused. Press Enter to continue.\n")

    return pauser if to_pause_on is not None else None


def display_results(harness):
    num_passed = len(harness.passed)
    num_failed = len(harness.failed)
    num_skipped = len(harness.skipped)
    num_warned = len(harness.warned)
    num_regressions = len(harness.regressions)
    num_fixes = len(harness.fixes)
    total = num_passed + num_failed + num_skipped

    print("=" * 80)
    print("Ran %d %s\n" % (total, util.nice_plural(total, 'test', 'tests')))
    print("  %d passed" % num_passed)
    print("  %d failed" % num_failed)

    if num_failed > 0:
        print("      View?   yuno show failed")
        print("      Re-run? yuno run failed")
        # note about diff files goes here

    if num_skipped > 0:
        print("  %d skipped" % num_skipped)
        print("      View? yuno show skipped")

    if num_warned > 0:
        print("  %d warned" % num_warned)
        print("      View? yuno show warned")

    if num_regressions > 0:
        print("\n- %d %s\n    " % (
            num_regressions,
            util.nice_plural(num_regressions, 'regression', 'regressions')),
            end='')
        print("\n    ".join([str(r) for r in sorted(harness.regressions)]))

    if num_fixes > 0:
        print("\n+ %d fixed :)\n    " % num_fixes, end='')
        print("\n    ".join([str(f) for f in sorted(harness.fixes)]))


def get_loader(command):
    return {
        cli.RUN_ALL: _all_tests,
        cli.RUN_GLOB: _tests_matching_path_glob,
        cli.RUN_PIPE: _tests_from_pipe,
        cli.RUN_PHASE: _tests_in_phase,
        cli.RUN_CHECK: _tests_in_check,
        cli.RUN_PHASE_AND_CHECK: _tests_in_phase_and_check,
        cli.RUN_FAILED: _failed_tests,
        cli.RUN_FAILING: _failing_tests,
        cli.RUN_PASSED: _passed_tests,
        cli.RUN_PASSING: _passing_tests,
        cli.RUN_FILES: _tests_matching_file_glob,
        cli.RUN_SUITE: _tests_in_suite
    }[command]


def build_harness(options, harness_class=core.testing.Harness):
    diff_routine = diff_routines.__dict__.get(options.diff_mode)
    pauser = build_pauser(options.pause_on)

    return harness_class(
        diff_routine=diff_routine, pause_controller=pauser)


def load_tests(test_class, args):
    return get_loader(args.command)(test_class, args)


def run_tests(test_set, harness):
    harness.run_set(test_set)
    return harness


def load_and_run(args, harness=None, test_class=None, loader=None, message=None):
    message = message or "Running {which_tests}:"
    harness = harness or build_harness(args)
    test_set = []

    test_class = test_class or core.testing.Test
    loader = loader or partial(_load_excluding_patterns, args.ignore_patterns)

    try:
        test_set, description = loader(test_class, args)
        message = message.format(which_tests=description)

        print(message + '\n')
        run_tests(test_set, harness)

    # Might be thrown by the loader.
    except core.errors.SuiteLoadError as e:
        print(e.for_console())
        print("To see what suites are available, use:")
        print("    yuno show suites")

    # Might be thrown by the harness.
    except core.errors.EmptyTestSet as e:
        print(e.for_console())

        if args.command == cli.RUN_GLOB:
            print("To run specific tests, use:")
            print("    yuno run files path/to/test*.rc")

        commands_using_globs = (cli.RUN_GLOB, cli.RUN_FILES)
        if args.command in commands_using_globs and os.name == 'posix':
            print(text.SHELL_GLOB_EXPANSION_WARNING)
        # TODO: this.
        # if args.command == cli.RUN_SUITE:
        #     print("To see its contents, use:")
        #     print("    yuno.py show suite {}".format(args.suite))

    # Might be thrown by anything.
    except core.errors.YunoError as e:
        print(e.for_console())

    except KeyboardInterrupt:
        print("Run stopped. Results were not recorded.")

    return harness, test_set or []


def _load_excluding_patterns(patterns, test_class, args):
    test_set, description = load_tests(test_class, args)

    for p in patterns or []:
        test_set = [t for t in test_set if not re.search(p, t.source.path)]

    return test_set, description


def main(argv):
    args, parser = cli.get_cli_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(2)

    harness, test_set = load_and_run(args)

    if len(test_set) < 1:
        return

    display_results(harness)

    if args.save_as is not None:
        save_suite(args.save_as, test_set, overwrite=args.overwrite)
