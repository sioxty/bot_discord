from asyncio import Queue
import asyncio
import logging
from typing import override
import disnake

from aiosoundcloud.schemas import Track
from .session import Session, ManagerSession

from .exception import LimitQueue, NotPlaySound, NotConnectedVoice

log = logging.getLogger(__name__)


class TrackQueue:
    def __init__(self, limit):
        self.LIMIT_QUEUE = limit
        self._queue = Queue(maxsize=limit)

    async def add(self, track: Track):
        if self._queue.full():
            raise LimitQueue("Queue is full")
        await self._queue.put(track)

    async def get(self):
        return await self._queue.get()

    def is_empty(self):
        return self._queue.empty()

    def task_done(self):
        self._queue.task_done()

    def as_list(self):
        return list(self._queue._queue)

    def size(self):
        return self._queue.qsize()


class AudioPlayer(Session):
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

    def __init__(self, voice_channel: disnake.VoiceChannel, manager):

        super().__init__(voice_channel.id, manager)
        self.__voice_channel = voice_channel
        self.__voice_client: disnake.VoiceClient | None
        self.__now_play: Track = None
        self.queue = TrackQueue(10)

    @property
    def now_play(self):
        return self.__now_play

    async def __connect(self):
        if self.__voice_client is None:
            self.__voice_client = self.__voice_channel.connect()

    async def play_loop(self):
        await self.__connect()
        while not self.queue.is_empty():
            track = await self.queue.get()
            await self._play(track)
            self.queue.task_done()
        await self.stop()

    async def _play(self, track: Track):
        self.__now_play = track

        def after_playing(error=None):
            if error:
                log.error(f"Playback error: {error}")

        stream_url = await track.get_stream()
        self.__voice_client.play(
            disnake.FFmpegPCMAudio(stream_url, **self.FFMPEG_OPTIONS),
            after=after_playing,
        )

    async def skip(self):
        self.__voice_client.stop()

    async def stop(self):
        await self.__voice_client.disconnect()
        self.close()


class PlayerManager(ManagerSession):
    @override
    def get_session(self, voice_channel: disnake.VoiceChannel) -> AudioPlayer:
        if not isinstance(voice_channel, disnake.VoiceChannel):
            raise NotConnectedVoice("Not connected to a voice channel.")
        session = super().get_session(voice_channel.id)
        if session is None:
            self.create(AudioPlayer(voice_channel, self))
            session = self.get_session(voice_channel.id)
        return session


player_manager = PlayerManager()
