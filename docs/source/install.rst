============
Installation
============

Introduction
============

This section of the documentation shows how to install mctools. We will cover multiple instillation options here,
such as installing via pip and getting the source code.

Python
======

Before you install mctools, you must first have python and pip installed. We will walk through the process of
achieving this. We recommend installing python 3.7, but any python 3 version should work. mctools is NOT
backwards comparable with python 2.

More information on installing/configuring python can be found `here <https://www.python.org/downloads/>`_

Linux
-----

You can install python using your system's package manager.
Below, we will install python 3.7 and pip using apt, the Debian package manager:

.. code-block:: bash

    $ apt install python3.7 python3-pip

It is important to specify that we want the python 3 version of pip, or else it will not work correctly.

Windows
-------

Windows users can download python `here <https://www.python.org/downloads/>`_.
The instillation is pretty straightforward, although we recommend adding python to your PATH environment
variable, as it makes using python much easier.

Mac
---

You can find instillation instructions `here <https://docs.python-guide.org/starting/install3/osx/>`_.

Instillation via PIP
====================

You can install mctools using PIP like so:

.. code-block:: bash

    $ pip install mctools

You can optionally install mctools with extra color support:

.. code-block:: bash

    $ pip install mctools[color]

Reasons on why you should install with color support are outlined in the `Formatting Tutorial <format.html>`_.
Color support is only relevant for Windows installations.

To learn more about PIP and installing in general, check out the
`Tutorial on installing packages <https://packaging.python.org/tutorials/installing-packages/>`_.

Source Code
===========

You can acquire the source code from github like so:

.. code-block:: bash

    $ git clone https://github.com/Owen-Cochell/mctools

This will download the source code to your computer. You can directly reference the package from your application,
or install it using pip:

.. code-block:: bash

    $ cd mctools  # Move to the directory
    $ pip install .

You can also get the tarball from github, which you can download like so:

.. code-block:: bash

    $ CURL -ol https://github.com/Owen-Cochell/mctools/tarball/master