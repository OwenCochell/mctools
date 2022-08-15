.. _client_tutorial:

===============
Client Tutorial
===============

Introduction
============

This tutorial will give you insight and examples into common client features.
This is a general guide on client functionality. If you need specific information on a topic,
like interacting with a server via RCON, see the specific tutorial for that topic.

Now, all clients inherit from the BaseClient interface.
It defines features and usage present in all clients, regardless of operation.
The default configuration for clients are recommended for most users, as it will do the following:


    1. Generate a request ID based on system time
    2. Automatically replace format codes with appropriate ASCII values
    3. Set socket timeout to 60 seconds


However, advanced users may find tweaking these features to be helpful.

.. note::

    In all following examples, we assume that a client is properly imported,
    and has been instantiated under the name 'client'

Client Methods
==============

All clients have the following methods:

    1. is_connected()
    2. start()
    3. stop()
    4. raw_send()
    5. get_formatter()

is_connected
------------

You can use this method to determine if a client is connected:

.. code-block:: python

    value = client.is_connected()

This method returns a boolean, where True means we are connected, and False means we are not.
'Connected' simply means that we have established a TCP stream with the server
(Or started communicating in the case of UDP), and we are ready to send/receive information.

.. note::

    Just because we are connected doesn't mean we are authenticated! In the case of RCON,
    you must authenticate first before sending commands.

start
-----

You can use this method to start the client, and any underlying protocol objects:

.. code-block:: python

    client.start()

This will, again, start the underlying protocol object, meaning that if we are communicating over TCP,
a TCP stream will be established.

start() is called automatically where appropriate, so you will not have to start the object yourself.

stop
----

You can use this function to stop the client, and close any underlying protocol objects:

.. code-block:: python

    client.stop()

It is HIGHLY recommended to call this when you are done communicating with the server.
Not doing so could cause problems server side. Protocol objects will attempt to gracefully close the
connection when they are deleted, but this does not always work.

You can stop the client multiple times without any issues,
and stopping a client that is already stopped will have no effect.

.. note::

    As of mctools version 1.2.0, client objects can be started again after they have been stopped.

    However, in older versions of mctools, clients can not be started again after they have been stopped.
    This means that if you stop a client, it will be completely unusable.
    This is due to the design of python sockets, as sockets can't be re-used if closed.
    In this case, you will have to create a new client if you stop your current one.

raw_send
--------

.. warning::

    It is recommended to use the high-level wrappers, as sending your own content could mess up the client instance!

This function gives you the ability to bypass the higher-level client wrappers and send your own information:

.. code-block:: python

    client.raw_send(*args)

The usage of this command differs from client to client. See the documentation for specific client usage.

get_formatters
--------------

This function gives you access to the underlying Formatters instance:

.. code-block:: python

    format = client.get_formatter()

This returns the FormatterCollection instance in use by the client,
which will allow you to fine tune the formatter to your use.

More information can be found in the `Formatter Tutorial. <format.html>`_.

Instantiating Clients
=====================

All clients have the same parameters when instantiating:

.. py:class:: Client(host, port=[Port Num], reqid=None, format_method='replace', timeout=60)

    A client implementation. All clients share this format.

    :param host: Hostname of the server
    :param port: Port number of the server
    :param reqid: Request ID to use
    :param format_method: Format method to use
    :param timeout: Timeout for socket operations

We can use these parameters to change the operation of clients.

host
----

The host of the server we are connecting to, this should be a string.

port
----

The port number of the server we are connecting to, this should be a integer.
The default port number differs from client to client.

reqid
-----

.. warning::

    Specifying your own request ID is not recommended!
    Doing so could lead to unstable operation.

The request ID is what we use to identify ourselves to a server.
By default, the client generates a request ID based on system time,
this occurs when the value for 'reqid' is None.

You may specify your own request ID by passing an integer to the 'reqid' parameter.

format_method
-------------

This parameter specifies how (or how not) packets should be formatted.
Minecraft has a special formatting convention that allows users to add custom
colors or effects to text. Info on that can be found `here <https://minecraft.gamepedia.com/Formatting_codes>`_.

Sometimes, often with the use of extensive plugins,
there can be many format characters within the received data,
which can make it difficult to read the content.
Clients provide formatting methods to make this content more human-readable.

Clients support the following format methods,
and use the following constants to identify them:


    1. client.REPLACE - Replace all format characters with their appropriate ASCII values
    2. client.REMOVE - Remove all format characters
    3. client.RAW - Do not format the content

For example, if you wanted to remove format characters,
you would instantiate the client like so:

.. code-block:: python

    client = Client('example.host', 12345, format_method=Client.REMOVE)

This will configure the client to remove all format characters.
This logic applies to the other format options.
The default operation is to replace format characters.

You can also specify the formatting operation on a per-call basis.

For example, let's say you are communicating via RCON,
and want to remove the formatting characters from the 'help' command, instead of replace them.
You would call the 'command' function like so:

.. code-block:: python

    resp = rcon.command('help', format_method=Client.REMOVE)

Every client method where 'formattable' information is fetched has a
'format_method' parameter that you can use to set a 'one time' formatting mode.
If not specified, then the global formatting type will be used.

For more information on formatters, please see the :ref:`Formatter Tutorial. <formatter_tutorial>`

timeout
-------

This parameter specifies the timeout length for socket operations.
It is 60 seconds by default, but can be however long/short you want it to be.
The value MUST be an integer. We don't recommend setting this value too high
or too low.

You can change the timeout at any time using the 'set_timeout' method.
Here is an example of this in action:

.. code-block:: python

    client.set_timeout(120)

In this example, we have set the socket timeout to 120 seconds. All clients have the 'set_timeout'
method.

Packets
=======

By default, clients only return the most relevant parts of a package, usually a payload.
However, some users might want to work with the packages directly.
All client methods that return server information/statistics can return the raw packets instead of the payloads.
This can be done by setting the 'return_pack' argument to 'True'.

Here is an example of this using the PINGClient:

.. code-block:: python

    pack = ping.get_stats(return_pack=True)

Context Managers
================

All clients have context manager support:

.. code-block:: python

    with client as Client('example.host', port=12345):

        client.do_something()
        client.do_another_thing()

When the 'with' block is exited (or an exception occurs),
then the stop() method will automatically be called.
This ensures that the client always gracefully stops the connection.

Exceptions
==========

Each client has their own set of exceptions that are raised when necessary.
However, individual clients do not raise exceptions when network issues occur,
which is where 'ProtocolErrors' come in.

A 'ProtocolError' is an exception raised by the underlying protocol object that
each client uses. This means that it does not matter which client you are using,
if a network issue occurs, then a 'ProtocolError' will be raised.  

List of 'ProtocolErrors':

    1. ProtocolError - Base exception for all protocol errors
    2. ProtoConnectionClosed - Raised when the connection is closed by the remote host

Here is an example of importing and handling these exceptions:

.. code-block:: python

    from mctools.errors import ProtoConnectionClosed  # Import the exception we wish to handle

    with client as Client('example.host', port=1234):

        try:

            client.do_something()

        except ProtoConnectionClosed:

            # Exception has been handled, and the client has been stopped:

            print("Remote host closed connection!")

Conclusion
==========

That concludes our tutorial for client usage!

The tutorials on other topics, such as RCON,
will focus on topic specific usage,
and will skip generic client features.