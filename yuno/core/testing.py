from __future__ import print_function

"""Classes for defining, loading, and running tests.

"""

import os
import re
import posixpath
import subprocess
import locale

from yuno.core.config import config
from yuno.core import errors, history

from .util import working_dir, posix_newlines, to_posix_path, multiline_fill


SOURCE_EXTENSION = config.source_extension
OUTPUT_EXTENSION = config.output_extension
ANSWER_EXTENSION = config.answer_extension
MATCH_ALL_TESTS = '**/*' + SOURCE_EXTENSION


def build_glob(phase=None, check=None):
    def to_glob_syntax(globlike):
        glob = re.sub(r'(\d-\d)', r'[\1]', globlike)
        glob = re.sub(r'^(\d+)([a-z]-[a-z])$', r'\1[\2]', glob)

        return glob

    phase_part = 'phase*'
    check_part = 'check*'

    if phase:
        phase_part = 'phase' + to_glob_syntax(phase)
    if check:
        check_part = 'check' + to_glob_syntax(check)
    return posixpath.join(phase_part, check_part, "*" + SOURCE_EXTENSION)


def build_regex(phase=None, check=None):
    def range_to_regex(range_string):
        # Filter out the simple cases first
        if range_string == '*':
            return '.*'
        # Matches: 3, 3a
        elif re.match(r'^(\d+[a-z]?)$', range_string):
            return range_string
        # Converts: 3a-c -> 3[a-c]
        elif re.match(r'^(\d+)([a-z]-[a-z])$', range_string):
            return re.sub(r'^(\d+)([a-z]-[a-z])', r'\1[\2]', range_string)

        # Matches: 2-3, 2-3a, 3a-4, 3a-3c
        range_bounds = re.match(r'(\d+)([a-z])?-(\d+)([a-z])?', range_string)

        left_bound = range_bounds.group(1)
        first_letter = range_bounds.group(2)

        right_bound = range_bounds.group(3)
        last_letter = range_bounds.group(4)

        middle = range(int(left_bound) + 1, int(right_bound))

        first_letter_pattern = '[%s-z]' % (first_letter or 'a')
        # Things like 18a-19 should start matching at 18a, not 18.
        first_letter_pattern += '?' if not first_letter else ''
        last_letter_pattern = '[a-%s]?' % (last_letter or 'z')

        patterns = []
        patterns.append(left_bound + first_letter_pattern)
        patterns.extend([str(n) + '[a-z]?' for n in middle])
        patterns.append(right_bound + last_letter_pattern)

        return '({0})'.format('|'.join(patterns))

    phase = range_to_regex(phase) if phase else r'\d+'
    check = range_to_regex(check) if check else r'\d+[a-z]?'

    return ['^phase%s$' % phase, '^check%s$' % check]
    # return re.compile('^/?phase{0}/check{1}/(.+)?$'.format(phase, check))


class TestComponent(object):
    """A test component is any file required for the test to run.

    Currently, a test named "Example" would have the following components:
        /some/path/Example.rc (source file)
        /some/path/Example.my.out (test output)
        /some/path/Example.ans.out (the expected output)

    Public attributes are:
        path - Path such that open(path) would open the file (path/to/file.ext)
        path_to - Dirname of path (/path/to)
        name - Basename of path, no extension (file)
        filename - Basename with extension (file.ext)

    """
    def __init__(self, path, path_to, name, filename):
        self.path = path
        self.path_to = path_to
        self.name = name
        self.filename = filename


class Test(object):
    def __init__(self, path):
        source_extension = re.escape(SOURCE_EXTENSION)
        path = re.sub(r'^\.{1,2}[/\\]', '', to_posix_path(path.strip()))

        path_to, filename = posixpath.split(path)
        name = os.path.splitext(filename)[0]

        answer_filename = name + ANSWER_EXTENSION
        output_filename = name + OUTPUT_EXTENSION

        self.source = TestComponent(path, path_to, name, filename)
        self.answer = TestComponent(
            posixpath.join(path_to, answer_filename),
            path_to,
            name,
            answer_filename
        )
        self.output = TestComponent(
            posixpath.join(path_to, output_filename),
            path_to,
            name,
            output_filename
        )


    def run_in_harness(self, harness):
        """Runs the test in the given harness, an object which implements
        test_failed(), test_skipped(), test_passed(), and test_warned().

        See testing.Harness for signatures.

        """
        classpath = os.pathsep.join(config.compiler_classpath)
        compile_command = config.compiler_invocation.format(
            classpath=classpath,
            compiler_executable=config.compiler_executable,
            testcase=self.source.path
        )

        output = ''

        try:
            # If a shell injection happens here, the attacker has already
            # gained write access to local files.
            # TODO: (#1) Use arg lists to allow command-line setting swapping
            output = subprocess.check_output(compile_command, shell=True)
        except subprocess.CalledProcessError as e:
            # The compiler process halted with a nonzero return code. It's best
            # not to assume this is a total failure, so let's warn them in case
            # they're just misusing exit codes.
            harness.test_warned(
                self,
                "Test `%s` finished with exit code %d." % (
                    compile_command, e.returncode
                )
            )
            output = e.output

        try:
            answer_file = open(self.answer.path)
            expected_output = answer_file.read()
            try:
                output = output.decode('utf-8')
            except AttributeError:
                pass

            if not self.passes(expected_output, output):
                harness.test_failed(self, output, expected_output)
            else:
                harness.test_passed(self, output)
        except IOError:
            message = "Unreadable or missing answer file " + self.answer.path
            harness.test_skipped(self, message)


    def passes(self, expected, actual):
        return posix_newlines(expected) == posix_newlines(actual)


    def __repr__(self):
        return "Test(\"%s\")" % self.source.path


    def __str__(self):
        return self.source.path


    def __lt__(self, other):
        return self.source.path < other.source.path


