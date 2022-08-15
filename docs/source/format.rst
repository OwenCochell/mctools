.. _formatter_tutorial:

===================
Formatting Tutorial
===================

Introduction
============

This section aims to give you a basic understanding of formatters and how to use them.

Minecraft servers(vanilla and otherwise) use
`special formatting codes <https://minecraft.gamepedia.com/Formatting_codes>`_ for
adding color and effects to text.
Minecraft uses the '§' character and the value after that to determine
what color/effect the text should have.

For example:

.. code-block:: none

    §4This text will appear red.

When the formatting operation is complete, the text will appear red.

These colors are used in a variety of things,
such as signs, books, player names, command output, ect.
However, these characters can make it difficult to read the content of the message.

For example, take the following help output:

.. code-block:: none

    §e--------- §fHelp: Index (1/40) §e--------------------
    §7Use /help [n] to get page n of help.
    §6Aliases: §fLists command aliases
    §6Bukkit: §fAll commands for Bukkit
    §6ClearLag: §fAll commands for ClearLag
    §6Essentials: §fAll commands for Essentials
    §6LuckPerms: §fAll commands for LuckPerms
    §6Minecraft: §fAll commands for Minecraft
    §6Vault: §fAll commands for Vault
    §6WorldEdit: §fAll commands for WorldEdit

This output is somewhat difficult to read. It would be easier if the formatting chars were replaced
with ASCII color codes so we can see the response in color. It would also be easier if the characters were removed.
mctools provides methods that can handle these formatting characters,
so text can be made more human-readable.

Note on color support
=====================

The mctool's formatters add color and text attributes to text using
`ASCII escape codes <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ and
`Ascii color codes <http://pueblo.sourceforge.net/doc/manual/ansi_color_codes.html>`_.
In most cases, these color codes will be universally compatible, and the terminal in use will handle these codes,
and draw the text with the appropriate colors/attributes.

However, some terminals will NOT support handling of ASCII escape codes, with
`Windows 10 CMD.exe <https://en.wikipedia.org/wiki/Cmd.exe>`_ being one of them. This can lead to output that is either
not colored or difficult to read, as these terminals often
output the characters instead of applying the attributes to the text.

To handle this, mctools offers an optional install dependency which will install the python library
`colorama <https://pypi.org/project/colorama/>`_. colorama will automatically enable ASCII escape code support, which
will allow us to draw text in certain colors.

colorama is automatically enabled if it is installed. If not installed, the formatter will
continue the formatting operation.


Formatter Usage
===============

A 'Formatter' is a class that alters content received from a server.
All formatters must inherit the 'BaseFormatter' class, and must provide the following methods:

    1. format() - Change the makeup of the content(insert/move characters) to make text more readable.
    2. clean() - Remove content to make it more readable

This design was mostly for handling formatting characters,
but a formatter can make any changes to the text as it sees fit.

.. note::

    A formatter can optionally specify a 'get_id()' method that returns an integer.
    This integer is used to determine the order of the formatter. The lower the number, the higher
    it's priority.

For example, lets say that a server is replacing content with an '@' symbol every few characters,
and you want to make a formatter that would handle this oddity.
Your clean() method would simply remove each and every '@' character from the content.
Your format() method, however, would attempt to replace the '@' characters with their intended values.
Again, this is just a recommendation. Both methods can do the same operation
if that's what the situation entails.

mctools has some formatters built in for convenience. The builtins ONLY handle
formatting characters(With the exception of the special formatters). Builtin formatters all use static methods,
meaning that a class does not have to be instantiated to be used.

BaseFormatter
-------------

Parent class that each formatter MUST inherit.
This class also has an ID of 20, meaning that any formatter that hasn't
specified a get_id() method will have an ID of 20.

DefaultFormatter
----------------

DefaultFormatter is the backbone of all built in formatters.
DefaultFormatter handles formatting characters, replacing them with the desired ASCII
color codes, or simply removing them. DefaultFormatter only handles strings, and is used by
the RCONClient, as well as other formatters.

QUERYFormatter
--------------

QUERYFormatter was designed to format a query response in dictionary format,
processing the relevant fields only. It uses DefaultFormatter for replacing/removing format chars, and is used
by QUERYClient.

