usage = "%(prog)s show [-h] <what>"

description = """\
details:
  show fail[ed|ing]
      failed: every test that failed on the last run
      failing: every test that hasn't passed since it last failed

  show pass[ed|ing]
      passed: every test that passed on the last run
      passing: every test that hasn't failed since it last passed

  show skipped|warned
      every test that skipped or warned on the last run, respectively

  show last
      a log of the last run

  show suites
      a list of suites Yuno is tracking

"""
