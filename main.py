import asyncio, calendar, datetime, io, json, math, os, random, time, unicodedata, aiohttp, discord, humanize, requests
from asyncpg import create_pool
from discord import DMChannel
from discord.ext import commands, tasks
from discord.app import Option
from discord.ext.commands import (BucketType,MissingPermissions,command,cooldown,has_permissions)
from dotenv import load_dotenv
from storage.bot_data import *
import ext.helpers as helpers
from pathlib import Path
from storage.morse import *

reqd_guilds = [881207955029110855,869782707226439720] #[pycord server,testing server]

owners = [
571638000661037056 #bruce
,761932885565374474 #oli
,754557382708822137,  #marcus
685082846993317953 #geno
]
owner = owners[0]

class HelpCommand(commands.HelpCommand):
    def get_ending_note(self):
        return "Use {0}{1} [command] for more info on a command.".format(
            self.clean_prefix, self.invoked_with
        )

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = "|".join(command.aliases)
            fmt = f"[{command.name}|{aliases}]"
            if parent:
                fmt = f"{parent}, {fmt}"
            alias = fmt
        else:
            alias = command.name if not parent else f"{parent} {command.name}"
        return f"{alias} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Pycord-Chan", color=discord.Color.blurple())
        description = self.context.bot.description
        if description:
            embed.description = description

        for cog_, cmds in mapping.items():
            name = "Other Commands" if cog_ is None else cog_.qualified_name
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                value = "\u2002".join(c.name for c in cmds)
                if cog_ and cog_.description:
                    value = "{0}\n{1}".format(cog_.description, value)

                embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog_):
        embed = discord.Embed(title="{0.qualified_name} Commands".format(cog_))
        if cog_.description:
            embed.description = cog_.description

        filtered = await self.filter_commands(cog_.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(
                name=self.get_command_signature(command),
                value=command.short_doc or "...",
                inline=False,
            )

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name)
        if group.help:
            embed.description = group.help

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.short_doc or "...",
                    inline=False,
                )

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

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

def get_extensions():
    extensions = []
    extensions.append("jishaku")
    for file in Path("cogs").glob("**/*.py"):
        if "!" in file.name or "DEV" in file.name:
            continue
        extensions.append(str(file).replace("/", ".").replace(".py", ""))
    return extensions

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"

@bot.event
async def on_ready():
    print(f"{bot.user} is Ready and Online!")

@bot.event
async def on_command_error(ctx, error):
    exception = error
    if hasattr(ctx.command, "on_error"):
        pass
    error = getattr(error, "original", error)

    if ctx.author.id in ctx.bot.owner_ids:
        if isinstance(error,(commands.MissingAnyRole,commands.CheckFailure,commands.DisabledCommand,commands.CommandOnCooldown,commands.MissingPermissions,commands.MaxConcurrencyReached),):
            try:
                await ctx.reinvoke()
            except discord.ext.commands.CommandError as e:
                pass
            else:
                return

    if isinstance( error,(commands.BadArgument,commands.MissingRequiredArgument,commands.NoPrivateMessage,commands.CheckFailure,commands.DisabledCommand,commands.CommandInvokeError,commands.TooManyArguments,commands.UserInputError,commands.NotOwner,commands.MissingPermissions,commands.BotMissingPermissions,commands.MaxConcurrencyReached,commands.CommandNotFound,),):
        await helpers.log_command_error(ctx, exception, True)
        if not isinstance(error, commands.CommandNotFound):
            if await helpers.is_disabled(ctx):
                return
        text = None
        if isinstance(error, commands.CheckFailure):
            if bot.disabled:
                text = "The bot is currently disabled. It will be back soon."
        if not isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="Error", description=text or str(error), color=discord.Color.red()
            )
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            owner = bot.get_user(ctx.bot.owner_ids[0])
            embed.set_footer(
                icon_url=bot.user.avatar_url,
                text=f"If you think this is a mistake please contact {owner}",
            )
            await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        await helpers.log_command_error(ctx, exception, True)
        time2 = datetime.timedelta(seconds=math.ceil(error.retry_after))
        error = f"You are on cooldown. Try again after {humanize.precisedelta(time2)}"
        embed = discord.Embed(
            title="Error", description=error, color=discord.Color.red()
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        owner = bot.get_user(ctx.bot.owner_ids[0])
        embed.set_footer(
            icon_url=bot.user.avatar_url,
            text=f"If you think this is a mistake please contact {owner}",
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
                    f"<@{ctx.bot.owner_ids[0]}>"
                ),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            pass
        await helpers.log_command_error(ctx, exception, False)

bot.launch_time = datetime.datetime.utcnow()

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

@bot.slash_command(guild_ids=reqd_guilds, description="Frequently Asked Questions about pycord")
async def faq(
    ctx,
    question: Option(str, "Choose your question", choices=["How to create Slash Commands", "How to create Context Menu Commands", "How to create buttons"]),
    display: Option(str, "Should this message be private or displayed to everyone?", choices=["Ephemeral", "Displayed"], default="Ephemeral", required=False)):
	isprivate = display == "Ephemeral"
	if question == "How to create Slash Commands":
		await ctx.send(f"{data['slash-commands']}", ephemeral=isprivate)
	elif question == "How to create Context Menu Commands":
		await ctx.send(f"{data['context-menu-commands']}", ephemeral=isprivate)
	elif question == "How to create buttons":
		await ctx.send(f"{data['buttons']}", ephemeral=isprivate)

@bot.slash_command(guild_ids=reqd_guilds)
async def issue(ctx, number:Option(int, "The issue number")):
	link = f'https://github.com/Pycord-Development/pycord/issues/{number}'
	response = requests.get(link)
	if response.status_code == 200:
		await ctx.send(f'{link}')
	else:
		await ctx.send(f'That issue doesn\'t seem to exist. If you think this is a mistake, contact {owner}.')

@bot.slash_command(guild_ids=reqd_guilds)
async def pr(ctx, number:Option(int, "The pr number")):
	link = f'https://github.com/Pycord-Development/pycord/pull/{number}'
	response = requests.get(link)
	if response.status_code == 200:
		await ctx.send(f'{link}')
	else:
		await ctx.send(f'That pull request doesn\'t seem to exist in the repo. If you think this is a mistake, contact {owner}.')

@bot.user_command(name="Join Position", guild_ids=reqd_guilds)
async def _joinpos(ctx, member:discord.Member):
	all_members = list(ctx.guild.members)
	all_members.sort(key=lambda m: m.joined_at)
	def ord(n):
		return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
	embed = discord.Embed(title = "Member info", description = f'{member.mention} was the {ord(all_members.index(member) + 1)} person to join')
	await ctx.send(embed=embed)

def encrypt(message):
    cipher = ''
    for letter in message:
        if letter != ' ':
            cipher += MORSE_CODE_DICT[letter] + ' '
        else:
            cipher += ' '
    return cipher

def decrypt(message):
    message += ' '
    decipher = ''
    citext = ''
    for letter in message:
        if (letter != ' '):
            i = 0
            citext += letter
        else:
            i += 1
            if i == 2 :
                decipher += ' '
            else:
                decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT
                .values()).index(citext)]
                citext = ''
    return decipher

