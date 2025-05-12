from .schemas import SongDTO
from disnake import Embed


async def song_embed(song: SongDTO) -> Embed:
    time=song.duration // 1000
    embed = Embed(
        title=song.title,
        description=f"{(time // 60):02}:{(time % 60):02}",
        url=song.permalink_url,
    )
    embed.set_thumbnail(url=song.artwork_url)
    embed.set_author(
        name=song.user.username,
        url=song.user.permalink_url,
        icon_url=song.user.avatar_url,
    )
    return embed
