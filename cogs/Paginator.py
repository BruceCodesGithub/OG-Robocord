import discord
from discord.ext import commands
import asyncio

class paginator(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def paginato(self,ctx,p):
        m = await ctx.send(embed=p[0])
        c = p[0]
        a = ['⏪','⬅️','➡️','⏩']
        if not len(p) == 1:
            for i in a:
                await m.add_reaction(i)
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add',check=lambda reaction, user: user == ctx.author and reaction.emoji in a,timeout=30.0)
                except asyncio.TimeoutError:
                    for i in a[::-1]:
                        await m.remove_reaction(i,member=self.bot.user)
                    break
                else:
                    if reaction.emoji == '⬅️':
                        l = p.index(c)
                        if not l == 0:
                            c = p[l-1]
                            await m.remove_reaction('⬅️',member=ctx.author)
                            await m.edit(embed=c)
                        else:
                            await m.remove_reaction('⬅️',member=ctx.author)
                    elif reaction.emoji == '➡️':
                        l = p.index(c)
                        if not l == len(p)-1:
                            c = p[l+1]
                            await m.remove_reaction('➡️',member=ctx.author)
                            await m.edit(embed=c)
                        else:
                            await m.remove_reaction('➡️',member=ctx.author) 
                    elif reaction.emoji == '⏪':
                        c = p[0]
                        await m.remove_reaction('⏪',member=ctx.author)
                        await m.edit(embed=c)
                    elif reaction.emoji == '⏩':
                        c = p[-1]
                        await m.remove_reaction('⏩',member=ctx.author)
                        await m.edit(embed=c)                        
                    continue
            else:
                pass


def setup(bot):
    bot.add_cog(paginator(bot))