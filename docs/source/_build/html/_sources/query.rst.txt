==============
Query Tutorial
==============

Introduction
============

Welcome to the tutorial for QUERYClient!
This section aims to give you a basic understanding on QUERYClient usage.

Basic Query Usage
=================

mctools gives you the ability to retrieve server statistics via the
`Minecraft Query protocol <https://wiki.vg/Query>`_.
The Minecraft Query protocol is an implementation of the
`Gamespy Query protocol <http://wiki.unrealadmin.org/UT3_query_protocol>`_.

.. note::

    While the Minecraft Query protocol was made to be compatible
    with the Gamespy Query protocol, we don't recommend using QUERYClient
    for anything other than Minecraft. No testing has been done on
    other Query implementations.

Creating the Instance
---------------------

First, you must create a QUERYClient instance:

.. code-block:: python

    from mctools import QUERYClient

    query = QUERYClient('mc.server.net')

This will create a QUERYClient instance with the default configuration.
All of the options can be set as you see fit, but the default configuration is recommended for most users.
Query can only be used if the server has
`Query functionality enabled <https://minecraft.gamepedia.com/Server.properties>`_.

.. note::

    For more information on general client configuration and instantiation, see the `client tutorial. <client.html>`_

Retrieving Statistics
---------------------

Their are two types of information you can retrieve from a server:
basic stats and full stats.
Basic stats show host IP, port number, message of the day, ect. This is fine for most uses.
Full stats shows more information about the server, such as players connected,
plugins installed, ect.
We will walk through the process of retrieving both.

Basic statistics
----------------

You can retrieve basic stats like so:

.. code-block:: python

    stats = query.get_basic_stats()

This will fetch basic server statistics and put it into a dictionary.
The dictionary has the following format:

.. code-block:: python

    {'gametype': 'SMP',
    'hostip': '127.0.0.1',
    'hostport': '25565',
    'map': 'world',
    'maxplayers': '20',
    'motd': 'Now we got business!',
    'numplayers': '1'}

The *gametype* field is is hardcoded to 'SMP'.

The *hostip* field is the host IP of the server.

The *hostport* field is the hostip of the server.

The *map* field is the name of the current map.

The *maxplayers* field is the maximum number of players.

The *motd* field is the message of the day.

The *numplayers* are the players connected to the server.

Full statistics
---------------

If you want to retrieve the full stats, you may do the following:

.. code-block:: python

    stats = query.get_full_stats()

This will fetch full server statistics and put it into a dictionary.
The dictionary should have the following format:

.. code-block:: python

    {'game_id': 'MINECRAFT',
    'gametype': 'SMP',
    'hostip': '127.0.0.1',
    'hostport': '25565',
    'map': 'world',
    'maxplayers': '20',
    'motd': 'Now we got business!',
    'numplayers': '1',
    'players': ['MinecraftPlayer'],
    'plugins': '',
    'version': '1.15.2'}

The *game_id* field is hardcoded to 'MINECRAFT'.

The *gametype* field is hardcoded to 'SMP'.

The *hostip* field is the host IP of the server.

The *hostport* field is the port number of the server.

The *map* field is the name of current map.

The *maxplayers* field is the maximum amount of players allowed on the server.

The *motd* is the message of the day.

The *numplayers* are the number of players currently connected.

The *players* is a list containing the user names of all connected players.

The *plugins* filed contains a list of plugins used.
This is not used by the vanilla server, however community servers
such as Bukkit and Spigot use this value. Most servers follow this format:

.. code-block:: python

    [SERVER_MOD_NAME[: PLUGIN_NAME(; PLUGIN_NAME...)]]

The *version* field is the version of the server.

Stopping the instance
---------------------

Due to the `UDP protocol's <https://en.wikipedia.org/wiki/User_Datagram_Protocol>`_ design(The protocol Query uses),
the client instance does not *need* to be stopped.
However, we still recommend stopping your client for readability, and so you can be explict as to when your
program will stop communicating over the network.

Conclusion
==========

That concludes the tutorial on QUERYClient usage!
