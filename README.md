# Minecraft Connection Tools
A python implementation for interacting with Minecraft servers.

# Introduction

mctools allows you to interact with Minecraft servers via [rcon](https://wiki.vg/RCON), 
[query](https://wiki.vg/Query), and [server list ping protocol](https://wiki.vg/Server_List_Ping).

This allows you to the following:

 - Send and receive Minecraft server commands
 - Get player count(max and currently playing)
 - Get server version
 - Get the message of the day
 - Get currently installed plugins
 - And much more!
 
All of this can be achieved using simple, intuitive calls to mctools. mctools does all the heavy lifting for you!

# Example

Send a command to the Minecraft server via rcon:

    from mctools import RCONClient  # Import the RCONClient

    HOST = 'mc.server.net'  # Hostname of the Minecraft server
    PORT = 1234  # Port number of the RCON server

    # Create the RCONClient:

    rcon = RCONClient(HOST, port=PORT)

    # Login to RCON:

    if rcon.login("password"):

        # Send command to RCON - broadcast message to all players:

        resp = rcon.command("broadcast Hello RCON!")
 
 # Instillation
 
 You can install mctools via pip:
 
    $ pip install mctools
    
 For more information on installing mctools, check out the instillation section in our documentation{LINK HERE!]
 
 # Formatting
 
 mctools has support for handling Minecraft formatting codes. 
 You can decide weather mctools replaces formatting charcters with intended values, removes them, or leaves them be.
 
 For example, lets say you received the following content during a rcon session:
 
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
    
 As you can see, this text is somewhat hard to read. If you told mctools to remove the formatting characters, 
 then the output will look like this:
 
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
 
 Much easier to read and process. mctools handles this operation automatically, so you don't have to.
 mctools also handels situations where content is sent in ChatObject notation, and can extract messages from the 
 player sample list.
 
 To learn more about formatters, and how to create your own, then please check out the formatting documentation[LINK HERE!].
 
 # Command line tool
 
 mctools is shipped with a CLI front end called mcli.py, which you can use to start rcon sessions, get stats
 via query/ping, check if a Minecraft server is up, ect. 
 
 After installing mctools(through pip or some other method), you can invoke mcli.py like so:
 
    $ mcli.py --help
    
 This will generate the help menu for mcli.py. To learn more about mcli.py, please check out the documentation{LINK HERE!]
 
 # Documentation
 
 mctools has an extensive documentation. It contains tutorials, the API reference, and best practice recommendations.
 You can find the documentation here[LINK HERE!].
 
 # Conclusion
 
 mctools offers a pythonic, reliable way to interact with Minecraft servers, without being too complicated.
 If you have any questions or issues, then please open an issue. Pull requests of any kind a welcome and encouraged!
 
 Thank you for reading!