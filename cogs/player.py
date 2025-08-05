import logging

import disnake
from disnake.ext import commands
from aiosoundcloud import SoundCloud
from aiosoundcloud.schemas import Track
from .core import ManagementSession
from .core.audio_player_session import AudioPlayerSession
from .core import view
from .core.exception import LimitQueue, NotConnectedVoice, NotPlaySound
from config import CLIENT_ID


log = logging.getLogger(__name__)
api = SoundCloud(client_id=CLIENT_ID)
manager = ManagementSession(api=api)


async def soundcloud_autocomplete(inter, string: str):
    limit = 5
    if not string or len(string) < 3:
        return []
    try:
        results = await api.search(query=string, limit=limit)
        return [
            disnake.OptionChoice(
                name=f"{track.title} - {track.user.username}"[:100], value=track.title
            )
            for track in results[:limit]
        ]
    except Exception:
        return []


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="play", description="Play a track from SoundCloud by name or link."
    )
    async def play(self, inter: disnake.ApplicationCommandInteraction, query: str = commands.Param(autocomplete=soundcloud_autocomplete)):  # type: ignore

        if not inter.author.voice:  # type: ignore
            return await inter.send("You are not connected to a voice channel.")
        session: AudioPlayerSession = await manager.get_session(inter.author.voice.channel)  # type: ignore
        await inter.response.defer()
        result = await api.search(query, limit=1)

        if not result:
            await inter.send("Song not found.")
            return

        track = result[0]
        await session.play(track)
        embed = await view.track_embed(track)

        await inter.send(embed=embed)

    @commands.slash_command(
        name="stop",
        description="Disconnect the bot from the voice channel and stop playback.",
    )
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        session = await manager.get_session(inter.author.voice.channel)  # type: ignore
        await session.stop()
        await inter.send("Disconnected.")
        manager.sessions.remove(session)

    @commands.slash_command(
        name="skip", description="Skip the current track in the queue."
    )
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        session = await manager.get_session(inter.author.voice.channel)  # type: ignore
        await session.skip()
        await inter.send("Skipped.")

    @commands.slash_command(name="queue", description="Show the current track queue.")
    async def show_queue(self, inter: disnake.ApplicationCommandInteraction):
        if manager.is_session(inter.author.voice.channel):
            inter.send("Player not play", ephemeral=True)
            return
        session = await manager.get_session(inter.author.voice.channel)  # type: ignore
        queue = session.queue.as_list()
        now_track = session.get_track_play_now()
        if not queue:

            if now_track:
                await inter.send(
                    f"play now: {now_track.title} - {now_track.user.username}"
                )
                return
            await inter.send("Queue empty!", ephemeral=True)
            return

        embed = view.queue_embed(session.get_track_play_now(), *queue)
        await inter.send(embed=embed)

    @commands.slash_command(name="playlist", description="Play a playlist by URL.")
    async def playlist(self, inter: disnake.ApplicationCommandInteraction, url: str):
        await inter.response.defer()
        session = await manager.get_session(inter.author.voice.channel)
        # type: ignore
        playlist = await api.get_playlist(
            url, limit=session.queue.LIMIT_QUEUE - session.queue.size()
        )

        await session.play(*playlist.tracks)
        embed = await view.playlist_embed(playlist)
        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(Player(bot))
