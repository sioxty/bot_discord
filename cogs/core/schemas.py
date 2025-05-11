from dataclasses import dataclass,field

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class FormatDTO:
    protocol: str
    mime_type: str

@dataclass
class TranscodingDTO:
    url: str
    preset: str
    duration: int
    snipped: bool
    format: FormatDTO
    quality: str
    is_legacy_transcoding: bool

@dataclass
class PublisherMetadataDTO:
    id: Optional[int] = None
    urn: Optional[str] = None
    artist: Optional[str] = None  # Поле необов'язкове
    explicit: Optional[bool] = None
    contains_music: Optional[bool] = None

@dataclass
class BadgesDTO:
    pro: bool
    pro_unlimited: bool
    creator_mid_tier: bool
    verified: bool

@dataclass
class VisualEntryDTO:
    urn: str
    entry_time: int
    visual_url: str

@dataclass
class VisualsDTO:
    urn: str
    enabled: bool
    visuals: List[VisualEntryDTO]

@dataclass
class UserDTO:
    id: int
    username: str
    permalink: str
    permalink_url: str
    avatar_url: Optional[str]
    city: Optional[str]
    country_code: Optional[str]
    created_at: datetime
    description: Optional[str]
    followers_count: int
    followings_count: int
    likes_count: int
    playlist_count: int
    playlist_likes_count: int
    reposts_count: Optional[int]
    track_count: int
    uri: str
    urn: str
    verified: bool
    badges: BadgesDTO
    visuals: Optional[VisualsDTO]

@dataclass
class SongDTO:
    id: int
    title: str
    permalink: str
    permalink_url: str
    description: Optional[str]
    genre: Optional[str]
    duration: int
    full_duration: int
    streamable: bool
    downloadable: bool
    download_count: int
    playback_count: int
    likes_count: int
    reposts_count: int
    comment_count: int
    commentable: bool
    sharing: str
    state: str
    created_at: datetime
    release_date: Optional[datetime]
    last_modified: datetime
    artwork_url: Optional[str]
    waveform_url: Optional[str]
    license: str
    embeddable_by: str
    tag_list: str
    uri: str
    urn: str
    kind: str
    public: bool
    station_urn: Optional[str]
    station_permalink: Optional[str]
    display_date: datetime
    monetization_model: Optional[str]
    policy: Optional[str]
    purchase_title: Optional[str]
    purchase_url: Optional[str]
    secret_token: Optional[str]
    track_authorization: str
    publisher_metadata: Optional[PublisherMetadataDTO]
    user: UserDTO
    steame_url: str
    
from datetime import datetime

def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if value:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return None

def song_dto_from_dict(**data: dict) -> SongDTO:
    publisher_metadata = None
    if "publisher_metadata" in data and data["publisher_metadata"]:
        
        
        publisher_metadata = PublisherMetadataDTO(**data["publisher_metadata"])

    visuals = None
    if "user" in data and "visuals" in data["user"] and data["user"]["visuals"]:
        visuals_data = data["user"]["visuals"]
        visuals = VisualsDTO(
            urn=visuals_data["urn"],
            enabled=visuals_data["enabled"],
            visuals=[
                VisualEntryDTO(**v) for v in visuals_data.get("visuals", [])
            ]
        )

    badges = BadgesDTO(**data["user"]["badges"])

    user = UserDTO(
        id=data["user"]["id"],
        username=data["user"]["username"],
        permalink=data["user"]["permalink"],
        permalink_url=data["user"]["permalink_url"],
        avatar_url=data["user"].get("avatar_url"),
        city=data["user"].get("city"),
        country_code=data["user"].get("country_code"),
        created_at=parse_datetime(data["user"]["created_at"]),
        description=data["user"].get("description"),
        followers_count=data["user"]["followers_count"],
        followings_count=data["user"]["followings_count"],
        likes_count=data["user"]["likes_count"],
        playlist_count=data["user"]["playlist_count"],
        playlist_likes_count=data["user"]["playlist_likes_count"],
        reposts_count=data["user"].get("reposts_count"),
        track_count=data["user"]["track_count"],
        uri=data["user"]["uri"],
        urn=data["user"]["urn"],
        verified=data["user"]["verified"],
        badges=badges,
        visuals=visuals
    )

    return SongDTO(
        id=data["id"],
        title=data["title"],
        permalink=data["permalink"],
        permalink_url=data["permalink_url"],
        description=data.get("description"),
        genre=data.get("genre"),
        duration=data["duration"],
        full_duration=data["full_duration"],
        streamable=data["streamable"],
        downloadable=data["downloadable"],
        download_count=data["download_count"],
        playback_count=data["playback_count"],
        likes_count=data["likes_count"],
        reposts_count=data["reposts_count"],
        comment_count=data["comment_count"],
        commentable=data["commentable"],
        sharing=data["sharing"],
        state=data["state"],
        created_at=parse_datetime(data["created_at"]),
        release_date=parse_datetime(data.get("release_date")),
        last_modified=parse_datetime(data["last_modified"]),
        artwork_url=data.get("artwork_url"),
        waveform_url=data.get("waveform_url"),
        license=data["license"],
        embeddable_by=data["embeddable_by"],
        tag_list=data["tag_list"],
        uri=data["uri"],
        urn=data["urn"],
        kind=data["kind"],
        public=data["public"],
        station_urn=data.get("station_urn"),
        station_permalink=data.get("station_permalink"),
        display_date=parse_datetime(data["display_date"]),
        monetization_model=data.get("monetization_model"),
        policy=data.get("policy"),
        purchase_title=data.get("purchase_title"),
        purchase_url=data.get("purchase_url"),
        secret_token=data.get("secret_token"),
        track_authorization=data["track_authorization"],
        publisher_metadata=publisher_metadata,
        user=user,
        steame_url=data["stream_url"]
    )

