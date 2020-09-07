import re

from mctools.rcon.datatypes import Players

"""
Mixins that add functionality to RCON, such as listing players, executing certain commands, ect.
"""

# Regular expressions used for locating items:

SEED = re.compile("(?<=\[)(.*?)(?=])")
PLAYERS = re.compile('(?<=[:,])(.*?)(?=[,\s\b])')


class BaseMixin(object):

    """
    Basic RCON mixin, all mixin objects will inherit this class.
    """

    def command(self, com, check_auth=True, format_method=None, return_packet=False):

        """
        Dummy command class for mixin usage. Prevents IDE's from generating errors,
        and allows them to autocomplete.

        :rtype: str
        """

        pass


class VanillaMixins(BaseMixin):

    @property
    def seed(self):

        """
        Fetches the current world seed.

        :return: The world seed.
        :rtype: int
        """

        # Extract the seed and return it:

        return int(SEED.match(self.command('seed'))[0])

    @property
    def players(self):

        """
        Fetches and parses the players list.

        :return: Players object
        :rtype: Players
        """

        # Get the response from the server:

        resp = self.command("list")

        # Create and return the players object:

        return Players.fromresponse(resp)