class Harness(object):
    def __init__(self, diff_routine=None, pause_controller=None):
        self.diff_routine = diff_routine
        self._pause = pause_controller or (lambda x: None)

        self._success_message = self._load_template(
            config.success_message,
            default='PASS: {test_path}/{test_name}'
        )
        self._failure_message = self._load_template(
            config.diff_message if diff_routine else config.failure_message,
            default='FAIL: {test_path}/{test_name}'
        )
        self._skip_message = self._load_template(
            config.skip_message,
            default='SKIP: {test_path}/{test_name} ({reason})'
        )
        self._warn_message = self._load_template(
            config.warn_message,
            default='WARN: {message}'
        )


    def _load_template(self, path, default=''):
        try:
            with open(path) as template:
                return template.read()
        except IOError:
            print("WARN: Could not read template: " + path)
            return default


    def _report_result(self, message_template, **kwargs):
        message = message_template
        for (placeholder, value) in kwargs.items():
            message = multiline_fill(placeholder, value, message)

        print(message)


    def test_passed(self, test, output):
        self.passed.append(test)
        self._report_result(
            self._success_message,
            test_path=test.source.path_to or '[repo root]',
            test_name=test.source.filename
        )
        self._pause('p')


    def test_failed(self, test, output, expected_output):
        fail_details = {
            'test_path': test.source.path_to or '[repo root]',
            'test_name': test.source.filename
        }

        if self.diff_routine:
            fail_details['diff'] = self.diff_routine(expected_output, output)
        else:
            fail_details['expected'] = expected_output
            fail_details['actual'] = output

        self._report_result(self._failure_message, **fail_details)
        self.failed.append(test)
        self._pause('f')


    def test_skipped(self, test, reason):
        self.skipped.append(test)
        self._report_result(
            self._skip_message,
            test_path=test.source.path_to or '[repo root]',
            test_name=test.source.filename,
            reason=reason
        )
        self._pause('s')


    def test_warned(self, test, message):
        self.warned.append(test)
        self._report_result(self._warn_message, message=message)
        self._pause('w')


    def run_test(self, test):
        test.run_in_harness(self)


    def run_set(self, test_set):
        self._start_run()

        if len(test_set) == 0:
            raise errors.EmptyTestSet()

        with working_dir(config.test_folder):
            for test in test_set:
                test.run_in_harness(self)

        self._finish_run()


    def _start_run(self):
        self._previously_failing = set()
        self._previously_passing = set()

        with working_dir(config.data_folder):
            try:
                read_or_create = os.O_RDONLY | os.O_CREAT
                failing = os.fdopen(os.open('failing.txt', read_or_create))
                passing = os.fdopen(os.open('passing.txt', read_or_create))
                self._previously_failing = set([f.strip() for f in failing])
                self._previously_passing = set([p.strip() for p in passing])
            except (IOError, OSError):
                print("WARN: Failed to load history. Results won't be saved.")
                self._history_off = True
            finally:
                failing.close()
                passing.close()

        self.passed = []
        self.failed = []
        self.skipped = []
        self.warned = []
        self.regressions = set()
        self.fixes = set()


    def _finish_run(self):
        if self.__dict__.get('_history_off') == True:
            return

        failed = [str(test) for test in self.failed]
        passed = [str(test) for test in self.passed]
        self.regressions = sorted(self._previously_passing.intersection(failed))
        self.fixes = sorted(self._previously_failing.intersection(passed))

        # Making sure to account for tests that weren't run this time.
        now_passing = self._previously_passing.union(passed).difference(failed)
        now_failing = self._previously_failing.union(failed).difference(passed)

        with working_dir(config.data_folder):
            Suite(None, 'passing.txt', sorted(now_passing)).save()
            Suite(None, 'failing.txt', sorted(now_failing)).save()
            # with open('passing.txt', 'w+') as passing:
            #     passing.writelines([str(test) + '\n' for test in now_passing])

            # with open('failing.txt', 'w+') as failing:
            #     failing.writelines([str(test) + '\n' for test in now_failing])

        record = history.RunRecord(
            regressions=self.regressions,
            fixes=self.fixes,
            passed=self.passed,
            failed=self.failed,
            skipped=self.skipped,
            warned=self.warned
        )
        record.save()


