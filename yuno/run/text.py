"""Long or hard-to-format messages printed by the `run` module are stored
in this file. They're meant to be static, not templates to be customized by
users.

"""

# ------------------------------------------------------------------------------
#
SUITE_ALREADY_EXISTS = """
Suite {suite_name} already exists. Use --save {suite_name} -o to overwrite."""

# ------------------------------------------------------------------------------
#
BAD_PHASE_OR_CHECK = """\
Arguments to phase/check must be of the form:

  6       (exact match; won't run 6a, 6b, etc)
  6-10    (matches 6, 6a, 6b, 7, 8a, ..., 10z)
  6a-c    (matches 6a, 6b, 6c; short for 6a-6c)
  6b-19a  (matches 6b, 6c, ... 14, 15a, ..., 19, 19a)

Range matching is always greedy, including any checks and lettered subparts not
excluded by the input. Use `yuno run` with a glob for more specifc matching."""

SHELL_GLOB_EXPANSION_WARNING = """
NOTE: Your shell may natively support globs. For compatibility with Windows,
Yuno needs to handle glob expansion on its own. If they're not matching as
expected, try wrapping them in quotes or turning off your glob expander."""