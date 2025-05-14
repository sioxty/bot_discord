import logging

import disnake
from disnake.ext import commands
from aiosoundcloud import SoundCloud
from .core import ManagementSession
from .core.audio_player_session import AudioPlayerSession
from .core.view import song_embed
from .core.exception import LimitQueue, NotConnectedVoice
from config import CLIENT_ID


log = logging.getLogger(__name__)
api = SoundCloud(client_id=CLIENT_ID)
manager = ManagementSession(api=api)


async def is_voice_connected(inter: disnake.ApplicationCommandInteraction):
    if not inter.author.voice:
        raise NotConnectedVoice("Not connected to a voice channel")

async def soundcloud_autocomplete(inter, string: str):
    limit = 5
    if not string or len(string) < 3:
        return []

    results = await api.search(query=string, limit=limit)
    return [
        disnake.OptionChoice(name=f"{track.title} - {track.user.username}"[:100], value=track.title)
        for track in results[:limit]
    ]

class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="play")
    async def play(self, inter: disnake.ApplicationCommandInteraction, query: str = commands.Param(autocomplete=soundcloud_autocomplete)):
        try:
            if not inter.author.voice:
                return await inter.send("You are not connected to a voice channel.")
            session: AudioPlayerSession = await manager.get_session(inter.author.voice.channel)
            await inter.response.defer()
            songs = await api.search(query,limit=1)
            if not songs:
                await inter.send("Song not found.")
                return
            await session.add_song(songs[0])
            embed = await song_embed(songs[0])
            await inter.send(embed=embed)
        except LimitQueue:
            await inter.send(f"Queue is full, max {session.LIMIT_QUEUE} songs.")

    @commands.slash_command(name="stop")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        if not inter.author.voice:
            return await inter.send("You are not connected to a voice channel.")
        session = await manager.get_session(inter.author.voice.channel)
        await session.stop()
        await inter.send("Disconnected.")
        manager.sessions.remove(session)

    @commands.slash_command(name="skip")
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        try:
            await is_voice_connected(inter)
            session = await manager.get_session(inter.author.voice.channel)
            await session.skip()
            await inter.send("Skipped.")
        except NotConnectedVoice:
            await inter.send("Not connected to a voice channel.")



def setup(bot):
    bot.add_cog(Player(bot))
