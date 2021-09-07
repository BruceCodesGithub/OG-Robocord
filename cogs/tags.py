import discord
from discord.ext import commands, helpers
from cogs.database import Database
from random import randint
from cogs.Paginator import paginator

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(self.bot)
        self.paginate = paginator(self.bot)

    @commands.group(invoke_without_command=True)
    async def tag(self,ctx,name=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        a = await self.db.show(name)
        await ctx.reply(a)

    @tag.command()
    async def create(self,ctx,name=None,*,value=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        if not value:
            return await ctx.reply("Value is a required argument")
        if not name.lower() in ['create','edit','delete','make','add','remove','info','transfer','claim','all']:
            b = await self.db.new(name,value,ctx.author.id)
            await ctx.reply(b)
        else:
            await ctx.reply("That name is reserved")

    @tag.command()
    async def delete(self,ctx,name=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        f=ctx.author.guild_permissions.manage_messages
        b = await self.db.remove(name,ctx.author.id,f)
        await ctx.reply(b)

    @tag.command()
    async def edit(self,ctx,name=None,*,value=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        if not value:
            return await ctx.reply("Value is a required argument")
        b = await self.db.update(name,value,ctx.author.id)
        await ctx.reply(b)

    @tag.command()
    async def info(self,ctx,name=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        b = await self.db.data(name)
        embed = discord.Embed(title=name,color=randint(0,0xffffff))
        if not b == 'nothing found':
            embed.add_field(name="Author",value=f'<@{b}>')
            await ctx.reply(embed=embed)
            return
        else:
            await ctx.send("Nothing Found")
        
    @tag.command()
    async def transfer(self,ctx,name=None,member:discord.Member=None):
        if not name:
            return await ctx.reply("Name is a required argument")
        if not member:
            return await ctx.reply('Member is a required argument')
        b = await self.db.transfer(name,ctx.author.id,member.id)
        await ctx.reply(b)

    @tag.command()
    async def alias(self,ctx,n,a):
        a = await self.db.set_aliases(n,a,ctx.author.id)
        await ctx.send(a)

    @tag.command()
    async def claim(self,ctx,n):
        listx = ctx.guild.members
        m = []
        for i in range(len(listx)):
            m.append(listx[i])
        s = await self.db.see_if_not(n)
        s = ctx.guild.get_member(s)
        if s in m:
            await ctx.reply("The tag owner is still in the server")
        else:
            b = await self.db.transfer_not(n, ctx.author.id)
            await ctx.reply(b)

    @tag.command()
    async def all(self,ctx):
        b = await self.db.view_all()
        if b == "Server has no tags":
            return
        c = [i[0] for i in b]
        embeds = [] 
        a = 1
        d = ''
        while c:
            try:
                g = c[0:10]
                for i in g:
                    d += f'{a}) {i} \n'
                    a += 1
                embed = discord.Embed(title=f"{ctx.guild.name}'s tags",description=d,color=randint(0,0xffffff))
                embeds.append(embed)
                d = ''
                del c[0:10]
            except IndexError:
                g = c[0:-1]
                for i in g:
                    d += f'{a}) {i} \n'
                embed = discord.Embed(title=f"{ctx.guild.name}'s tags",description=d,color=randint(0,0xffffff))
                embeds.append(embed)   
                d = ''
                del c[0:-1]     
        await self.paginate.paginato(ctx, embeds)            

    @commands.command()
    async def tags(self,ctx,m:discord.Member=None):
        if m == None:
            m = ctx.author
        b = await self.db.mine(m.id)
        if b == "You have no tags":
            return
        c = [i[0] for i in b]
        embeds = []
        a = 1  
        d = '' 
        while c:
            try:
                g = c[0:10]
                for i in g:
                    d += f'{a}) {i} \n'
                    a += 1
                embed = discord.Embed(title=f"{m.name}'s tags",description=d,color=randint(0,0xffffff))
                embeds.append(embed)
                d = ''
                del c[0:10]
            except IndexError:
                g = c[0:-1]
                for i in g:
                    d += f'{a}) {i} \n'
                embed = discord.Embed(title=f"{m.name}'s tags",description=d,color=randint(0,0xffffff))
                embeds.append(embed)   
                d = ''
                del c[0:-1]     
        await self.paginate.paginato(ctx, embeds)



def setup(bot):
    bot.add_cog(Tags(bot))
