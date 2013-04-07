usage = """yuno.py run all
  or   yuno.py run <glob>
  or   yuno.py run phase <#> check <#>
  or   yuno.py run phase <#>
  or   yuno.py run check <#>
  or   yuno.py run suite <name>

note:
  all forms support the optional arguments below

details:
  run all
      run every test in the test folder, searching recursively

  run <glob>
      run all tests in folders matching this glob
      Ex: yuno.py run phase1/check[1-3]

  run fail(ed|ing)
      failed: run all tests that failed on the last run
      failing: run all tests that haven't passed since they last failed

  run files <glob>
      run specific files (as opposed to run <glob>, which runs all files in any
      folders matched by <glob>)

  run -
      run a newline-delimited stream of file paths given through a pipe
      Ex: yuno.py run - < some-tests.txt

  run (phase|check) <#>
      run all tests for this check or phase
      <#> may be a number (7) or a range (1-6)

  run phase <#> check <#>
      use this form if phase or check alone would be ambiguous

  run suite <name>
      run the given suite of tests
"""
