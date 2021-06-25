import collections
import re

from discord.ext import commands

time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(
                    "{} is an invalid time-key! h/m/s/d are valid!".format(k)
                )
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class TelephoneConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isnum() and not len(argument) == 10:
            raise commands.BadArgument(
                "{} is not a valid phone number".format(argument)
            )
        return int(argument)


Codeblock = collections.namedtuple("Codeblock", "language content")


class CodeblockConverter(commands.Converter):
    async def convert(self, ctx, argument):
        """
        A converter that strips codeblock markdown if it exists.
        Returns a namedtuple of (language, content).
        :attr:`Codeblock.language` is an empty string if no language was given with this codeblock.
        It is ``None`` if the input was not a complete codeblock.
        """
        if not argument.startswith("`"):
            return Codeblock(None, argument)

        # keep a small buffer of the last chars we've seen
        last = collections.deque(maxlen=3)
        backticks = 0
        in_language = False
        in_code = False
        language = []
        code = []

        for char in argument:
            if char == "`" and not in_code and not in_language:
                backticks += 1  # to help keep track of closing backticks
            if (
                last
                and last[-1] == "`"
                and char != "`"
                or in_code
                and "".join(last) != "`" * backticks
            ):
                in_code = True
                code.append(char)
            if char == "\n":  # \n delimits language and code
                in_language = False
                in_code = True
            # we're not seeing a newline yet but we also passed the opening ```
            elif "".join(last) == "`" * 3 and char != "`":
                in_language = True
                language.append(char)
            elif (
                in_language
            ):  # we're in the language after the first non-backtick character
                if char != "\n":
                    language.append(char)

            last.append(char)

        if not code and not language:
            code[:] = last

        return Codeblock("".join(language), "".join(code[len(language) : -backticks]))
