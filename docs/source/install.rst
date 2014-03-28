Installing
==========

.. |ieng9_python3_path| replace:: ``/software/common/python-3.2/bin/``

Python
------

Yuno uses Python, either 3.x or 2.7. If you need it, use your package manager or `get a copy <http://www.python.org/downloads>`_ and install it somewhere nice.

Not sure if you have Python, or which version? On Linux/OS X, use::

    # Check for any version
    python -V

    # Check for Python 3
    python3 -V

On Windows::

    :: Any version
    python -V

    :: Python 3
    py -3 -V


Yuno
----

.. _install-for-131:

For Rick Ord's 131
..................

It's pre-configured for the starter code. Clone it or extract the (`archive <https://github.com/bulatb/yuno/archive/v0.3.zip>`_ | `tarball <https://github.com/bulatb/yuno/archive/v0.3.tar.gz>`_) next to ``bin/`` and you'll be set.

To clone with Git::

    cd /your/project
    git clone https://github.com/bulatb/yuno.git
    cd yuno
    git checkout v0.3

Your goal is a directory which looks like this::

    your/project/
        .eclipse_turds, .idea_spam, etc/
        bin/
            (.class files)
        src/
            (.java files)
        testcases/
            (we'll get to this)
        yuno/
            (yuno.py, etc)

For other projects
..................

Download Yuno as above and put it anywhere you want. To get it working for your project, open ``settings/config.json`` and set ``test_folder``, ``compiler_invocation``, and ``compiler_classpath`` (if your project uses Java) to whatever is appropriate.

On ieng9
........

Install Yuno :ref:`for 131 <install-for-131>`, but note the default Python version is too old. Python 3.2 is found in |ieng9_python3_path|.

Make it nice
------------

At this point, Yuno can be run with either

::

    ./yuno.py <args>

or

::

    <python executable> yuno.py <args>

A simple ``yuno <args>`` would be much nicer. We'll use a stupid, brute-force alias because it makes things easy, but a symlink, ``%PATH%`` and ``%PATHEXT%``, or whatever you prefer should work as well. (A future version will remove this step. For now... sorry!)

On Linux/OS X::

    alias yuno='/path/to/compatible/python /path/to/yuno/yuno.py'

On Windows::

    :: Replace XX with your Python version - 27 for 2.7, 31 for 3.1, etc.
    doskey yuno=C:\PythonXX\python.exe C:\path\to\yuno\yuno.py $*

To make it permanent:

- On Linux/OS X with Bash, add your command to ``~/.bashrc`` or similar.
- On Windows, make a `special shortcut <http://devblog.point2.com/2010/05/14/setup-persistent-aliases-macros-in-windows-command-prompt-cmd-exe-using-doskey/>`_ for your ``cmd.exe``.