class Suite(object):
    @staticmethod
    def from_file(filename, test_class=Test):
        try:
            suite_name = os.path.basename(filename).replace('.txt', '')
            tests = load_from_file(filename, test_class=test_class)
            return Suite(suite_name, filename, tests)
        except IOError:
            raise errors.SuiteLoadError(filename)


    @staticmethod
    def from_name(name, test_class=Test):
        for folder in config.suite_folders:
            filename = posixpath.join(folder, name + '.txt')
            if os.path.isfile(filename):
                return Suite.from_file(filename, test_class=test_class)

        raise errors.SuiteLoadError(name)


    def __init__(self, name, filename, tests):
        self.name = name
        self.filename = filename
        self.tests = tests


    def save(self, filename=None):
        if not filename:
            filename = self.filename

        try:
            with open(filename, 'w+') as suite_file:
                suite_file.writelines(
                    [str(t) + '\n' for t in self.tests]
                )
        except IOError:
            raise errors.SuiteSaveError(self.name, self.filename)


# Poor test loaders have to be all the way down here. :(


def load_from_glob(file_glob, test_class=Test):
    """Finds all test files matched by [file_glob] and returns them as a list
    of [test_class] objects.

    """
    if '/**' in file_glob or '**/' in file_glob:
        globlib = __import__('yuno.core.recursive_glob', fromlist=['yuno.core'])
    else:
        globlib = __import__('glob')

    tests = []

    with working_dir(config.test_folder):
        return sorted([test_class(path) for path in globlib.glob(file_glob)])


def load_from_file(name_or_handle, test_class=Test, line_filter=None):
    """Reads a file containing paths to test files (dirnames + basenames) and
    returns them as a list of [test_class] objects. Any non-blank,
    non-whitespace line is treated as a valid path.

    [name_or_handle] is a filename or an open file-like object. If an open file
    is given, it will be fully read but won't be closed.

    [line_filter] is an optional function that takes a line and returns either
    False or a string. If truthy, its output will be used in place of the
    original line.

    """
    line_filter = (lambda x: x) if line_filter is None else line_filter

    def get_tests(handle):
        tests = []

        for line in handle:
            if line.strip() == '':
                continue

            line = line_filter(line)
            if line:
                tests.append(test_class(line))

        return tests


    with errors.converted((IOError, OSError), to=errors.DataFileError):
        try:
            with open(name_or_handle) as file_handle:
                return get_tests(file_handle)
        except TypeError:
            # Got passed an open file. Read it, but don't close it.
            return get_tests(name_or_handle)

    return sorted(tests)


def load_all(test_class=Test, filter_fn=None):
    """Returns all the tests (files ending in `config.source_extension`) in the
    repository as a list of [test_class] objects.

    If [filter_fn] is given, includes only tests for which it returns True.

    """
    tests = []
    with working_dir(config.test_folder):
        for root, dirs, files in os.walk('.'):
            for filename in files:
                if filename.endswith(config.source_extension):
                    tests.append(
                        # [2:] strips the ./ added by os.walk()
                        test_class(posixpath.join(root, filename)[2:])
                    )

    if filter_fn:
        return sorted(filter(filter_fn, tests))

    return sorted(tests)


def load_from_regex(compiled_pattern, test_class=Test):
    """Returns all tests in the repository whose source file's full path
    matches [compiled_pattern] as a list of [test_class] objects. This loader
    is probably the slowest in the average case.

    """
    def regex_filter(test_case):
        return compiled_pattern.match(test_case.source.path)

    return load_all(test_class=test_class, filter_fn=regex_filter)


def load_by_walking(search_path, test_class=Test):
    """Searches the repo for tests along [search_path], level by level,
    regex-matching folder names and discarding any trees that fail. Prefer this
    over load_regex() for paths whose patterns can be cleanly separated into
    tokens and definitely won't need any backtracking.

    [search_path] should be a list of strings (not compiled regexes) containing
    patterns to match against subfolder names, one for each level of depth.
    Matching will continue til a pattern fails or that depth has been reach, at
    which point any tests found in the bottom folder are returned.

    For example, ['phase(1|2|12)', 'check.*'] will match:
        phase1/check2/
        phase12/check-xyz/
    but won't match:
        phase1/check2/check3/

    """
    isfile, isdir = (os.path.isfile, os.path.isdir)

    def find_tests(folder):
        def is_test(filename):
            is_file = isfile(os.path.join(folder, filename))
            return is_file and filename.endswith(SOURCE_EXTENSION)

        tests = []
        for entry in os.listdir(folder):
            if is_test(entry):
                tests.append(test_class(posixpath.join(folder, entry)))
        return tests

    def search_folder(folder, search_path):
        tests = []

        if len(search_path) == 0:
            return find_tests(folder)
        else:
            folder_contents = os.listdir(folder)

            for item in folder_contents:
                item_path = posixpath.join(folder, item)
                if isdir(item_path) and re.match(search_path[0], item):
                    tests += search_folder(
                        posixpath.join(folder, item), search_path[1:]
                    )
            return tests

    with working_dir(config.test_folder):
        return sorted(search_folder('.', search_path))
