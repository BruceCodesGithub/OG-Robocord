import discord
from discord.ext import commands
import io, random
import animec


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="anime")
    async def _anime(self, ctx, *, query):
      try:
        anime = animec.Anime(query)
      except:
        await ctx.send(embed = discord.Embed(description="No anime with that name was found."))
        return
      
      embed = discord.Embed(title=anime.title_english, url = anime.url, description=f"{anime.description[:200]}...", color=discord.Color.random())
      embed.add_field(name="Rating", value=f"{anime.rating}", inline=True)
      embed.add_field(name="Ranking", value=f"{anime.ranked}", inline=True)
      embed.add_field(name="Status", value=f"{anime.status}", inline=False)
      embed.add_field(name="Episodes", value=f"{anime.episodes}", inline=False)
      embed.set_image(url=anime.poster)
      await ctx.send(embed=embed)

    @commands.command(name="aninews")
    async def _anime_news(self, ctx):
      news = animec.aninews.Aninews(amount=5)
      embed = discord.Embed(title="Anime news", description="For the weeb army and in the honor of Atomic Baby", color=discord.Color.random())
      embed.add_field(name=news.titles[0], value=f"{news.description[0][:400]}... [Continue Reading]({news.links[0]})")
      embed.add_field(name=news.titles[1], value=f"{news.description[1][:300]}... [Continue Reading]({news.links[1]})")
      embed.add_field(name=news.titles[2], value=f"{news.description[2][:300]}... [Continue Reading]({news.links[2]})")
      embed.add_field(name=news.titles[3], value=f"{news.description[3][:200]}... [Continue Reading]({news.links[3]})")
      embed.add_field(name=news.titles[4], value=f"{news.description[4][:200]}... [Continue Reading]({news.links[4]})")
      await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Fun(bot))
