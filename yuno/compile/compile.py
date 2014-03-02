import sys

from yuno.run import cli as run_cli, run

from .testing import AssemblyGenerator, AssemblyWritingTest


def main(argv):
    print("\nRunning your compiler to generate assembly files.")
    print("=" * 80, end='\n\n')

    args, _ = run_cli.get_cli_args(argv)
    run.load_and_run(AssemblyGenerator(), AssemblyWritingTest, args)

    print("")
    print("=" * 80)
    print("Done.")
