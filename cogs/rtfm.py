import warnings

import discord
import ext.rtfm_utils as rtfm
from discord.ext import commands


class RTFM(commands.Cog):
    """Commands related to searching documentations"""

    def __init__(self, bot):
        self.bot = bot
        self.targets = {
            "python": "https://docs.python.org/3",
            "pycord": "https://pycord.readthedocs.io/en/latest",
            "master": "https://pycord.readthedocs.io/en/master",
        }
        self.aliases = {
            ("py", "py3", "python3", "python"): "python",
            ("pycord", "pyc", "py-cord"): "pycord",
            ("master", "pycord-master", "pyc-master", "py-cord-master"): "master",
            # too many aliases? idk pls change this before using
        }
        self.cache = {}

    @property
    def session(self):
        return self.bot.session

    async def build(self, target) -> None:
        url = self.targets[target]
        req = await self.session.get(url + "/objects.inv")
        if req.status != 200:
            warnings.warn(
                Warning(
                    f"Received response with status code {req.status} when trying to build RTFM cache for {target} through {url}/objects.inv"
                )
            )
            raise commands.CommandError("Failed to build RTFM cache")
        self.cache[target] = rtfm.SphinxObjectFileReader(
            await req.read()
        ).parse_object_inv(url)

    @commands.command()
    async def rtfm(self, ctx, docs: str, *, term: str = None):
        """
        Returns the top 10 best matches of documentation links for searching the given term in the given docs
        Returns the entire documentation link if no term given
        """
        docs = docs.lower()
        target = None
        for aliases, target_name in self.aliases.items():
            if docs in aliases:
                target = target_name

        if not target:
            lis = "\n".join(
                [f"{index}. {value}" for index, value in list(self.targets.keys())]
            )
            return await ctx.reply(
                embed=ctx.error(
                    title="Invalid Documentation",
                    description=f"Documentation {docs} is invalid. Must be one of \n{lis}",
                )
            )
        if not term:
            return await ctx.reply(self.targets[target])

        cache = self.cache.get(target)
        if not cache:
            await ctx.trigger_typing()
            await self.build(target)
            cache = self.cache.get(target)

        results = rtfm.finder(
            term, list(cache.items()), key=lambda x: x[0], lazy=False
        )[:10]

        if not results:
            return await ctx.reply(
                f"No results found when searching for {term} in {docs}"
            )

        await ctx.reply(
            embed=discord.Embed(
                title=f"Best matches for {term} in {docs}",
                description="\n".join([f"[`{key}`]({url})" for key, url in results]),
                color=discord.Color.dark_theme(),
            )
        )


def setup(bot):
    bot.add_cog(RTFM(bot))