PINGFormatter
-------------

PINGFormatter is similar to Query, because it only formats relevant fields.

However, PINGFormatter uses two other formatters, ChatObjectFormatter and SampleDescriptionFormatter to handle
some scenarios that may come up during formatting process.

These formatters will do the same operation regardless of weather we are cleaning or formatting, with the exception of
color codes, which will only be included if we are formatting the text.

If you set the format method to RAW, then the special formatters will not be ran, meaning that the makeup of the server
statistics will not be altered.

ChatObjectFormatter
___________________

Some newer servers send description data in `ChatObject notation <https://wiki.vg/Chat>`_, which uses a collection of
dictionaries to format text instead of formatting characters.

Here is an example of a description in ChatObject notation:

.. code-block:: python

    {'description':

        {'extra': [{'bold': True,
                    'color': 'yellow',
                    'text': 'This is bold and yellow!'},

                    {'color': 'gold',
                     'text': ' Just gold. New line!\n'},

                    {'color': 'white',
                     'italics': True,
                     'text': 'We are on a new line, '},

                    {'color': 'green',
                     'text': 'and we love the color green.'},

                    {'color': 'white',
                     'text': '.'}]},

        'text': ''}

As you can see, this makes reading and parsing the content difficult. ChatObjectFormatter fixes this problem
by converting the dictionary into a single string, which makes reading and parsing the data much easier.

SampleDescriptionFormatter
__________________________

Sometimes, servers like to embed descriptions into the sample player list.
Servers usually use a player with a null UUID to show message content, so this formatter attempts to separate
valid players from message content.

Have a look at this example sample player list:

.. code-block:: python

    {'players': {'max': 5000,
             'online': 723,
             'sample': [{'id': '00000000-0000-0000-0000-000000000000',
                         'name': 'We are a server.'},
                        {'id': '00000000-0000-0000-0000-000000000000',
                         'name': ''},
                        {'id': '00000000-0000-0000-0000-000000000000',
                         'name': 'Check out our Twitter!'},
                        {'id': '00000000-0000-0000-0000-000000000000',
                         'name': ''},
                        {'id': '00000000-0000-0000-0000-000000000000',
                         'name': 'We have really great players!'},
                        {'id': '00000000-0000-0000-0000-000000000000',
                         'name': ''},
                        {'id': '00000000-0000-0000-0000-000000000000',
                         'name': 'Here is one of them:'},
                        {'id': '2ef8ad56-ec35-46e7-b90c-8172386d3fe7',
                        'name': 'MinecraftPLayer1'}]}}

If you look, there is a message encoded in this sample list, with one valid player.
The message has a null UUID, which is how SampleDescriptionFormatter determines if a user list is actually
a message.

After the formatting operation is complete, the *player* sub-dictionary will look like this:

.. code-block:: python

    {'players': {'max': 5000,
             'online': 723,
             'sample': [{'id': '2ef8ad56-ec35-46e7-b90c-8172386d3fe7',
                        'name': 'MinecraftPLayer1'}],
             'message': 'We are a server.\n\nCheck out our Twitter!\n\nWe have really great players!\n\nHere is one of them:'}}

Now, the sample only contains valid players, and the message is stored under a separate key named 'message'.
This allows us to accurately determine who is really playing, and view the message with no extra processing.


FormatterCollection class
=========================

'FormatterCollection' is a class that handles a collection of formatters.
It offers an easy to use API for adding/removing formatters, altering text with multiple formatters,
and defining what formatter should be used for specific inputs.

Every client has a FormatterCollection instance that they use to format incoming data(Clients automatically load the
relevant formatters at the start of the instance). However, clients give you the option to work with formatters directly
(This can be done by calling the 'get_formatter()' method of the class).

FormatterCollection offers the following methods to work with:

    1. add(formatter, command, ignore=None, args*, kwargs*) - Add a formatter
    2. remove(formatter) - Remove a formatter
    3. clear() - Remove all formatters
    4. format(text, command) - Formats the given text
    5. clean(text, command) - Cleans the given text
    6. get() - Returns the list of formatters

We will go over each of these methods and their usage.

add
---

