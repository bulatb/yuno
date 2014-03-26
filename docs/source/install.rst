Download and install
====================

Python check
------------

Yuno requires Python 2.7.x (not 2.6 or 3.x). It's a long, sad, highly fragmented story. If you don't already have it, or you have a different version, you should `get a copy <http://www.python.org/download/releases/2.7/>`_ and install it somewhere nice. You can check your default Python install's version like this: ``$ python --version``. ProTip: for ieng6 users, Python 2.7 lives in ``/software/common/python-2.7/bin/python2.7``.

If you have multiple Python installs and don't want to fiddle with shebangs, it might be good to make an alias for the runtime you want::

    # Just one of many ways to do this
    $ alias yuno="/path/to/python2.7 yuno.py"

The framework
-------------

If you're using Git, just::

    $ cd /your/project
    $ git clone https://github.com/bulatb/yuno.git

If not, download the `project zip <https://github.com/bulatb/yuno/archive/master.zip>`_ and extract it wherever you want.

**Note**: For a hassle-free install that works out of the box, your folder structure should look like this::

    /your/project/ (anywhere)
        .eclipsecrap, etc/
        bin/
            (.class files)
        testcases/
            (test repo; see below)
        yuno/
            (yuno.py, etc)

CSE 131: the test repo
----------------------

Historically it's been a good idea to maintain a central, class-wide test repo for everyone to share their tests. Someone usually steps up to manage it and make sure everything stays good. To get yourself a working copy, or just see the folder structure it should have, see the `GitHub project here <https://github.com/bulatb/compilers-testcases>`_.

If your care cup is `especially empty <http://pinterest.com/pin/135178426287092414/>`_, clone that repo next to Yuno and skip down down to the manual.

::

    $ cd /your/project
    $ git clone https://github.com/bulatb/compilers-testcases.git

