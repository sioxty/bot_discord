from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# === USER MODELS ===


@dataclass
class CreatorProduct:
    id: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CreatorProduct":
        return CreatorProduct(id=data.get("id", ""))


@dataclass
class CreatorSubscription:
    product: CreatorProduct

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CreatorSubscription":
        return CreatorSubscription(
            product=CreatorProduct.from_dict(data.get("product", {}))
        )


@dataclass
class VisualEntry:
    urn: str
    entry_time: int
    visual_url: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "VisualEntry":
        return VisualEntry(
            urn=data.get("urn", ""),
            entry_time=data.get("entry_time", 0),
            visual_url=data.get("visual_url", ""),
        )


@dataclass
class Visuals:
    urn: str
    enabled: bool
    visuals: List[VisualEntry]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Visuals":
        return Visuals(
            urn=data.get("urn", ""),
            enabled=data.get("enabled", False),
            visuals=[VisualEntry.from_dict(v) for v in data.get("visuals", [])],
        )


@dataclass
class ExtendedBadges:
    pro: bool
    creator_mid_tier: bool
    pro_unlimited: bool
    verified: bool

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExtendedBadges":
        return ExtendedBadges(
            pro=data.get("pro", False),
            creator_mid_tier=data.get("creator_mid_tier", False),
            pro_unlimited=data.get("pro_unlimited", False),
            verified=data.get("verified", False),
        )


@dataclass
class User:
    id: int
    username: str
    full_name: str
    first_name: str
    last_name: str
    avatar_url: str
    permalink: str
    permalink_url: str
    created_at: str
    last_modified: str
    uri: str
    urn: str
    city: Optional[str]
    country_code: Optional[str]
    description: Optional[str]
    followers_count: int
    followings_count: int
    likes_count: int
    playlist_likes_count: int
    playlist_count: int
    track_count: int
    reposts_count: Optional[int]
    comments_count: int
    station_urn: str
    station_permalink: str
    verified: bool
    badges: ExtendedBadges
    creator_subscription: Optional[CreatorSubscription] = None
    creator_subscriptions: List[CreatorSubscription] = field(default_factory=list)
    visuals: Optional[Visuals] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "User":
        return User(
            id=data["id"],
            username=data.get("username", ""),
            full_name=data.get("full_name", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            avatar_url=data.get("avatar_url", ""),
            permalink=data.get("permalink", ""),
            permalink_url=data.get("permalink_url", ""),
            created_at=data.get("created_at", ""),
            last_modified=data.get("last_modified", ""),
            uri=data.get("uri", ""),
            urn=data.get("urn", ""),
            city=data.get("city"),
            country_code=data.get("country_code"),
            description=data.get("description"),
            followers_count=data.get("followers_count", 0),
            followings_count=data.get("followings_count", 0),
            likes_count=data.get("likes_count", 0),
            playlist_likes_count=data.get("playlist_likes_count", 0),
            playlist_count=data.get("playlist_count", 0),
            track_count=data.get("track_count", 0),
            reposts_count=data.get("reposts_count"),
            comments_count=data.get("comments_count", 0),
            station_urn=data.get("station_urn", ""),
            station_permalink=data.get("station_permalink", ""),
            verified=data.get("verified", False),
            badges=ExtendedBadges.from_dict(data.get("badges", {})),
            creator_subscription=(
                CreatorSubscription.from_dict(data.get("creator_subscription", {}))
                if data.get("creator_subscription")
                else None
            ),
            creator_subscriptions=[
                CreatorSubscription.from_dict(cs["product"])
                for cs in data.get("creator_subscriptions", [])
                if "product" in cs
            ],
            visuals=(
                Visuals.from_dict(data.get("visuals", {}))
                if data.get("visuals")
                else None
            ),
        )


# === TRACK MODEL ===


@dataclass
class Transcoding:
    duration: int
    format_mime_type: str
    format_protocol: str
    is_legacy_transcoding: bool
    preset: str
    quality: str
    snipped: bool
    url: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Transcoding":
        fmt = data.get("format", {})
        return Transcoding(
            duration=data.get("duration", 0),
            format_mime_type=fmt.get("mime_type", ""),
            format_protocol=fmt.get("protocol", ""),
            is_legacy_transcoding=data.get("is_legacy_transcoding", False),
            preset=data.get("preset", ""),
            quality=data.get("quality", ""),
            snipped=data.get("snipped", False),
            url=data.get("url", ""),
        )


@dataclass
class Track:
    id: int
    title: str
    permalink: str
    permalink_url: str
    description: Optional[str]
    genre: Optional[str]
    duration: int
    full_duration: int
    commentable: bool
    comment_count: int
    playback_count: int
    likes_count: int
    reposts_count: int
    download_count: int
    downloadable: bool
    has_downloads_left: bool
    created_at: str
    last_modified: str
    display_date: str
    artwork_url: Optional[str]
    license: str
    embeddable_by: str
    monetization_model: str
    sharing: str
    state: str
    streamable: bool
    tag_list: Optional[str]
    track_authorization: str
    uri: str
    urn: str
    waveform_url: Optional[str]
    publisher_metadata: Dict[str, Any]
    media: List[Transcoding]
    user: User

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Track":
        return Track(
            id=data.get("id"),
            title=data.get("title", ""),
            permalink=data.get("permalink", ""),
            permalink_url=data.get("permalink_url", ""),
            description=data.get("description"),
            genre=data.get("genre"),
            duration=data.get("duration", 0),
            full_duration=data.get("full_duration", 0),
            commentable=data.get("commentable", False),
            comment_count=data.get("comment_count", 0),
            playback_count=data.get("playback_count", 0),
            likes_count=data.get("likes_count", 0),
            reposts_count=data.get("reposts_count", 0),
            download_count=data.get("download_count", 0),
            downloadable=data.get("downloadable", False),
            has_downloads_left=data.get("has_downloads_left", False),
            created_at=data.get("created_at", ""),
            last_modified=data.get("last_modified", ""),
            display_date=data.get("display_date", ""),
            artwork_url=data.get("artwork_url"),
            license=data.get("license", ""),
            embeddable_by=data.get("embeddable_by", ""),
            monetization_model=data.get("monetization_model", ""),
            sharing=data.get("sharing", ""),
            state=data.get("state", ""),
            streamable=data.get("streamable", False),
            tag_list=data.get("tag_list"),
            track_authorization=data.get("track_authorization", ""),
            uri=data.get("uri", ""),
            urn=data.get("urn", ""),
            waveform_url=data.get("waveform_url"),
            publisher_metadata=data.get("publisher_metadata", {}),
            media=[
                Transcoding.from_dict(t)
                for t in data.get("media", {}).get("transcodings", [])
            ],
            user=User.from_dict(data.get("user", {})),
        )
