import logging
from asyncio import Queue, Event, create_task

import disnake
from aiosoundcloud import SoundCloud
from aiosoundcloud.schemas import Track
from disnake import FFmpegPCMAudio, VoiceClient

from config import LIMIT_QUEUE

from .exception import LimitQueue, NotConnectedVoice, NotPlaySound

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


class AudioPlayerSession:
    def __init__(self, voice_channel: disnake.VoiceChannel, api: SoundCloud) -> None:
        self._voice_channel = voice_channel
        self.queue = TrackQueue(limit=LIMIT_QUEUE)
        self.__next_song_event = Event()
        self._now_play_track: Track | None = None
        self.api = api
        self._vc: VoiceClient | None = None

    def __repr__(self) -> str:
        return f"<AudioPlayerSession voice_channel={self._voice_channel.id}>"

    async def play(self, *tracks: Track):
        if tracks:
            for track in tracks[: self.queue.LIMIT_QUEUE - self.queue.size()]:
                await self.queue.add(track)

        if not self._vc:  # Not connected to a voice channel
            create_task(self.__play())

    async def connect(self):
        if self._vc is None or not self._vc.is_connected():
            self._vc = await self._voice_channel.connect()

    async def __play(self):
        await self.__play_loop()
        await self._vc.disconnect()
        self._vc = None

    async def stop(self):
        if not self._vc or not self._vc.is_connected():
            raise NotConnectedVoice("Not connected to a voice channel")
        await self._vc.disconnect()

    async def skip(self):
        if self._vc is None or not self._vc.is_playing():
            raise NotPlaySound("Bot don`t play sound")
        if self.queue.is_empty():
            await self._vc.disconnect()
            return
        self._vc.stop()

    def get_track_play_now(self):
        return self._now_play_track

    async def __play_loop(self):
        await self.connect()
        while not self.queue.is_empty():
            track = await self.queue.get()
            self._now_play_track = track
            self.__next_song_event.clear()

            def after_playing(error=None):
                if error:
                    log.error(f"Playback error: {error}")
                self.__next_song_event.set()

            stream_url = await self.api.get_stream_url(track)
            self._vc.play(
                FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS), after=after_playing
            )
            await self.__next_song_event.wait()
            self.queue.task_done()


class ManagementSession:
    def __init__(self, api) -> None:
        self.sessions: list[AudioPlayerSession] = []
        self.api: SoundCloud = api

    async def get_session(
        self, voice_channel: disnake.VoiceChannel
    ) -> AudioPlayerSession:
        if not disnake.VoiceChannel:
            raise NotConnectedVoice("Not connected to a voice channel")
        for session in self.sessions:
            if session._voice_channel.id == voice_channel.id:
                return session
        new_session = AudioPlayerSession(voice_channel, self.api)
        self.sessions.append(new_session)
        log.info(f"Created new session {new_session}")
        return new_session

    def is_session(self, voice_channel: disnake.VoiceChannel):
        return voice_channel.id in self.sessions

    async def close(self, session):
        log.info(f"Closing session {session}")
        self.sessions.remove(session)
