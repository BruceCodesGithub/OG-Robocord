import discord
from discord.ext import commands
from cogs.database import Database

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(self.bot)

    @commands.group(invoke_without_command=True)
    async def tag(self,ctx,name):
        a = await self.db.show(name)
        await ctx.reply(a)

    @tag.command()
    async def create(self,ctx,name,*,value):
        if not name.lower() in ['create','edit','delete','make','add','remove']:
            b = await self.db.new(name,value,ctx.author.id)
            await ctx.reply(b)
        else:
            await ctx.reply("That name is reserved")

    @tag.command()
    async def delete(self,ctx,name):
        b = await self.db.remove(name,ctx.author.id)
        await ctx.reply(b)

    @tag.command()
    async def edit(self,ctx,name,*,value):
        b = await self.db.update(name,value,ctx.author.id)
        await ctx.reply(b)

    @tag.command()
    async def info(self,ctx,name):
        b = await self.db.data(name)
        embed = discord.Embed(title=name)
        embed.add_field(name="Id",value=b[0])
        embed.add_field(name="Author",value=f'<@{b[1]}>')
        await ctx.reply(embed=embed)

    

def setup(bot):
    bot.add_cog(Tags(bot))
