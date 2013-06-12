import os
import posixpath

from yuno.core import errors, history, testing
from yuno.core.config import config

from . import cli


def _remove_deleted_tests(suite, available_tests):
    still_good = []
    num_removed = 0

    for test in suite.tests:
        if test.source.path in available_tests:
            still_good.append(test)
        else:
            num_removed += 1

    suite.tests = still_good
    return (suite, num_removed)


def _prune_last_run(available_tests):
    metrics = ['regressions', 'fixes', 'passed', 'failed', 'skipped', 'warned']
    last_run = history.RunRecord.from_last_run()
    num_removed = 0

    for field_name in metrics:
        test_paths = last_run.__dict__[field_name]
        still_good = []

        for path in test_paths:
            if path in available_tests:
                still_good.append(path.strip())
            else:
                num_removed += 1

        last_run.__dict__[field_name] = still_good

    last_run.save()
    return num_removed


def _prune_suites(available_tests):
    suite_folder = config.suite_folders[0]
    results = []

    for item in os.listdir(suite_folder):
        path = posixpath.join(suite_folder, item)

        if os.path.isfile(path) and item.endswith('.txt'):
            suite = testing.Suite.from_file(path)
            results.append(_remove_deleted_tests(suite, available_tests))
            suite.save()

    return results


def _print_interrupt_warning():
    print("WARN: Pruning interrupted.")
    print("WARN: Your history may now be inconsistent, but that's ok.")
    print("      To fix it, run some tests or run yuno prune again.")


def main(argv):
    options, parser = cli.get_cli_args(argv)

    valid_paths = set([test.source.path for test in testing.load_all()])
    listed_passing = testing.Suite.from_file('data/passing.txt')
    listed_failing = testing.Suite.from_file('data/failing.txt')

    valid_passing = _remove_deleted_tests(listed_passing, valid_paths)
    valid_failing = _remove_deleted_tests(listed_failing, valid_paths)

    try:
        print("Removing deleted tests from your history...\n")

        valid_passing[0].save()
        print("Pruned %d bad paths from passing test list." % valid_passing[1])

        valid_failing[0].save()
        print("Pruned %d bad paths from failing test list." % valid_failing[1])

        if options.prune_last or options.prune_all:
            pruned_from_log = _prune_last_run(valid_paths)
            print("\nPruned %d items from the run log." % pruned_from_log)

        if options.prune_suites or options.prune_all:
            print("")
            for suite, num_removed in _prune_suites(valid_paths):
                print("Pruned %d bad paths from suite %s (%s)." % (
                    num_removed, suite.name, suite.filename
                ))

    except errors.YunoError as e:
        print(e.for_console())
        _print_interrupt_warning()

    except KeyboardInterrupt:
        _print_interrupt_warning()

    except BaseException:
        _print_interrupt_warning()
        print("\nReason below:" + ('-' * 80))
        raise