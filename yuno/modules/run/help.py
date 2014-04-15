usage = """%(prog)s run [-h] all
  or   %(prog)s run <glob>
  or   %(prog)s run phase <#> check <#>
  or   %(prog)s run phase <#>
  or   %(prog)s run check <#>
  or   %(prog)s run suite <name>
  or   stream | %(prog)s run -

"""

description = """\
note:
  all forms support the optional arguments below

details:
  run all
      run every test in the test folder, searching recursively

  run <glob>
      run all tests in folders matching this glob
      Ex: %(prog)s run phase1/check[1-3]

  run fail(ed|ing)
      failed: run all tests that failed on the last run
      failing: run all tests that haven't passed since they last failed

  run pass(ed|ing)
      passed: run all tests that passed on the last run
      passing: run all tests that haven't failed since they last passed

  run files <glob>
      run specific files (as opposed to run <glob>, which runs all files in
      any folders matched by <glob>)

  run -
      run a newline-delimited stream of file paths given through a pipe
      Ex: %(prog)s run - < some-tests.txt

  run (phase|check) <#>
      run all tests for this check or phase
      <#> may be a number (7) or a range (1-6)

  run phase <#> check <#>
      use this form if phase or check alone would be ambiguous

  run suite <name>
      run the given suite of tests

"""
