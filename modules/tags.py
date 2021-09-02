import discord
from discord.ext import commands
from cogs.database import Database


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(self.bot)

    @commands.group(invoke_without_command)
    async def tag(self, name):
        await self.db.show(name)

    @tag.command()
    async def create(self, name, value):
        await self.db.new(name, value)


def setup(bot):
    bot.add_cog(Tags(bot))
