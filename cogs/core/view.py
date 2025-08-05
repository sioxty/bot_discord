from aiosoundcloud.schemas import Track, Playlist
from disnake import Embed


async def track_embed(track: Track) -> Embed:
    time = track.duration // 1000
    embed = Embed(
        title=track.title,
        description=f"{(time // 60):02}:{(time % 60):02}",
        url=track.permalink_url,
    )
    embed.set_thumbnail(url=track.artwork_url)
    embed.set_author(
        name=track.user.username,
        url=track.user.permalink_url,
        icon_url=track.user.avatar_url,
    )
    return embed


async def playlist_embed(playlist: Playlist) -> Embed:
    embed = Embed(
        title=playlist.title,
        description=track_list_embed(playlist.tracks),
        url=playlist.permalink_url,
    )
    embed.set_thumbnail(url=playlist.artwork_url or "")
    embed.set_author(
        name=playlist.user.username,
        url=playlist.user.permalink_url,
        icon_url=playlist.user.avatar_url,
    )

    return embed


def queue_embed(*track: Track) -> Embed:
    embed = Embed(
        title="Current Queue",
        description=(
            f"play now: [{track[0].title} - {track[0].user.username  }]({track[0].permalink_url})\n\n"
            + track_list_embed(track[1:])
        )[
            :4096
        ],  # Discord limit
    )
    return embed


def track_list_embed(tracks: list[Track]) -> str:
    return "\n".join(
        f"{i}. [{track.title} - {track.user.username}]({track.permalink_url})"
        for i, track in enumerate(tracks, 1)
    )[:4096]
