from __future__ import print_function

import difflib
import os
import re
import subprocess
import sys

from yuno import core
from yuno.core import errors, util
from yuno.core.config import config


_read_input = raw_input if sys.version_info[0] == 2 else input


def _prompt(message):
    answer = _read_input(message)
    while answer not in ('y', 'n'):
        answer = _read_input(message)

    return answer


class NaiveTest(core.testing.Test):
    def __init__(self, path):
        super(NaiveTest, self).__init__(path)


    def run_in_harness(self, harness):
        classpath = os.pathsep.join(config.compiler_classpath)
        compile_command = config.compiler_invocation.format(
            classpath=classpath,
            compiler_executable=config.compiler_executable,
            testcase=self.source.path
        )

        try:
            output = subprocess.check_output(
                compile_command, shell=True, universal_newlines=True)
            harness.test_passed(self, output)
        except subprocess.CalledProcessError as e:
            harness.test_passed(self, e.output)
            harness.test_warned(
                self,
                "Test `%s` finished with exit code %d." % (
                    compile_command, e.returncode
                )
            )


class AnswerGeneratingHarness(core.testing.Harness):
    def __init__(self, interactive=True, force_overwrite=False):
        self.interactive = interactive
        self.force_overwrite = force_overwrite

        self._result_message = self._load_template(
            'settings/templates/certify-answer.txt',
            default='TEST: {test_path}/{test_name}\n%sOutput below.\n%s\n%s' % (
                '      ', ('-' * 80), '{output}'
            )
        )
        self._warn_message = self._load_template(
            'settings/templates/certify-warning.txt',
            default=('=' * 80) + 'WARN: {message}' + ('=' * 80)
        )
        self._existing_answer_message = self._load_template(
            'settings/templates/certify-existing-answer.txt',
            default='NOTE: This test already has an answer file.\n{diff}'
        )


    def _generate_answer_file(self, path, contents):
        with errors.converted((IOError, OSError), to=errors.DataFileError):
            with open(path, 'w+') as answer_file:
                answer_file.writelines(contents.splitlines(True))


    def _confirm_overwrite(self):
        if self.force_overwrite:
            return True

        return _prompt("Overwrite existing answer file? (y/n) ") == 'y'


    def _confirm_correctness(self):
        if not self.interactive:
            return True

        return _prompt("Is that the correct output? (y/n) ") == 'y'


    def _certify(self, test, output):
        if not self._confirm_correctness():
            print("-- Changes discarded.")
            return

        if not os.path.isfile(test.answer.path):
            self._generate_answer_file(test.answer.path, output)
            print("++ Answer file created.")
        else:
            print(self._existing_answer_message.format(
                diff=''.join(
                    difflib.unified_diff(
                        open(test.answer.path, 'rU').readlines(),
                        output.splitlines(True),
                        fromfile=test.answer.filename,
                        tofile='proposed answer file'
                    )
                )
            ))

            if self._confirm_overwrite():
                print("++ Answer file updated.")
                self._generate_answer_file(test.answer.path, output)
            else:
                print("-- Answer discarded.")


    def test_passed(self, test, output):
        output = util.posix_newlines(output)

        print(self._result_message.format(
            test_path=test.source.path_to or '[repo root]',
            test_name=test.source.filename,
            output=output
        ))
        self._certify(test, output)

        print("\n\n" + ("=" * 80) + "\n\n")


    def test_warned(self, test, message):
        print(self._warn_message.format(message=message))


    def run_set(self, test_set):
        if len(test_set) == 0:
            raise errors.EmptyTestSet('No tests to certify')

        with util.working_dir(config.test_folder):
            for test in test_set:
                test.run_in_harness(self)
