"""
Formatters to alter response output - makes everything look pretty
"""

# Try to enable colorama support if we have it:

try:

    import colorama

    # Enable colorama:

    colorama.init()

except:

    # No colorama support, continue

    pass

CHAR = '\u00A7'  # Format char
OLD = '\u001b'
MAP = {'0': '\033[0m\033[30m',
       '1': '\033[0m\033[34m',
       '2': '\033[0m\033[32m',
       '3': '\033[0m\033[36m',
       '4': '\033[0m\033[31m',
       '5': '\033[0m\033[36m',
       '6': '\033[0m\033[33m',
       '7': '\033[0m\033[38;5;246m',
       '8': '\033[0m\033[38;5;243m',
       '9': '\033[0m\033[34;1m',
       'a': '\033[0m\033[32;1m',
       'b': '\033[0m\033[36;1m',
       'c': '\033[0m\033[31;1m',
       'd': '\033[0m\033[35;1m',
       'e': '\033[0m\033[33;1m',
       'f': '\033[0m\033[37;1m',
       'l': '\033[1m',
       'k': '\033[5m',
       'm': '\033[9m',
       'n': '\033[4m',
       'o': '\033[3m',
       'r': '\033[0m'}  # Mapping format chars with ASCII values


NAME_MAP = {'black': '0',
            'dark_blue': '1',
            'dark_green': '2',
            'dark_aqua': '3',
            'dark_red': '4',
            'dark_purple': '5',
            'gold': '6',
            'gray': '7',
            'dark_gray': '8',
            'blue': '9',
            'green': 'a',
            'aqua': 'b',
            'red': 'c',
            'light_purple': 'd',
            'yellow': 'e',
            'white': 'f',
            'obfuscated': 'k',
            'bold': 'l',
            'strikethrough': 'm',
            'underlined': 'n',
            'italic': 'o'}

# Added reset value to the front of color codes, as this is normal Java edition operation


class BaseFormatter(object):

    """
    Parent class for formatter implementations.
    """

    @staticmethod
    def format(text):

        """
        Formats text in any way fit.
        Note: This should not remove format chars, that's what remove is for,
        Simply replace them with their required values.

        :param text: Text to be formatted
        :type text: str
        :return: Formatted text
        :rtype: str
        """

        return text

    @staticmethod
    def clean(text):

        """
        Removes format chars, instead of replacing them with actual values.
        Great for if the user does not want/have color support,
        And wants to remove the unneeded format chars.

        :param text: Text to be formatted
        :type text: str
        :return: Formatted text
        :rtype: str
        """

        return text

    @staticmethod
    def get_id():

        """
        Should return an integer representing the formatter ID.
        This is important, as it determines how the formatters are sorted.
        Sorting goes from least - greatest, meaning that formatters with a lower ID get executed first.

        :return: Formatter ID
        :rtype: int
        """

        return 20


class DefaultFormatter(BaseFormatter):

    """
    Formatter with good default operation:
        - format() - Replaces all formatter codes with ascii values
        - clean() - Removes all formatter codes

    This formatter ONLY handles formatting codes and text attributes.
    """

    @staticmethod
    def format(text):

        """
        Replaces all format codes with their intended values
        (Color, text effect, ect).

        :param text: Text to be formatted.
        :type text: str
        :return: Formatted text.
        :rtype: str
        """

        # Iterate through the text until we find the format char:

        index = 0

        while index < len(text) - 1 and type(text) == str:

            # Checking for CHAR at index:

            if text[index] == CHAR:

                # Found a char, getting next value:

                form = text[index + 1]

                # Checking if we need to add a reset value to the front the of the color value,
                # A Minecraft Java edition "Feature"

                # Replacing format char with ASCII value:

                if form in MAP:

                    # Character is a valid format char, format it:

                    text = text.replace(CHAR + form, MAP[form], 1)

                    # Decrementing index, as we removed some stuff:

                    index = index - 1

                    continue

            # Increment index, nothing was found!

            index = index + 1

        # Adding reset char, so we don't mess up output

        text = text + MAP['r']

        return text

    @staticmethod
    def clean(text):

        """
        Removes all format codes. Does not use color/text effects.

        :param text: Text to be formatted.
        :type text: str
        :return: Formatted text.
        :rtype: str
        """

        index = 0

        while index < len(text) - 1 and type(text) == str:

            # Iterate through text until we find a format char:

            if text[index] == CHAR:

                # Found a format char, getting next char:

                form = text[index + 1]

                # Checking if format char is valid:

                if form in MAP:

                    # Yes, format char is valid. Removing all values:

                    text = text.replace(CHAR + form, '')

                    # Decrementing, as we removed some stuff

                    index = index - 1

                    continue

            index = index + 1

        return text

    @staticmethod
    def get_id():

        """
        Returns this formatters ID, which is 10.

        :return: Formatter ID
        :rtype: int
        """

        return 10


