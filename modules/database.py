import discord
from discord.ext import commands
import json


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_db(self):
        await self.bot.con.execute(
            "CREATE TABLE IF NOT EXISTS Tags (id BIGINT, name TEXT,content TEXT ,author BIGINT ,aliases TEXT[])"
        )

    async def new(self, n, v):
        exists = await self.bot.con.fetchrow("SELECT name FROM Tags WHERE name=$1", n)
        if exists:
            await ctx.reply("A tag already exists")
        else:
            a = await bot.con.fetchrow("SELECT count(*)")
            await self.bot.con.execute(
                "INSERT INTO Tags (id,name,content,author,aliases) VALUES($1,$2,$3,$4,$5)",
                a + 1,
                n,
                v,
                ctx.author.id,
                [],
            )
            await ctx.reply("Tag succeesfully created")

    async def show(self, n):
        e = await self.bot.con.fetchrow("SELECT content FROM Tags WHERE name=$1", n)
        if not e:
            await ctx.reply("No such tag found")
        else:
            await ctx.reply(e[0])

    @commands.Cog.listener()
    async def on_ready(self):
        await self.create_db()
        print("DB is gud")


def setup(bot):
    bot.add_cog(Database(bot))
