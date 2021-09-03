import discord
from discord.ext import commands, tasks
from discord.app import Option
from discord.ext.commands import when_mentioned_or, command, has_permissions, MissingPermissions, cooldown, BucketType
import datetime
import asyncio, aiohttp
from discord import DMChannel
import requests, humanize, json, asyncpg
import calendar, math, unicodedata, random, os, time, io
import ext.helpers as helpers
import asyncpg


async def create_db_pool():
    bot.con = await asyncpg.create_pool(
        database="pycord", user="<insert user here>", password="<insert pass here>"
    )

class HelpCommand(commands.HelpCommand):
  
    def get_ending_note(self):
        return 'Use p!{0} [command] for more info on a command.'.format(
            self.invoked_with)

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent}, {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Robocord', color=discord.Color.blurple())
        description = self.context.bot.description
        if description:
            embed.description = description

        for cog_, cmds in mapping.items():
            name = 'Other Commands' if cog_ is None else cog_.qualified_name
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                value = '\u002C '.join(f"`{c.name}`" for c in cmds)
                if cog_ and cog_.description:
                    value = '{0}\n{1}'.format(cog_.description, value)

                embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog_):
        embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog_))
        if cog_.description:
            embed.description = cog_.description

        filtered = await self.filter_commands(cog_.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command),
                            value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name)
        if group.help:
            embed.description = group.help

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(name=self.get_command_signature(command),
                                value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    # This makes it so it uses the function above
    # Less work for us to do since they're both similar.
    # If you want to make regular command help look different then override it
    send_command_help = send_group_help


bot = commands.Bot(
    command_prefix="p!",
    description="The bot build with and for pycord.",
    case_insensitive=True,
    embed_color=discord.Color.blurple(),
    help_command=HelpCommand(),
    activity=discord.Activity(
        type=discord.ActivityType.competing, name="What's dpy's Best Fork?"
    ),
    status=discord.Status.online,
)

bot.owner_ids = [571638000661037056, 761932885565374474]


@bot.event
async def on_invite_create(invite):
    await bot.tracker.update_invite_cache(invite)


@bot.event
async def on_invite_delete(invite):
    await bot.tracker.remove_invite_cache(invite)


os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"


bot.server_cache = {}
bot.session = aiohttp.ClientSession()
bot.default_prefixes = ["p!"]

# async def prefix(bot_, message):
#     return commands.when_mentioned_or(*(await helpers.prefix(bot_, message)))( 
#         bot_, message
#     )
# yall set the prefix manually to "p!" :bruh:

@bot.event
async def on_ready():
    print("{} is Ready and Online!".format(bot.user))
    print(f"Default Prefixes: {', '.join(bot.default_prefixes)}")


@bot.event
async def on_command_error(ctx, error):
    exception = error
    if hasattr(ctx.command, "on_error"):
        pass
    error = getattr(error, "original", error)

    if ctx.author.id in ctx.bot.owner_ids:
        if isinstance(
            error,
            (
                commands.MissingAnyRole,
                commands.CheckFailure,
                commands.DisabledCommand,
                commands.CommandOnCooldown,
                commands.MissingPermissions,
                commands.MaxConcurrencyReached,
            ),
        ):
            try:
                await ctx.reinvoke()
            except discord.ext.commands.CommandError as e:
                pass
            else:
                return

    if isinstance(
        error,
        (
            commands.BadArgument,
            commands.MissingRequiredArgument,
            commands.NoPrivateMessage,
            commands.CheckFailure,
            commands.DisabledCommand,
            commands.CommandInvokeError,
            commands.TooManyArguments,
            commands.UserInputError,
            commands.NotOwner,
            commands.MissingPermissions,
            commands.BotMissingPermissions,
            commands.MaxConcurrencyReached,
            commands.CommandNotFound,
        ),
    ):
        text = None
        if isinstance(error, commands.CheckFailure):
            if bot.disabled:
                text = "The bot is currently disabled. It will be back soon."
        if not isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="Error", description=text or str(error), color=discord.Color.red()
            )
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            owner = bot.get_user(ctx.bot.owner_ids[0])
            embed.set_footer(
                icon_url=bot.user.avatar.url,
                text=f"If you think this is a mistake please contact BruceDev#0001",
            )
            await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        time2 = datetime.timedelta(seconds=math.ceil(error.retry_after))
        error = f"You are on cooldown. Try again after {humanize.precisedelta(time2)}"
        embed = discord.Embed(
            title="Error", description=error, color=discord.Color.red()
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        owner = bot.get_user(ctx.bot.owner_ids[0])
        embed.set_footer(
            icon_url=bot.user.avatar.url,
            text=f"If you think this is a mistake please contact BruceDev#0001",
        )
        await ctx.send(embed=embed)

    else:
        try:
            raise error
            embed = discord.Embed(
                title="Oh no!",
                description=(
                    "An error occurred. My developer has been notified of it, "
                    "but if it continues to occur please DM "
                    f"<@571638000661037056>"
                ),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            pass


# bot.launch_time = datetime.datetime.utcnow()

@bot.command()
async def ping(ctx):
    loading = "<:thinkCat:853565931838242816>"
    ws_ping = (
        f"{(bot.latency * 1000):.2f}ms "
        f"({humanize.precisedelta(datetime.timedelta(seconds=bot.latency))})"
    )
    embed = discord.Embed(
        title="PONG!  :ping_pong:",
        description=(
            f"**{loading} Websocket:** {ws_ping}\n** :repeat: Round-Trip:** Calculating..."
        ),
        color=discord.Color.blurple(),
    )
    start = time.perf_counter()
    message = await ctx.send(embed=embed)
    end = time.perf_counter()
    await asyncio.sleep(0.5)
    trip = end - start
    rt_ping = f"{(trip * 1000):.2f}ms ({humanize.precisedelta(datetime.timedelta(seconds=trip))})"
    embed.description = (
        f"**{loading} Websocket:** {ws_ping}\n**" f":repeat: Round-Trip:** {rt_ping}."
    )
    await message.edit(embed=embed)
    await asyncio.sleep(0.5)
    start = time.perf_counter()
    await message.edit(embed=embed)


@bot.slash_command(guild_ids=[881207955029110855, 869782707226439720], description="Change the slowmode of a channel.")
@commands.has_any_role(882105157536591932, 881407111211384902, 881411529415729173, 881223795501846558)
async def setdelay(ctx, seconds: Option(int,"Slowmode time in seconds", required=True)):
  role = discord.utils.find(lambda r: r.id == 881407111211384902, ctx.author.guild.roles)
  role2 = discord.utils.find(lambda r: r.id == 881411529415729173, ctx.author.guild.roles)    
  if role in ctx.author.roles or role2 in ctx.author.roles:
      await ctx.channel.edit(slowmode_delay=seconds)
      await ctx.respond(f"Set the slowmode delay in this channel to {seconds} seconds!")

  else:
    await ctx.respond('You do not have the required roles!')

@bot.slash_command(guild_ids=[881207955029110855, 869782707226439720], description="Frequently Asked Questions about pycord")
async def faq(
    ctx,
    question: Option(str, "Choose your question", choices=["How to create Slash Commands", "How to create Context Menu Commands"]),
    display: Option(str, "Should this message be private or displayed to everyone?", choices=["Ephemeral", "Displayed"], default="Ephemeral", required=False)):
  if display == "Ephemeral":
    isprivate = True
  else:
    isprivate = False
  if question == "How to create Slash Commands":
      await ctx.send("""**What are Slash Commands?**
When you type `/`, you can see a list of commands a bot can use. These are called Slash Commands, and can be invoked with a Slash.

**Can I use them with pycord?**
Slash commands are not out in the stable version yet, but with the alpha and slash branch version of Py-cord, you can make user and message commands. Warning: Alpha and the slash branch can be unstable.
To update to Slash Branch, use, 
```bash
pip install git+https://github.com/Pycord-Development/pycord@slash
```
:warning: Make sure you have git installed.  Use `!git` to find out how to install it, or type `git` in the terminal to check if you already have it.

**Examples:**
```py
import discord
from discord.app import Option

bot = discord.Bot() # If you use commands.Bot, @bot.slash_command should be used for slash commands. You can use @bot.slash_command with discord.Bot as well

@bot.command(guild_ids=[...])
async def hello(
    ctx,
    name: Option(str, "Enter your name"),
    gender: Option(str, "Choose your gender", choices=["Male", "Female", "Other"]),
    age: Option(int, "Enter your age", required=False, default=18),
):
    await ctx.send(f"Hello {name}")

bot.run("TOKEN")
```""", ephemeral=isprivate)
  elif question == "How to create Context Menu Commands":
    await ctx.send("""**What are user commands and message commands?**
When you right click a message, you may see a option called "Apps". Hover over it and you can see commands a bot can run with that message. These are called message commands.
When you right click a message in the user list, you can once again see an option called "Apps". Hover over it and you can see commands a bot can run with that message. These are called user commands.

**Can I use them with pycord?**
With the alpha version of Py-cord, you can make user and message commands. Warning: Alpha can be unstable.
To update to Alpha, use
```bash
pip install -U git+https://github.com/Pycord-Development/pycord
```
:warning: Make sure you have git installed.  Use `!git` to find out how to install it, or type `git` in the terminal to check if you already have it installed.

**Examples**:
```py
import discord

bot = discord.Bot() # you can also use commands.Bot()

@bot.user_command(guild_ids=[...])  # create a user command for the supplied guilds
async def mention(ctx, member: discord.Member):  # user commands return the member
    await ctx.respond(f"{ctx.author.name} just mentioned {member.mention}!")

# user commands and message commands can have spaces in their names
@bot.message_command(name="Show ID")  # creates a global message command. use guild_ids=[] to create guild-specific commands.
async def show_id(ctx, message: discord.Message):  # message commands return the message
    await ctx.respond(f"{ctx.author.name}, here's the message id: {message.id}!")

```""", ephemeral=isprivate)


for i in ['jishaku', 'cogs.rtfm']:
    bot.load_extension(i)
    
load_dotenv()
bot.loop.run_until_complete(create_db_pool())
bot.run(os.getenv("TOKEN"))
