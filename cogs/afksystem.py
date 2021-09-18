from discord.ext import commands
from discord import AllowedMentions

class AFKSystem(commands.Cog, description = 'An AFK setting system!'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def afk(self, ctx, *, reason = 'No reason provided'):
        if self.bot.afk_people.get(ctx.author.id):
            return await ctx.send(f'{ctx.author.name}, you\'re already AFK')
        if len(reason) > 100: # so that chat doesn't flood when the reason has to be shown
            return await ctx.send(f'{ctx.author.name}, keep your AFK reason under 100 characters')
        self.bot.afk_people[ctx.author.id] = reason
        await ctx.send(f'{ctx.author.name}, you are now AFK', delete_after = 5)
        
    @commands.Cog.listener()
    async def on_message(self, msg):
        if self.bot.afk_people.get(msg.author.id):
            del self.bot.afk_people[msg.author.id]
            return await msg.channel.send(f'Welcome back {ctx.author.name}, you are no longer AFK')
        
        for mention in msg.mentions:
            if self.bot.afk_people.get(mention.id):
                return await msg.channel.send(f'{mention.name} is AFK: {self.bot.afk_people[mention.id]}', allowed_mentions = AllowedMentions.none())
            
def setup(bot):
    bot.add_cog(AFKSystem(bot))
