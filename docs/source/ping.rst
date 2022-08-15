=============
Ping Tutorial
=============

Introduction
============

Welcome to the tutorial for PINGClient!
This section aims to give you a basic understanding on PINGClient usage.

Basic Ping usage
================

mctools gives you the ability to ping
and retrieve basic statistics from a server via the `Server List Ping Interface <https://wiki.vg/Server_List_Ping>`_.
mctools uses a method similar to how the official Minecraft client pings servers.
You can retrieve a lot of useful information, such as ping latency,
server version, message of the day, players connected, ect.

Plus, Server List Ping is built into the protocol, meaning that it is always enabled,
regardless of server configuration.
This gives you a reliable way to get basic server statistics, even if RCON or Query is disabled.

.. warning::

    As of now, PINGClient only supports Minecraft servers that are version 1.7 or greater.


Creating the instance
---------------------

First, you must create a PINGClient instance:

.. code-block:: python

    from mctools import PINGClient

    ping = PINGClient('mc.server.net')

This will create a PINGClient instance with the default configuration.
All of the options can be set as you see fit, but the default configuration is recommended for most users.

Unlike other clients, PINGClient allows you to optionally specify the protocol number to use when communicating.
You can do this like so:

.. code-block:: python

    from mctools import PINGClient

    ping = PINGClient('mc.server.net', proto_num=PROTOCOL_NUMBER)

This allows PINGClient to emulate certain versions of the Minecraft client. By default, we use protocol number 0,
which means we are inquiring on which protocol version we should use.
You can find a list of protocol numbers and their versions `here <https://wiki.vg/Protocol_version_numbers>`_.

.. note::

    For more information on general client configuration and instantiation, see the :ref:`client tutorial. <client_tutorial>`

Pinging the server
------------------

.. warning::

    The server will automatically close the connection after you ping the server or fetch statistics.

    If you are running mctools version 1.2.0 or above,
    the PINGClient will be automatically stopped for you after each operation.
    The PINGClient can then be started again and used as expected.

    However, older versions of mctools do not support client restarting,
    and you will have to create a new PINGClient instance.

Once you have created your PINGClient, you can ping the server:

.. code-block:: python

    elapsed = ping.ping()

This will return the latency for the ping in milliseconds.
You can use this to determine if a server is receiving connections.

Retrieving Statistics
---------------------

You can also receive statistics from the server:

.. code-block:: python

    stats = ping.get_stats()

This will fetch ping stats, and put it into a dictionary.
The contents of the dictionary *should* be in the following format:

.. code-block:: python

    {'description':
        {'text': 'Now we got business!'},
    'players':
        {'max': 20,
        'online': 1,
        'sample': [
            {'id': 'fbf11fd0-5b74-490c-adc4-91febe9de2ae',
            'name': 'MinecraftPlayer'}],
           'message': ''},
    'time': 0.09879999993245292,
    'version': {
        'name': '1.15.2',
        'protocol': 578},
    'favicon': 'data:image/png;base64,<data>'}

The *description* field is the message of the day.

The *players* field gives some information about connected players.
It tells us the maximum amount of players allowed on the server at once(*max*),
as well as how many players are currently connected(*online*).
It also supplies a sample list of players who are online(*sample*).
Some very large scale servers might not offer a sample list of connected players, and simply leave it blank.

The *message* field contains the message embedded in the player sample list. If you have formatting enabled, PINGClient
will automatically separate the message and the valid players. We touch on this more later in the document.

The *time* field is the latency in milliseconds.

The *version* field gives some information about the server version.
The *name* field usually contains the server version, and this can differ if
the server is using a different implementation(Such as `PaperMC <https://papermc.io/>`_,
`Spigot <https://www.spigotmc.org/>`_, or `Bukkit <https://dev.bukkit.org/>`_).
The *protocol* is the protocol number the server is using.

The *favicon* field is a `PNG <http://en.wikipedia.org/wiki/Portable_Network_Graphics>`_ image
encoded in `Base64 <http://en.wikipedia.org/wiki/Base64>`_. This field is optional, and may not be present.

Note on Packet Format
---------------------

For most cases, the information received will match the example above,
and each field will contain the expected values that they *should* contain.

However, some servers take it upon themselves to embed messages into the player sample list,
or give the description in `ChatObject <https://wiki.vg/Chat>`_ notation. If you have formatting enabled,
then these cases are automatically handled for you.

You can read more about the ping formatters and how they handle data in the `Formatting tutorial <format.html>`_.

Stopping the instance
---------------------

As of mctools version 1.2.0, 
the PINGClient is automatically stopped for you after each operation.

Still, it is recommended to stop the client anyway when it is done being used:

.. code-block:: python

    ping.stop()

This will stop the underlying TCP connection to the Minecraft server, if their still is a connection.
Again, most of the time it is not necessary to stop the client as it is done for you.
You should still do so, as it can ensure that the client is stopped in case it did not automatically stop itself.
It also helps readability, and allows you to explicitly state when you are done communicating over a network.

Conclusion
==========

That concludes the tutorial for PINGClient!