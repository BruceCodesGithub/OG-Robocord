import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lock')
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages == False:
            return await ctx.send(f'The channel {channel.mention} is already locked!')
        overwrite.send_messages = False
        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f'Channel lock ran by {ctx.author}')
            await ctx.message.add_reaction(f'{channel.mention} successfully locked!')
        except Exception as e:
            return await ctx.send(f'Something went wrong during locking the channel {channel.mention}!')

    @commands.command(name='unlock')
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages == None:
            return await ctx.send(f'The channel {channel.mention} is already unlocked!')
        overwrite.send_messages = None
        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f'Channel unlock ran by {ctx.author}')
            await ctx.message.add_reaction(f'{channel.mention} successfully unlocked!')
        except Exception as e:
            return await ctx.send(f'Something went wrong during unlocking the channel {channel.mention}!')

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send('You do not have required permissions to use the command.')

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send('You do not have required permissions to use the command.')


def setup(bot):
    bot.add_cog(Moderation(bot))