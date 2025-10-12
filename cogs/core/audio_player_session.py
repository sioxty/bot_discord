import logging
from asyncio import Queue, Event, create_task

import disnake
from aiosoundcloud import SoundCloud
from aiosoundcloud.schemas import Track
from disnake import FFmpegPCMAudio, VoiceClient

from config import LIMIT_QUEUE
from .session import Session, ManagerSession
from .exception import LimitQueue, NotConnectedVoice, NotPlaySound
from config import api

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


class TrackQueue:
    def __init__(self, limit):
        self.LIMIT_QUEUE = limit
        self._queue = Queue(maxsize=limit)

    async def add(self, track):
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
    def __init__(self, voice_channel: disnake.VoiceChannel, manager) -> None:
        super().__init__(voice_channel.id, manager)
        self.__voice_channel = voice_channel
        self.queue = TrackQueue(limit=LIMIT_QUEUE)
        self.__next_song_event = Event()
        self.__now_play_track: Track | None = None
        self.__api = api
        self.__vc: VoiceClient | None = None

    async def play(self, *tracks: Track):
        if tracks:
            for track in tracks[: self.queue.LIMIT_QUEUE - self.queue.size()]:
                await self.queue.add(track)

        if not self.__vc:  # Not connected to a voice channel
            create_task(self.__play())

    async def connect(self):
        if self.__vc is None or not self.__vc.is_connected():
            self.__vc = await self.__voice_channel.connect()

    async def __play(self):
        await self.__play_loop()
        await self.__vc.disconnect()
        self.__vc = None

    async def stop(self):
        if not self.__vc or not self.__vc.is_connected():
            raise NotConnectedVoice("Not connected to a voice channel")
        await self.__vc.disconnect()

    async def skip(self):
        if self.__vc is None or not self.__vc.is_playing():
            raise NotPlaySound("Bot don`t play sound")
        if self.queue.is_empty():
            await self.__vc.disconnect()
            return
        self.__vc.stop()

    def get_track_play_now(self):
        return self.__now_play_track

    async def __play_loop(self):
        await self.connect()
        while not self.queue.is_empty():
            track = await self.queue.get()
            self.__now_play_track = track
            self.__next_song_event.clear()

            def after_playing(error=None):
                if error:
                    log.error(f"Playback error: {error}")
                self.__next_song_event.set()

            stream_url = await self.__api.get_stream_url(track)
            if not stream_url:
                log.error("No stream URL found for the track.")
                self.queue.task_done()
                continue
            self.__vc.play(
                FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS), after=after_playing
            )
            await self.__next_song_event.wait()
            self.queue.task_done()


class PlayerManager(ManagerSession):
    async def connect_session(self, voice_channel: disnake.VoiceChannel) -> AudioPlayer:
        if not disnake.VoiceChannel:
            raise NotConnectedVoice("Not connected to a voice channel")
        session_id = voice_channel.id
        if not self.is_session(session_id):
            new_session = AudioPlayer(voice_channel, self)
            self.create(new_session)
            session_id = new_session.session_id
        return self.get_session(session_id)


manager = PlayerManager()
