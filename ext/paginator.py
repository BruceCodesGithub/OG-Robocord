"""
Directly copied and modified from https://github.com/FrostiiWeeb/discord-ext-paginator/
"""

import discord
from typing import Union, List
from contextlib import suppress


class Paginator:
    """
    An object for pagination for discord.py.

    _pages: List[discord.Embed] : `The pages of the paginator.`
    index : int : `The index page of the paginator.`
    current : int : The current page of the paginator.
    timeout : float = 90.0 : `The timeout for the paginator.`
    ctx : NoneType : `The context for the paginator.`
    message : NoneType : `The message for the paginator.`
    compact : bool : `If the paginator's pages are less then 3 then compact will take over.
    _buttons : dict : The reactions for the paginator.`

    """

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
            "🔢": "input",
        }

        if self.compact is True:
            keys = ("⏩", "⏪", "🔢")
            for key in keys:
                del self._buttons[key]

    async def go_to_input(self):
        """
        An function for the input.
        """
        try:

            def check(m):
                return m.author == self.ctx.author

            await self.ctx.send("What page do you want to go to?")
            msg = await self.ctx.bot.wait_for(
                "message", timeout=20.0, check=check
            )
            if int(msg.content) > len(self._pages):
                pass
            elif int(msg.content) == len(self._pages):
                self.current = len(self._pages)
                await self.go_to_page(self._pages[self.current - 1])
            else:
                self.current = int(msg.content)
                await self.message.edit(embed=self._pages[self.current - 1])
        except Exception as e:
            print(e)

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
            return (
                str(reaction.emoji) in self._buttons
                and user == self.ctx.author
            )

        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add", check=check, timeout=self.timeout
                )
                if str(reaction.emoji) == "⏹️":
                    await self.message.delete()
                    break
                if str(reaction.emoji) == "▶️" and self.current != len(
                    self._pages
                ):
                    self.current += 1
                    await self.message.edit(
                        embed=self._pages[self.current - 1]
                    )
                if str(reaction.emoji) == "◀️" and self.current > 1:
                    self.current -= 1
                    await self.message.edit(
                        embed=self._pages[self.current - 1]
                    )
                if str(reaction.emoji) == "⏩":
                    self.current = len(self._pages)
                    await self.message.edit(
                        embed=self._pages[self.current - 1]
                    )
                if str(reaction.emoji) == "⏪":
                    self.current = 1
                    await self.message.edit(
                        embed=self._pages[self.current - 1]
                    )
                if str(reaction.emoji) == "🔢":
                    await self.go_to_input()

            except Exception as e:
                with suppress(discord.Forbidden, discord.HTTPException):
                    for b in self._buttons:
                        await self.message.remove_reaction(
                            b, self.ctx.bot.user
                        )
