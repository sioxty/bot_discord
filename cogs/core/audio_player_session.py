import logging
from asyncio import Queue, Event, create_task

import disnake
from disnake import FFmpegPCMAudio

from .schemas import SongDTO

log = logging.getLogger(__name__)

FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-nostdin '
        '-loglevel warning '
    ),
    'options': (
        '-vn '
        '-f s16le '
    )
}


class AudioPlayerSession:
    def __init__(self, voice_channel: disnake.VoiceChannel) -> None:
        self.LIMIT_QUEUE = 25
        self.voice_channel = voice_channel
        self.queue: Queue[SongDTO] = Queue(maxsize=self.LIMIT_QUEUE)
        self.next_song_event = Event()
        self._is_playing_loop = False
        self.vc = None

    def __repr__(self) -> str:
        return f"<AudioPlayerSession voice_channel={self.voice_channel.id}>"

    async def add_song(self, song: SongDTO):
        await self.queue.put(song)
        log.info(f"Added {song.title} to queue.")
        if not self.vc or not self.vc.is_playing():
            create_task(self.play())

    async def connect(self):
        if self.vc is None or not self.vc.is_connected():
            self.vc = await self.voice_channel.connect()

    async def play(self):
        await self.connect()

        # Якщо вже щось грає – не запускаємо ще раз
        if self.vc.is_playing() or self.next_song_event.is_set():
            return

        while not self.queue.empty():
            song = await self.queue.get()
            log.info(f"🎵 Playing {song.title}")
            self.next_song_event.clear()

            def after_playing(error=None):
                if error:
                    log.error(f"Playback error: {error}")
                self.next_song_event.set()

            self.vc.play(FFmpegPCMAudio(song.url, **FFMPEG_OPTIONS), after=after_playing)
            await self.next_song_event.wait()
            self.queue.task_done()

        await self.vc.disconnect()
        self._is_playing_loop = False


class ManagementSession:
    def __init__(self) -> None:
        self.sessions: list[AudioPlayerSession] = []

    async def get_session(self, voice_channel: disnake.VoiceChannel) -> AudioPlayerSession:
        for session in self.sessions:
            if session.voice_channel.id == voice_channel.id:
                return session
        new_session = AudioPlayerSession(voice_channel)
        self.sessions.append(new_session)
        log.info(f"Created new session {new_session}")
        return new_session

    async def close(self, session):
        log.info(f"Closing session {session}")
        self.sessions.remove(session)
