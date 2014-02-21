import sys

import yuno.core.config as config
from yuno.run import run

from .testing import AssemblyGenerator, FlintTest


def main(options):
    # Hack
    run.HARNESS = AssemblyGenerator
    run.TEST_CLASS = FlintTest

    # Haaaaaack
    run._display_results = (lambda x: None)

    print("\nRunning your compiler to generate assembly files.")
    print("=" * 80)
    print("")

    run.main(options)

    print("")
    print("=" * 80)
    print("Done.")
