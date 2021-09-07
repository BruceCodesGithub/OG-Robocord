# this file contains a bunch of data to make the code cleaner and less spammy. Many variables, lists and dicts are dfined here.

data = {
    "slash-commands": """**What are Slash Commands?**
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
```""",
    "context-menu-commands": """**What are user commands and message commands?**
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

bot.run("TOKEN")
```""",
}
