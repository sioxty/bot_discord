from .schemas import SongDTO
from disnake import Embed
import io

import aiohttp
import disnake
from PIL import Image


async def song_embed(song: SongDTO) -> Embed:
    embed = Embed(
        title=song.title,
        description=f"{await __author(song.artists)}" + "\n" + await __duration(song.duration),
    )
    return embed


async def __duration(duration: int) -> str:
    if duration > 3600:
        return f"{duration // 3600}:{(duration % 3600) // 60:02d}:{duration % 60:02d}"
    return f"{duration // 60}:{duration % 60:02d}"


async def __author(artists: list[str]) -> str:
    s = ""
    for author in artists:
        s += f"{author}, "
    return s[:-2]


async def get_preview(image_url) -> disnake.File:
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                raise ValueError(f"Не вдалося завантажити прев’ю: {resp.status}")
            data = await resp.read()
    img = Image.open(io.BytesIO(data))
    if not img.format:
        raise ValueError("Не вдалося визначити формат зображення.")
    width, height = img.size
    side = min(width, height)

    left = (width - side) // 2
    top = (height - side) // 2
    right = left + side
    bottom = top + side

    img = img.crop((left, top, right, bottom))

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)

    return disnake.File(buffer, filename='preview.jpg')
