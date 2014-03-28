Testing remotely
================

Version 0.3 adds two new subcommands: ``compile``, to save assembly files, and ``watch``, to watch a repo for new batches of assembly files and run them when a batch is ready. Together with an SSH mount, these commands allow for writing your compiler locally, invoking Yuno locally, and running tests on a remote machine. For CSE 131, we'll mount ieng9.

The goal: a local path whose contents automatically get synced in both directions with ieng9. Do this any way you want:

* `SSHFS <https://www.digitalocean.com/community/articles/how-to-use-sshfs-to-mount-remote-file-systems-over-ssh>`_ (Linux, OS X)
* `ExpanDrive <http://www.expandrive.com/expandrive>`_ (Windows, OS X)
* `win-sshfs <https://code.google.com/p/win-sshfs/>`_ (Windows)
* inotify + rsync hacks

Then, on ieng9, create :file:`131/` inside your home directory and set it up like this::

    131/
        input.c
        output.s
        testcases/
            (your test repo)
        yuno/
            (yuno installation)

Setup: Windows
--------------

Everything is pre-configured. Mount ieng9 so :file:`Q:\\` maps to :file:`/home/linux.../{you}`.

Setup: Linux/OS X
-----------------

On your machine—not ieng9—edit :file:`yuno/compile/settings/config.json` so the settings match this table. These paths assume you mounted :file:`/home/linux/.../{you}` at :file:`/mnt/ieng9/`.

======================   ===============================
setting                  value
======================   ===============================
data_folder              **/mnt/ieng9/**\ 131/yuno/data
assembly_output_folder   **/mnt/ieng9/**\ 131/testcases
======================   ===============================


Running tests
-------------

ieng9
.....

Once Yuno is installed, run ``yuno watch &`` to create a background process watching your :file:`testcases` folder. When a batch of tests shows up, ``watch`` runs them, saves each one as :file:`{test-name}.s.last` for reference and debugging, and deletes the files it ran.

Your machine
............

Instead of .rc files, ``yuno watch`` treats SPARC assembly files as input. The ``compile`` command will search your local test repository for RC files, generate from them assembly test files, and move the tests into your mounted test repository where ``watch`` picks them up. Arguments and options are the same as ``run``, except ``compile`` ignores ``--diff`` and ``--pause``.

To run phase 1, check 2 on ieng9::

    yuno compile phase 1 check 2

.. note:: This setup means your test repository is divided into RC source files (your machine) and answer files (ieng9). If you want them both in the same place, set ``"test_folder"`` in :file:`yuno/compile/settings/config.json` to your mounted test repository. Since you'll have to read more data via SSH, this option may be noticeably slower.

Getting results
---------------

The ``watch`` you ran will print the normal summary each time it runs a batch. If you'd rather see results on your machine, point ``"data_folder"`` in your local :file:`settings/config.json` at :file:`yuno/data` on ieng9. Then run ``yuno show`` as normal::

    yuno show last
    yuno show failed
    # etc.

