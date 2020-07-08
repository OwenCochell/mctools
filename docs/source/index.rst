Welcome to Minecraft-Connection-Tools documentation!
====================================================

This is the documentation for Minecraft-Connection-Tools(mctools) -
an easy to use python library for querying, interacting, and gathering information on Minecraft servers.

mctools implements the following Minecraft protocols:

    1. RCON
    2. Query
    3. Server List Ping

Here is a brief example of the RCONClient, one of the Minecraft client implementations:

.. code-block:: python

    from mctools import RCONClient  # Import the RCONClient

    HOST = 'mc.server.net'  # Hostname of the Minecraft server
    PORT = 1234  # Port number of the RCON server

    # Create the RCONClient:

    rcon = RCONClient(HOST, port=PORT)

    # Login to RCON:

    if rcon.login("password"):

        # Send command to RCON - broadcast message to all players:

        resp = rcon.command("broadcast Hello RCON!")


We also offer a CLI front end for mctools, called 'mcli.py'. You can read all about it below.

This documentation contains tutorials on basic usage, as well as the API reference. We recommend starting with
the client tutorial, as it gives you a general idea of how clients work.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   client
   rcon
   query
   ping
   format
   mcli
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