@bot.message_command(name="Encrypt to Morse", guild_ids=reqd_guilds)
async def _tomorse(ctx, message:discord.message):
	result = encrypt(message.content.upper())
	await ctx.send(result)

@bot.message_command(name="Decrypt Morse", guild_ids=reqd_guilds)
async def _frommorse(ctx, message:discord.message):
	result = decrypt(message.content)
	await ctx.send(result)

@bot.message_command(name="Decrypt binary", guild_ids=reqd_guilds)
async def _frombinary(ctx, message:discord.message):
	a_binary_string = message.content
	binary_values = a_binary_string.split()
	ascii_string = ""
	for binary_value in binary_values:
		an_integer = int(binary_value, 2)
		ascii_character = chr(an_integer)
		ascii_string += ascii_character
	await ctx.send(ascii_string)

@bot.message_command(name="Encrypt to binary", guild_ids=reqd_guilds)
async def _tobinary(ctx, message:discord.message):
	a_string = message.content
	a_byte_array = bytearray(a_string, "utf8")
	byte_list = []
	for byte in a_byte_array:
		binary_representation = bin(byte)
		byte_list.append(binary_representation)
	await ctx.send(" ".join(byte_list))

# @bot.slash_command(name="Decrypt from hex", guild_ids=[869782707226439720, 881207955029110855])
# async def _fromhex(ctx, message:discord.message):
# 	hex_string = message.content[2:]

# 	bytes_object = bytes.fromhex(hex_string)


# 	ascii_string = bytes_object.decode("ASCII")

# 	await ctx.send(ascii_string)

# @bot.message_command(name="Encrypt to hex", guild_ids=[869782707226439720, 881207955029110855])
# async def _tohex(ctx, message:discord.message):
# 	hex_string = message.content
# 	an_integer = int(hex_string, 16)
# 	hex_value = hex(an_integer)
# 	await ctx.send(hex_value)

@bot.user_command(name="Avatar",  guild_ids=reqd_guilds)
async def _avatar(ctx, member:discord.Member):
	embed = discord.Embed(title=f'{member}\'s avatar!', description=f"[Link]({member.avatar.url})", color=member.color)
	try:
		embed.set_image(url=member.avatar.url)
	except AttributeError:
		embed.set_image(url=member.display_avatar.url)
	await ctx.send(embed=embed)

for ext in get_extensions():
    bot.load_extension(ext)

load_dotenv()
bot.loop.run_until_complete(create_db_pool())
bot.run(os.getenv("TOKEN"))
