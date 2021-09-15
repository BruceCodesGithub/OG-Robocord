"""
Directly copied and modified from https://github.com/FrostiiWeeb/discord-ext-paginator/
"""

from contextlib import suppress
from typing import List, Union

import discord


class Paginator:
    __slots__ = (
        "_pages",
        "index",
        "current",
        "timeout",
        "ctx",
        "message",
        "compact",
        "_buttons",
    )

    def __init__(
        self,
        *,
        entries: Union[List[discord.Embed], discord.Embed] = None,
        timeout: float = 90.0,
    ):

        self._pages = entries
        self.index = 0
        self.current = 1
        self.timeout = timeout
        self.ctx = None
        self.compact: bool = False
        self.message = None
        if len(self._pages) == 2:
            self.compact = True

        self._buttons = {
            "⏪": "stop",
            "◀️": "plus",
            "▶️": "last",
            "⏩": "first",
            "⏹️": "minus",
        }

        if self.compact is True:
            keys = ("⏩", "⏪")
            for key in keys:
                del self._buttons[key]

    async def start(self, ctx):
        """
        Start the paginator.
        """
        self.ctx = ctx

        await self._paginate()

    async def _paginate(self):
        """
        Start the pagination session.
        """
        with suppress(discord.HTTPException, discord.Forbidden, IndexError):
            self.message = await self.ctx.send(embed=self._pages[0])
        for b in self._buttons:
            await self.message.add_reaction(b)

        def check(reaction, user):
            return str(reaction.emoji) in self._buttons and user == self.ctx.author

        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add", check=check, timeout=self.timeout
                )
                if str(reaction.emoji) == "⏹️":
                    await self.message.delete()
                    break
                if str(reaction.emoji) == "▶️" and self.current != len(self._pages):
                    self.current += 1
                    await self.message.edit(embed=self._pages[self.current - 1])
                if str(reaction.emoji) == "◀️" and self.current > 1:
                    self.current -= 1
                    await self.message.edit(embed=self._pages[self.current - 1])
                if str(reaction.emoji) == "⏩":
                    self.current = len(self._pages)
                    await self.message.edit(embed=self._pages[self.current - 1])
                if str(reaction.emoji) == "⏪":
                    self.current = 1
                    await self.message.edit(embed=self._pages[self.current - 1])

            except Exception as e:
                print(e)  # just for additional info, nothing else
                with suppress(discord.Forbidden, discord.HTTPException):
                    for b in self._buttons:
                        await self.message.remove_reaction(b, self.ctx.bot.user)
