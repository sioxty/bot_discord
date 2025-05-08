import logging

import disnake
from disnake.ext import commands
from .core import YouTubeClient, ManagementSession, song_embed, get_preview
from .core.exception import NotFoundSong
from .core.interface import ISongAPI

log = logging.getLogger(__name__)
api: ISongAPI = YouTubeClient()
manager = ManagementSession()


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="play")
    async def play(self, inter: disnake.ApplicationCommandInteraction, query: str):
        try:
            session = await manager.get_session(inter.author.voice.channel)
            log.info(f"Playing {manager.sessions}")
            await inter.response.defer()
            song = await api.get_song(query)
            await session.add_song(song)
            file = await get_preview(song.thumbnail)
            embed = await song_embed(song)
            embed.set_thumbnail(url="attachment://preview.jpg")
            await inter.send(embed=embed, file=file)
        except NotFoundSong:
            await inter.send("Song not found.")

    @commands.slash_command(name="stop")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.author.voice:
            return await inter.send("You are not connected to a voice channel.")
        session = await manager.get_session(inter.author.voice.channel)
        await session.vc.disconnect()
        await inter.send("Disconnected.")
        manager.sessions.remove(session)

    @commands.slash_command(name="skip")
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.author.voice:
            await inter.send("You are not connected to a voice channel.")
            return
        session = await manager.get_session(inter.author.voice.channel)
        if not session.vc is not None or not session.vc.is_playing():
            await inter.send("Nothing is playing.")
            return
        if session.queue.empty():
            await session.vc.disconnect()
            manager.sessions.remove(session)
            await inter.send("Disconnected.")
            return
        session.vc.stop()
        await inter.send("Skipped.")

    @commands.command(name="sessions")
    async def sessions(self, ctx):
        await ctx.send(f"Sessions: {manager.sessions}")


def setup(bot):
    bot.add_cog(Player(bot))
