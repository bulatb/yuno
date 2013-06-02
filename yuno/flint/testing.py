import os
from posixpath import join as path_from
import shutil
import subprocess

from yuno import core
from yuno.core import errors, testing
from yuno.core.util import working_dir
from yuno.core.config import config


class FlintTest(core.testing.Test):
    def __init__(self, path):
        super(FlintTest, self).__init__(path)


    def run_in_harness(self, harness):
        classpath = os.pathsep.join(config.compiler_classpath)
        compile_command = config.compiler_invocation.format(
            classpath=classpath,
            compiler_executable=config.compiler_executable,
            testcase=self.source.path
        )

        try:
            subprocess.check_output(compile_command, shell=True)
            asm_last_written = 0

            try:
                asm_last_written = os.stat(
                    config.compiler_output_file).st_mtime
            except OSError as e:
                print("fails here")
                print(e)
                harness.test_failed(self, "", "")
                return

            # print("mtime: " + str(asm_last_written))
            # print("last success: " + str(harness.last_success_at))

            if asm_last_written > harness.last_success_at:
                harness.test_passed(self, "")
                harness.last_success_at = asm_last_written
            else:
                harness.test_failed(self, "", "")
        except subprocess.CalledProcessError as e:
            harness.test_passed(self, e.output)
            harness.test_warned(
                self,
                "Test `%s` finished with exit code %d." % (
                    compile_command, e.returncode
                )
            )


class AssemblyGenerator(core.testing.Harness):
    def __init__(self, pause_controller=None, diff_routine=None):
        super(AssemblyGenerator, self).__init__()
        self.last_success_at = 0


    def test_passed(Self, test, output):
        filename = path_from(test.source.path_to, test.source.name) + '.s'
        # filename = filename.replace('/', '_')
        saved_output_filename = filename + '.most-recent'

        try:
            shutil.copyfile(config.compiler_output_file,
                path_from(config.assembly_output_folder, filename))
            shutil.copyfile(config.compiler_output_file,
                path_from(config.assembly_output_folder, saved_output_filename))
            print("DONE: " + filename)
        except OSError as e:
            print(e)
            print("FAIL: could not copy {} to {}".format(
                filename, config.assembly_output_folder))


    def test_failed(self, test, output, expected_output):
        print("FAIL: " + test.source.path)
        print("      No assembly written to " + config.compiler_output_file)


    def test_skipped(self, test, reason):
        pass


    def test_warned(self, test, message):
        pass


    def run_set(self, test_set):
        if len(test_set) == 0:
            raise errors.EmptyTestSet()

        with working_dir(config.test_folder):
            for test in test_set:
                test.run_in_harness(self)

        try:
            done_file = open(
                path_from(config.assembly_output_folder, '.done'), 'w+')
            done_file.close()
        except OSError:
            print("-" * 80)
            print("\nWARN: Failed to close this batch of tests.")
            print("      Run `yuno steel --finish` on ieng9 to fix this.")

