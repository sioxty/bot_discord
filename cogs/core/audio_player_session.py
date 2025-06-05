import logging
from asyncio import Queue, Event, create_task

import disnake
from aiosoundcloud import SoundCloud
from aiosoundcloud.schemas import Track
from disnake import FFmpegPCMAudio

from .exception import LimitQueue, NotConnectedVoice

log = logging.getLogger(__name__)

FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 "
        "-reconnect_streamed 1 "
        "-reconnect_delay_max 5 "
        "-nostdin "
        "-loglevel warning "
    ),
    "options": ("-vn " "-f s16le "),
}


class AudioPlayerSession:
    def __init__(self, voice_channel: disnake.VoiceChannel, api: SoundCloud) -> None:
        self.LIMIT_QUEUE = 25
        self.voice_channel = voice_channel
        self.queue: Queue[Track] = Queue(maxsize=self.LIMIT_QUEUE)
        self.next_song_event = Event()
        self._is_playing_loop = False
        self.api = api
        self.vc = None

    def __repr__(self) -> str:
        return f"<AudioPlayerSession voice_channel={self.voice_channel.id}>"

    async def add_song(self, song: Track):
        if self.queue.full():
            raise LimitQueue(f"{self.LIMIT_QUEUE} songs in queue")
        await self.queue.put(song)

        if not self.vc:
            create_task(self.play())

    async def connect(self):
        if self.vc is None or not self.vc.is_connected():
            self.vc = await self.voice_channel.connect()

    async def play(self):
        await self.connect()

        while not self.queue.empty():
            song = await self.queue.get()
            self.next_song_event.clear()

            # Define a callback function to be executed after the current song finishes playing.
            def after_playing(error=None):
                if error:
                    log.error(f"Playback error: {error}")  # Log any playback errors.
                self.next_song_event.set()  # Signal that the current song has finished.

            stream_url = await self.api.get_stream_url(song)
            self.vc.play(
                FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS), after=after_playing
            )
            await self.next_song_event.wait()
            self.queue.task_done()

        await self.vc.disconnect()
        self.vc = None
        self._is_playing_loop = False

    async def stop(self):
        if self.vc is None:
            raise NotConnectedVoice("Not connected to a voice channel")
        await self.vc.disconnect()

    async def skip(self):
        if self.vc is None or not self.vc.is_playing():
            raise NotConnectedVoice("Not connected to a voice channel")
        if self.queue.empty():
            await self.vc.disconnect()
            return
        self.vc.stop()


class ManagementSession:
    def __init__(self, api) -> None:
        self.sessions: list[AudioPlayerSession] = []
        self.api: SoundCloud = api

    async def get_session(
        self, voice_channel: disnake.VoiceChannel
    ) -> AudioPlayerSession:
        for session in self.sessions:
            if session.voice_channel.id == voice_channel.id:
                return session
        new_session = AudioPlayerSession(voice_channel, self.api)
        self.sessions.append(new_session)
        log.info(f"Created new session {new_session}")
        return new_session

    async def close(self, session):
        log.info(f"Closing session {session}")
        self.sessions.remove(session)