class QUERYFormatter(BaseFormatter):

    """
    Formatter for formatting responses from the Query server.
    Will only format certain parts, as servers SHOULD follow a specific implementation for Query.
    """

    @staticmethod
    def format(text):

        """
        Replaces format chars with actual values.

        :param text: Response from Query server(Ideally in dict form).
        :type text: dict
        :return: Formatted content.
        :rtype: dict
        """

        return QUERYFormatter._packet_format(text, 0)

    @staticmethod
    def clean(text):

        """
        Removes format chars from the response.

        :param text: Response from Query server
        :type text: dict
        :return: Formatted content.
        :rtype: dict
        """

        return QUERYFormatter._packet_format(text, 1)

    @staticmethod
    def _packet_format(data, format_type):

        """
        Does all the heavy lifting for formatting packets.
        Will determine if a packet is basic or full stats, and format it accordingly.

        :param data: Data to be formatted
        :type data: dict
        :param format_type: Type of formatting operation
        :type format_type: int
        :return: Formatted data
        :rtype: dict
        """

        # Creating new dictionary so we don't mess up the original:

        data = dict(data)

        # Formatting the message of the day:

        if format_type == 0:

            # Format the content:

            data['motd'] = DefaultFormatter.format(data['motd'])

        if format_type == 1:

            # Clean the content:

            data['motd'] = DefaultFormatter.clean(data['motd'])

        # Checking for player lists:

        if 'players' in data.keys():

            # Players key present, formatting names:

            final = []

            for play in data['players']:

                if format_type == 0:

                    # Format the data:

                    final.append(DefaultFormatter.format(play))

                if format_type == 1:

                    # Clean the data:

                    final.append(DefaultFormatter.clean(play))

            # Overriding original with formatted values

            data['players'] = final

        return data


class PINGFormatter(BaseFormatter):

    """
    Formatter for formatting responses from the server via Server List Ping protocol.
    We only format relevant content, such as description and player names.
    We also use special formatters, such as ChatObjectFormatter, and SampleDescriptionFormatter.
    """

    @staticmethod
    def format(stat_dict):

        """
        Formats a dictionary of stats from the Minecraft server.

        :param stat_dict: Dictionary to format
        :type stat_dict: dict
        :return: Formatted statistics dictionary.
        :rtype: dict
        """

        # Formatting description:

        return PINGFormatter._packet_format(stat_dict, 1)

    @staticmethod
    def clean(stat_dict):

        """
        Cleaned a dictionary of stats from the Minecraft server.

        :param stat_dict: Dictionary to format
        :type stat_dict: dict
        :return: Formatted statistics dictionary.
        :rtype: dict
        """

        # Cleaning description:

        return PINGFormatter._packet_format(stat_dict, 2)

    @staticmethod
    def _packet_format(stat_dict, form):

        """
        Does all the heavy lifting for format operations.
        Will determine if special formatters are necessary, and use them accordingly.

        :param stat_dict: Dictionary of stats
        :type stat_dict: dict
        :param form: Formatting type to use
        :type form: int
        :return: Formatted statistics dictionary
        :rtype: dict
        """

        if 'description' in stat_dict.keys():

            # Formatting description:

            if type(stat_dict['description']) != str:

                # We need to use ChatObject formatter:

                stat_dict['description'] = (ChatObjectFormatter.format(stat_dict['description']) if form == 1 else
                                            ChatObjectFormatter.clean(stat_dict['description']))

            else:

                # Primitive formatting, handle it:

                stat_dict['description'] = (DefaultFormatter.format(stat_dict['description']) if form == 1 else
                                            DefaultFormatter.clean(stat_dict['description']))

        if 'sample' in stat_dict['players'].keys():

            # Organizing names:

            stat_dict['players']['sample'], stat_dict['players']['message'] = SampleDescriptionFormatter.format(
                stat_dict['players']['sample'])

            # Formatting the names:

            final = []

            for name in stat_dict['players']['sample']:

                if form == 1:

                    # Format the content:

                    final.append([DefaultFormatter.format(name['name']), name['id']])

                else:

                    # CLean the content:

                    final.append([DefaultFormatter.clean(name['name']), name['id']])

            stat_dict['players']['sample'] = final

            # Formatting the message:

            stat_dict['players']['message'] = (DefaultFormatter.format(stat_dict['players']['message']) if form == 1
                                               else DefaultFormatter.clean(stat_dict['players']['message']))

        return stat_dict


