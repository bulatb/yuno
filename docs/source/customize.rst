Customizing Yuno
================

Configuration
-------------

The settings you can change are documented and defined in ``settings/config.json``. Yuno comes pre-configured to work with the standard repo layout described above, but you're free to use whatever you prefer. The defaults are saved in ``settings/config.json.default``.

Except for comments (lines starting with ``//``), the config syntax is `standard JSON <http://en.wikipedia.org/wiki/JSON#Data_types.2C_syntax_and_example>`_. Intrepid editors will find that Yuno's comment stripping code is very stupid, so comments at the ends of lines . Complaints may be addressed to:

| ATTN: Roundfile Group
| 127 Wontfix Road
| Dev-null, CA 92122
|

Customizing output
------------------

Most messages that end up at the console (not yet all) are built from plaintext template files whose paths are set in ``failure_message``, ``diff_message``, and so on in the settings file. You can either change the paths or just edit the defaults in-place. What you see is what you get, newlines and all.

