from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_db(self):
        await self.bot.con.execute(
            "CREATE TABLE IF NOT EXISTS Tags (name TEXT,content TEXT ,author BIGINT ,aliases TEXT[])"
        )

    async def new(self, n, v, i):
        exists = await self.bot.con.fetchrow("SELECT name FROM Tags WHERE name=$1", n)
        if exists:
            return "A tag with that name already exists"
        else:
            await self.bot.con.execute(
                "INSERT INTO Tags (name,content,author) VALUES($1,$2,$3)", n, v, i
            )
            return "Tag succesfully created"

    async def show(self, n):
        e = await self.bot.con.fetchrow("SELECT content FROM Tags WHERE name=$1", n)
        if not e:
            return "No such tag found"
        else:
            return e[0]

    async def remove(self, n, auth, allowed=False):
        e = await self.bot.con.fetchrow("SELECT content FROM Tags WHERE name=$1", n)
        if not e:
            return "No such tag found"
        else:
            authcheck = await self.bot.con.fetchrow(
                "SELECT author FROM Tags WHERE name=$1", n
            )
            if authcheck[0] == auth or allowed:
                a = e[0]
                await self.bot.con.execute("DELETE FROM Tags WHERE name=$1", n)
                return "Succsfully Deleted"
            else:
                return "You dont own the tag"

    async def update(self, n, c, auth):
        e = await self.bot.con.fetchrow("SELECT content FROM Tags WHERE name=$1", n)
        if not e:
            return "No such tag found"
        else:
            authcheck = await self.bot.con.fetchrow(
                "SELECT author FROM Tags WHERE name=$1", n
            )
            if authcheck[0] == auth:
                a = e[0]
                await self.bot.con.execute(
                    "UPDATE Tags SET content=$1 WHERE name=$2", c, n
                )
                return "Succesfully Edited"
            else:
                return "You dont own the tag"

    async def data(self, n):
        e = await self.bot.con.fetchrow("SELECT author FROM Tags WHERE name=$1", n)
        if e:
            return e[0]
        else:
            return "nothing found"

    async def transfer(self, n, auth, auth2):
        e = await self.bot.con.fetchrow("SELECT author FROM Tags WHERE name=$1", n)
        if not e:
            return "No such tags found"
        else:
            if e[0] == auth:
                await self.bot.con.execute(
                    "UPDATE Tags SET author=$1 WHERE name=$2", auth2, n
                )
                return "Succesfully transfered ownership of tag"
            else:
                return "You dont own the tag"

    async def mine(self, auth):
        e = await self.bot.con.fetch("SELECT name FROM Tags WHERE author=$1", auth)
        if not e:
            return "You have no tags"
        else:
            return e

    async def view_all(self):
        e = await self.bot.con.fetch("SELECT name FROM Tags")
        if not e:
            return "You have no tags"
        else:
            return e

    async def set_aliases(self, n, a, auth):
        e = await self.bot.con.fetchrow("SELECT content FROM Tags WHERE name=$1", n)
        if not e:
            return "Tag not found"
        else:
            e = e[0]
            await self.bot.con.execute(
                "INSERT INTO Tags (name,content,author) VALUES($1,$2,$3)", a, e, auth
            )
            return "SUCCESS"

    async def see_if_not(self, n):
        e = await self.bot.con.fetchrow("SELECT author FROM Tags WHERE name=$1", n)
        if not e:
            return "Tag not found"
        else:
            return e[0]

    async def transfer_not(self, n, auth):
        await self.bot.con.execute("UPDATE Tags SET author=$1 WHERE name=$2", auth, n)
        return "Succesfully Claimed"

    @commands.Cog.listener()
    async def on_ready(self):
        await self.create_db()
        print("DB is gud")


def setup(bot):
    bot.add_cog(Database(bot))
