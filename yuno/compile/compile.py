from __future__ import print_function

import sys

from yuno.run import cli as run_cli, run

from .testing import AssemblyGenerator, AssemblyWritingTest


def main(argv):
    print("\nRunning your compiler to generate assembly files.")
    print("=" * 80, end='\n\n')

    args, _ = run_cli.get_cli_args(argv)
    _, test_set = run.load_and_run(
        args,
        harness=AssemblyGenerator(),
        test_class=AssemblyWritingTest,
        message="Compiling {which_tests}:")

    if len(test_set) > 0 and args.save_as is not None:
        run.save_suite(args.save_as, test_set, overwrite=args.overwrite)

    print("")
    print("=" * 80)
    print("Done.")