class ChatObjectFormatter(BaseFormatter):

    """
    A formatter that handles the formatting scheme of ChatObjects.
    This description scheme differs from primitive chat objects, as it doesn't use formatting characters.
    It instead uses a collection of dictionaries to define what colors and attributes should be used.
    """

    @staticmethod
    def format(chat, color=None, attrib=None):

        """
        Formats a description dictionary, and returns the formatted text.
        This gets tricky, as the server could define a variable number of child dicts that have their own
        attributes/extra content.
        So, we must implement some recursion to be able to parse and understand the entire string.

        :param chat: Dictionary to be formatted
        :type chat: dict
        :param color: Parent text color, only used in recursive operations
        :type color: str
        :param attrib: Parent attributes, only used in recursive operations
        :type attrib: str
        :return: Formatted text
        :rtype: str
        """

        # Define some variables for keeping attributes in:

        attrib = attrib if attrib is not None else ''  # Text attributes we should add
        color = color if color is not None else ''  # Color we should make the text
        extra = ''  # Extra text we should add
        text = ''  # Text we should display

        # Iterate over each value:

        for val in chat:

            if val in NAME_MAP:

                # We have a formatting character, check if we want it or not:

                if chat[val]:

                    # We want this character, add it to the attributes:

                    attrib = MAP[NAME_MAP[val]] + attrib

                    continue

                # We don't want this character, remove it if it is present:

                attrib = attrib.replace(MAP[NAME_MAP[val]], '')

                continue

            if val == 'color':

                # Found a valid color:

                color = MAP[NAME_MAP[chat[val]]]

                continue

            if val == 'text':

                # Found our text, add it:

                text = chat[val]

                continue

        # See if their is any extra text to format:

        if 'extra' in chat.keys():

            # Some extra junk we have to process, iterate over it:

            for child in chat['extra']:

                # Send this extra text down with the parent values:

                extra = extra + ChatObjectFormatter.format(child, color=color, attrib=attrib)

        # We have to specify color first, or else our style codes will get lost!
        # This is only a problem on certain platforms.
        # We also send the text through the DefaultFormatter, as some servers send info this way

        return MAP['r'] + color + attrib + DefaultFormatter.format(text) + extra

    @staticmethod
    def clean(text):

        """
        Cleans a description directory, and returns the cleaned text.

        :param text: Dictonary to be formatted
        :type text: dict
        :return: Cleaned text
        :rtype: str
        """

        # Iterate over the values:

        final = text['text']

        if 'extra' in text.keys():

            # Iterate over each value and process it:

            for child in text['extra']:

                final = final + ChatObjectFormatter.clean(child)

        # Clean up the text, just in case

        return DefaultFormatter.clean(final)


class SampleDescriptionFormatter(BaseFormatter):

    """
    Some servers like to put special messages in the 'sample players' field.
    This formatter attempts to handle this, and sort valid players and null players into separate categories.
    """

    NULL_USER = '00000000-0000-0000-0000-000000000000'  # UUID for null users.

    @staticmethod
    def format(text):

        """
        Formats a sample list of users, removing invalid ones and adding them to a message sublist.
        We return the message in the playerlist, and also return valid players.

        :param text: Valid players, Message encoded in the sample list
        :type text: list, str
        :return: Dictionary containing message, and valid users.
        """

        # Iterate over players:

        valid = []
        message = ''

        for player in text:

            # Check if player is invalid:

            if player['id'] == SampleDescriptionFormatter.NULL_USER:

                # Found an invalid user, add it's content to the message.

                message = message + player['name'] + '\n'

                # Removing player from player list:

                text.remove(player)

                continue

            # Valid user, add it to the sample list:

            valid.append(player)

        # Return values

        return valid, message

    @staticmethod
    def clean(text):

        """
        Does the same operation as format. This is okay because we don't change up any values or alter the content,
        we just organise them, and the color formatter will handle it later.

        :param text: Valid players, Message encoded in the sample list
        :type text: list, str
        :return: Dictionary containing message, and valid users.
        """

        return SampleDescriptionFormatter.format(text)


