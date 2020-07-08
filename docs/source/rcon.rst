=============
RCON Tutorial
=============

Introduction
============

Welcome to the tutorial for RCONClient!
This section aims to give you a basic understanding of RCONClient usage.

Basic RCON Usage
================

mctools gives you the ability to interact with a server via RCON.
The `Minecraft RCON protocol <https://wiki.vg/RCON>`_ allows admins to remotely execute Minecraft commands.
The Minecraft RCON protocol is an implementation of the
`Source RCON protocol <https://developer.valvesoftware.com/wiki/Source_RCON_Protocol>`_.

.. note::

    While the RCON protocol is a common standard,
    we do not recommend using RCONClient for anything other than Minecraft.
    There has been no testing done on other RCON implementations.

Creating The Instance
---------------------

First, you must create a RCONClient instance:

.. code-block:: python

    from mctools import RCONClient

    rcon = RCONClient('mc.server.net')

This will create a RCONClient instance with the default configuration.
All of the options can be set as you see fit, but the default configuration is recommended for most users.
RCON can only be used if the server has
`RCON functionality enabled. <https://minecraft.gamepedia.com/Server.properties>`_

.. note::

    For more information on general client configuration and instantiation, see the `client tutorial. <client.html>`_

Authenticating with the RCON server
-----------------------------------

Before you can start sending commands, you must first authenticate like so:

.. code-block:: python

    success = rcon.login('password')

Where 'password' is the password used to authenticate.

The function will return True for success, and False for failure.
Most servers will require you to specify a password before you can send commands.

.. note::

    By default, RCONClient will raise an exception if you attempt to send commands when not authenticated.
    You can read about disabling this feature below, but be aware that sending commands while not authenticated can
    lead to unstable operation.

If you have failed to authenticate, you may try again. mctools will allow you to attempt to authenticate as many times
as you need, but the RCON server may have security features in place to block repeated login attempts.

If you have successfully authenticated, you can now start sending commands to the RCON server.

You can check if you are authenticated like so:

.. code-block:: python

    auth = rcon.is_authenticated()

This function will return True if you are authenticated, False if not.

Interacting with the RCON server
--------------------------------

You may now send Minecraft commands to the server like so:

.. code-block:: python

    response = rcon.command("command")

Where 'command' is the command you wish to send to the RCON server.
The function will return the response in string format from the server, formatted appropriately.

.. note::

    You can disable the authentication check by passing 'no_auth=True' to the command function, which will disable
    the check for this command. Again, be aware that this can lead to unstable operation.

For example, if you wanted to broadcast 'Hello RCON!' to every player on the server,
you would issue the following:

.. code-block:: python

    response = rcon.command("broadcast Hello RCON!")

The command sent will broadcast "Hello RCON!" to every player on the server.

.. note::

    Sometimes, the server will respond with an empty string. Some commands have no output, or return an empty string
    when issued over RCON, so this is usually a normal operation. It can also mean that the server doesn't understand
    the command issued.

Ending the session
------------------

To end the session with the server correctly, do the following:

.. code-block:: python

    rcon.stop()

This will stop the underlying TCP connection to the server.
It is ALWAYS recommended to stop the instance, as not doing so could cause problems server-side.

.. note::

    Once a RCONClient instance is stopped, it can't be reused/restarted. This is because of the design of
    Python socket objects. You must create a new RCONClient to interact with the RCON server.

Conclusion
==========

And that concludes the basic usage for RCONClient!