The 'add' method adds a formatter to the collection. It has the following parameters:

    1. formatter - Formatter class to add(Must inherit BaseFormatter, or an exception will be raised)
    2. command - Command(s) associated with the formatter
    3. ignore - Command(s) to ignore

.. warning::

    FormatterCollection will NOT instantiate your formatters. This means you must instantiate your formatter BEFORE
    adding it to the collection, or make all of your formatter methods static.

FormatterCollection will only call a formatter that can handle relevant text.
To determine if text is relevant to a formatter, you must supply command(s) to the add method.
The value can be a string containing a single command, or a list containing multiple. You may
also supply a empty string('') to the command parameter to affiliate the formatter to every command
(unless a command is ignored, which we will get to later).

For example, let's say you wanted to create a formatter for RCONClient that only handles output from the
'motd' command. You would add the formatter like this(assume that FormatterCollection is instantiated as
'form').

.. code-block:: python

    form.add(my_formatter, 'motd')

Content will only be sent to this formatter if the command executed was 'motd'. Clients automatically supply
the command executed when formatting content.

Conversely, we have the 'ignore' parameter. Ignore specifies which commands should be ignored by the formatter.
Unlike the command parameter, ignore is optional, and nothing will be ignored if it is not set.
ignore accepts commands in the same format as the command parameter, meaning that you can specify a single command
as a string, or multiple commands as a list.

For example, if you want to add a formatter that accepts all commands except the 'list' command, you can do the
following:

.. code-block:: python

    form.add(my_formatter, '', ignore='list')

FormatterCollection will send all content to the formatter, except content from the 'list' command.

As you can see, the convention for affiliating commands with a formatter is primarily designed for usage with rcon.
However, FormatterCollection also supplies the following constants to help identify formatting operations:

    1. QUERY - Value used by QUERYClient to identify query content to be formatted
    2. PING - Value used by PINGClient to identify ping content to be formatted

You can use these values to affiliate or ignore ping/query content. For example, let's say you want to make a formatter
that handles ping content. You can do the following:

.. code-block:: python

    form.add(my_formatter, form.PING)

This will affiliate the formatter with ping content.

remove
------

Will remove a specified formatter from the collection. You must supply the formatter instance to be removed.
Will return True for success, False for failure.

clear
-----

Will remove all formatters from the collection.

format
------

Will send the given content through the relevant formatters, and format the content. You must supply the command issued with the
'command' parameter. The same logic from above applies here, if you pass '', then it will affiliate the content with ALL
formatters.

clean
-----

Same operation, except the the content is cleaned by relevant formatters instead of formatted.

get
---

.. warning::

    It is not recommended to edit this list yourself! Users should use the higher level methods to
    add or remove formatters.

This will return the list of formatters used by FormatterCollection. The information on a formatter is stored in a
sublist with the following format:

.. code-block::

    [Formatter Instance,
    Commands to match,
    Commands to ignore]

You can edit this list manually, however it is recommended that you use the higher level methods for adding/removing
formatters.

Custom Formatter
================

In this example we will be writing a formatter that will replace the word 'help' with 'assistance'.
If we are cleaning the text, then we will simply remove 'help' from the content.

.. code-block:: python

    from mctools import formattertools

    class HelpFormatter(formattertools.BaseFormatter)
        """
        A Simple formatter to change some wording on the Minecraft help menu.
        """

        @staticmethod
        def format(text):
            """
            Replaces 'help' with assistance.
            """

            return text.replace('help', 'assistance')

        @staticmethod
        def clean(text):
            """
            Removes 'help' from the text.
            """

            return text.remove('help')


We now have a formatter we can use. We must register it with the RCONClient FormatterCollection:

.. code-block:: python

    from mctools import mclient

    rcon = mclient.RCONClient('mc.server.net', 25565)

    form = rcon.get_formatter()

    form.add(HelpFormatter, 'help')

    rcon.start()


The formatter has been registered with the FormatterCollection of the RCONClient, and will format the help menu
accordingly.

Conclusion
==========

You should now have an understanding on the usage of formatters. Most of the time, the built in formatters
will handle the formatting correctly. If this is not the case, then you can create and add your own formatter
to the client.