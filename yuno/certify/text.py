UNEXPECTED_PIPE = """
Detected pipe to `certify files`. If you're trying to pipe test cases,
use `certify -`.

Streams piped to `certify files` will be understood as answers for the
prompts, which can damage the test repo if it's not what you intended.
If you just want all your cases certified, try `--yes --overwrite`. If
you really want to drive the program through a pipe, make sure the first
line of your input stream is "pipe" (no quotes, ending in a \\n)."""