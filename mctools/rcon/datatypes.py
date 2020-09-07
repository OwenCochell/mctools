import re

"""
Custom classes that represent certain things, such as players.

THIS IS A WORK IN PROGRESS!
This is not to be used in production!!!
"""

PLAYERS = re.compile('(?<=[:,])(.*?)(?=[,\s\b])')


class Players:

    """
    This class represents online players, how many are online, names, ect.
    We offer methods to iterate over the list of players.

    :param max_players: Maximum number of players allowed on the server
    :type max_players: int
    :param online: Number of players online
    :type online: int
    :param players: Tuple of players currently online
    :type players: tuple
    """

    REGEX = re.compile('(?<=[:,])(.*?)(?=[,\s\b])')  # Regular expression for getting players

    def __init__(self, max_players, online, players):

        self.max = max_players  # Maximum players allowed on the server at once
        self.online = online  # Number of players currently online
        self.players = players  # Tuple of players

    @classmethod
    def fromresponse(cls, resp):

        """
        Creates a Players object using the response fom the 'list' command.
        We utilise regular expressions, as some plugins offer custom player lists.
        This allows us to reliably extract player info, as long as the list follows a certain pattern,
        which most should.

        :param resp: Response from 'list' command.
        :type resp: str
        :return: Players object
        :rtype: Players
        """

        # Get the list of players:

        players = tuple(cls.REGEX.match(resp.replace(' ', '')))

        # Get the numbers:

        nums = resp.split(':')[0]
        max_players, online = [int(n) for n in nums.split() if n.isdigit()]

        # Return the object:

        return Players(max_players, online, players)

    def __len__(self):

        """
        Returns the length of the player list,
        or the number of players online.

        :return: Number of players online
        :rtype: int
        """

        return self.online

    def __getitem__(self, position):

        """
        Gets an item from the player list and returns it.
        Used for adding iteration support.

        :param position: Position of item we wish to get
        :return: Item at position
        """

        return self.players[position]

    def __repr__(self):

        """
        'Official' representation of the object.

        :return: String containing object info
        """

        return "Players({}, {}, {})".format(self.max, self.online, self.players)

    def __str__(self):

        """
        'Informal' representation of the object.
        We only list player online/max players, as listing all of them would be unnecessary.

        :return: String containing object info
        """

        return "{} players online out of {}".format(self.max, self.online)


class Command:

    """
    Represents a single command, and all arguments associated with it.
    """

    def __init__(self, name, args):

        self.name = name  # Name of the command
        self.args = args  # Command arguments

    def parse_args(self, args):

        """
        Parses a string of arguments and converts it into something we can understand
        (Whatever that may be).

        We might have to use recursion, goody!

        Argument notation will go as follows:

            dict - Sublist of options


        :param args: Arguments to parse
        :return:
        """

        # First, we split by name, as vanilla help will offer it on seperate lines:

        nargs = args.split(self.name)

        # lets iterate over each value:

        for path in nargs:

            if len(nargs) > 1:

                # Need a new dictionary for this:

                self.args[path] = {}

            for arg in path.split(' '):

                # Figure out what we are working with:

                pass


class Help:

    """
    Represents a collection of commands.
    We can add, remove, and even attempt to autocomplete commands.
    """

    def __init__(self):

        self.commands = {}  # Dictionary of commands

    def add(self, command):

        """
        Adds a command object to the command dictionary.

        :param command: Command object to add
        :return:
        """


class CommandParser:

    """
    This class handles the parsing and autocompletion
    """

    pass