class FormatterCollection:

    """
    A collection of formatters - Allows for formatting text with multiple formatters,
    and determining which formatter is relevant to the text.

    This class offers the following constants:

      - FormatterCollection.QUERY - Used for identifying Query protocol content.
      - FormatterCollection.PING - Used for identifying Server List Ping protocol content.
    """

    QUERY = 'QUERY_PROTOCOL'
    PING = 'PING_PROTOCOL'

    def __init__(self):

        self._form = []  # List of formatters

    def _get_id(self, form):

        """
        Gets the formatter ID, used by sort() for sorting formatters.

        :param form: Formatter.
        :return: Formatter ID.
        """

        return form.get_id()

    def add(self, form, command, ignore=None):

        """
        Adds a formatter, MUST inherit the BaseFormatter class.
        Your formatter must either be instantiated upon adding it, or the 'clean' and 'format'
        methods are static, as FormatterCollection will not attempt to instantiate your object.

        :param form: Formatter to add.
        :param command: Command(s) to register the formatter with. May be a string or list. \
                         Supply an empty string('') to affiliate with every command, \
                         or a list to affiliate with multiple.
        :type command: str, list
        :param ignore: Commands to ignore, formatter will not format them, leave blank to accept everything.
                       May be string or list.
                       Supply 'None' to allow all commands, or a list to affiliate with multiple.
        :type ignore: str, list
        :return: True for success, False for Failure.
        :rtype: bool
        """

        # Checking formatter parent class:

        if not issubclass(form, BaseFormatter):

            # Form is not a subclass

            raise Exception("Invalid Formatter! Must inherit from BaseFormatter!")

        # Checking command type:

        command = self._convert_type(command, 'Command')

        # Checking ignore type:

        ignore = self._convert_type(ignore, 'Ignore')

        # Adding formatter to list

        self._form.append([form, command, ignore])

        # Sorting list of formatters:

        self._form.sort(key=lambda x: x[0].get_id())

        return True

    def _convert_type(self, thing, text):

        """
        Attempts to convert data into a compatible type(list or string).

        :param thing: Thing to convert.
        :param text: Weather it is a command, or ignore.
        :return: Converted type
        """

        if type(thing) not in [str, tuple, list] and thing is not None:

            # Ignore is not a valid type, checking if it is an int so we can convert it:

            if type(thing) == int:

                # Converting int to string

                return str(thing)

            else:

                raise Exception("Invalid {}} Type! Must be str, list, or tuple!".format(text))

        return thing

    def remove(self, form):

        """
        Removes a specified formatter from the list.

        :param form: Formatter to remove
        :type form: BaseFormatter
        :return: True on success, False on failure
        :rtype: bool
        """

        # Attempting to remove formatter:

        try:

            self._form.remove(form)

        except Exception:

            # Formatter not found, returning

            return False

        # Formatter removed!

        return True

    def clear(self):

        """
        Removes all formatters from the list.
        """

        # Clearing list:

        self._form.clear()

        return

    def get(self):

        """
        Returns the list of formatters.
        Can be used to check loaded formatters, or manually edit list.
        Be aware, that manually editing the list means that the formatters may have some unstable operations.

        :return: List of formatters.
        :rtype: list
        """

        return self._form

    def format(self, text, command):

        """
        Runs the text through the format() function of relevant fomatters.
        These formatters will be removing and replacing characters,
        Most likely format chars.

        :param text: Text to be formatted
        :type text: str
        :param command: Command issued - determines which formatters are relevant.
                        You may leave command blank to affiliate with every formatter.
        :type command: str
        :return: Formatted text.
        :rtype: str
        """

        # Iterating through every formatter:

        for form in self._form:

            # Checking if formatter is relevant:

            if self._is_relevant(form, command):

                # Formatter is relevant, formatting text:

                text = form[0].format(text)

        # Return formatted text:

        return text

    def clean(self, text, command):

        """
        Runs the text through the clean() method of every formatter.
        These formatters will remove characters, without replacing them,
        Most likely format chars.
        We only send non-string data to specific formatters.

        :param text: Text to be formatted.
        :type text: str
        :param command: Command issued - determines which formatters are relevant.
                        You may leave command blank to affiliate with every formatter.
        :type command: str
        :return: Formatted text.
        :rtype: str
        """

        # Iterating through every formatter:

        for form in self._form:

            # Checking if formatter is relevant:

            if self._is_relevant(form, command):

                # Formatter is relevant, formatting text:

                text = form[0].clean(text)

        # Return formatted text

        return text

    def _is_relevant(self, form, command):

        """
        Value determining if the the formatter is relevant to the incoming data.
        :param form: List of formatter info.
        :param command: Command issued.
        :return: True if relevant, False if not.
        """

        # Checking ignore values first:

        if (type(form[2]) == str and form[2] == command) or (type(form[2]) in [list, tuple] and command in form[2]):

            # Command is a value we are ignoring

            return False

        # Checking if value is one we are accepting:

        if form[1] == '' or (type(form[1]) == str and form[1] == command) or (type(form[1]) in [list, tuple] and command in form[1]):

            # Command is a command we can handel:

            return True

        return False

    def __len__(self):

        """
        Returns the amount of formatters in the collection.
        :return: Number of formatters in collection.
        """

        return len(self._form)
