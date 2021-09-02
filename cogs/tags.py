import discord
from discord.ext import commands
from cogs.database import Database


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(self.bot)

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, name=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        a = await self.db.show(name)
        await ctx.reply(a)

    @tag.command()
    async def create(self, ctx, name=None, *, value=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        if not value:
            return await ctx.reply("Value is a required argument")
        if not name.lower() in [
            "create",
            "edit",
            "delete",
            "make",
            "add",
            "remove",
            "info",
            "transfer",
            "claim",
            "all",
        ]:
            b = await self.db.new(name, value, ctx.author.id)
            await ctx.reply(b)
        else:
            await ctx.reply("That name is reserved")

    @tag.command()
    async def delete(self, ctx, name=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        f = ctx.author.guild_permissions.manage_messages
        b = await self.db.remove(name, ctx.author.id, f)
        await ctx.reply(b)

    @tag.command()
    async def edit(self, ctx, name=None, *, value=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        if not value:
            return await ctx.reply("Value is a required argument")
        b = await self.db.update(name, value, ctx.author.id)
        await ctx.reply(b)

    @tag.command()
    async def info(self, ctx, name=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        b = await self.db.data(name)
        embed = discord.Embed(title=name)
        embed.add_field(name="Id", value=b[0])
        if not b[0] == "nothing found":
            embed.add_field(name="Author", value=f"<@{b[1]}>")
        else:
            embed.add_field(name="Author", value=f"nothing found")
        await ctx.reply(embed=embed)

    @tag.command()
    async def transfer(self, ctx, name=None, member: discord.Member = None):
        if not name:
            return await ctx.reply("Name is a required argument")
        if not member:
            return await ctx.reply("Member is a required argument")
        b = await self.db.transfer(name, ctx.author.id, member.id)
        await ctx.reply(b)


def setup(bot):
    bot.add_cog(Tags(bot))
