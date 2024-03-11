# Minecraft Connection Tools
A python implementation for interacting with Minecraft servers.

[![Documentation Status](https://readthedocs.org/projects/mctools/badge/?version=latest)](https://mctools.readthedocs.io/en/latest/?badge=latest)

# Introduction

mctools allows you to interact with Minecraft servers via [rcon](https://wiki.vg/RCON), 
[query](https://wiki.vg/Query), and [server list ping protocol](https://wiki.vg/Server_List_Ping).

This allows you to do the following:

- Send and receive Minecraft server commands
- Get player count(max and currently playing)
- Get server version
- Get the message of the day
- Get currently installed plugins
- And much more!

All of this can be achieved using simple, intuitive calls to mctools. mctools does all the heavy lifting for you!
Also, mctools has no external dependencies(Unless you are a windows user and need color support),
and only uses the python standard library. Just download and go!

# Example

Send a command to the Minecraft server via rcon:

```python
from mctools import RCONClient  # Import the RCONClient

HOST = 'mc.server.net'  # Hostname of the Minecraft server
PORT = 1234  # Port number of the RCON server

# Create the RCONClient:

rcon = RCONClient(HOST, port=PORT)

# Login to RCON:

if rcon.login("password"):

   # Send command to RCON - broadcast message to all players:

   resp = rcon.command("broadcast Hello RCON!")
```

# Installation 

You can install mctools via pip:

```bash
$ pip install mctools
```

If you are a windows user and want color support, then install mctools like so:

```bash
$ pip install mctools[color]
```

For more information on installing mctools, check out the instillation section in our 
[documentation](https://mctools.readthedocs.io/en/latest/install.html).

# Formatting

mctools has support for handling Minecraft formatting codes. 
You can decide weather mctools replaces formatting characters with intended values, removes them, or leaves them be.

For example, lets say you received the following content during a rcon session:

```
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
```

As you can see, this text is somewhat hard to read. If you told mctools to remove the formatting characters,
then the output will look like this:

```
--------- Help: Index (1/40) --------------------
Use /help [n] to get page n of help.
Aliases: Lists command aliases
Bukkit: All commands for Bukkit
ClearLag: All commands for ClearLag
Essentials: All commands for Essentials
LuckPerms: All commands for LuckPerms
Minecraft: All commands for Minecraft
Vault: All commands for Vault
WorldEdit: All commands for WorldEdit
```

Much easier to read and process. mctools handles this operation automatically, so you don't have to.
mctools also handles situations where content is sent in ChatObject notation, and can extract messages from the
player sample list.

To learn more about formatters, and how to create your own,
then please check out the [formatting documentation](https://mctools.readthedocs.io/en/latest/format.html).

# MCLI - mctools Command Line Interface

mctools is shipped with a CLI front end called mcli, which you can use to start rcon sessions, get stats
via query/ping, check if a Minecraft server is up, ect.

After installing mctools(through pip or setuptools), you can invoke mcli like so:

```bash
$ mcli --help
```

You can also run mcli.py(which is located in the parent directory) if you downloaded the source code and did not
install via pip/setuptools.

The above command will generate the help menu for mcli. To learn more about mcli, please check out the 
[mcli documentation](https://mctools.readthedocs.io/en/latest/mcli.html).

We supply mcli as an executable built using pyinstaller under releases
for windows systems that don't have python installed.
The exe file provided may be buggy or have some weird quirks,
so it is recommended to invoke mcli via python.

# Documentation

mctools has an extensive documentation. It contains tutorials, the API reference, and best practice recommendations.
You can find the [documentation here](https://mctools.readthedocs.io/).

Be sure to also check out the [mctools PyPi page](https://pypi.org/project/mctools/) for more information.

# Bug Reports

If you encounter a bug or any other event that does not seem normal,
then please open an issue, or email me personally.
I will be sure to get back to you as soon as possible.

Your feedback and reports are appreciated!
Your comments and issues are an excellent way to correct issues with mctools.

# Contributing

Pull requests are welcome and encouraged :) ! If you want to see a feature in mctools, or have found a bug,
a PR will be the quickest way to get your change implemented. 
Feel free to email me or open an issue if you have any problems.

If you are interested in helping in the development of mctools, then send me an email, and we can get talking!
Believe me, there is plenty of work that needs to be done. More help would be greatly appreciated!

# Conclusion

mctools offers a pythonic, reliable way to interact with Minecraft servers, without being too complicated.
Please check the documentation for more information. More features (hopefully) coming soon!

Thank you for reading!
