from dataclasses import dataclass,field



@dataclass
class SongDTO:
    title: str
    webpage_url: str
    url: str
    thumbnail: str
    duration: int
    uploader: str
    artists: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.artists:
            self.artists = [self.uploader]

def create_SongDTO(info: dict)->SongDTO:
    song_data = {key: info[key] for key in SongDTO.__annotations__.keys() if key in info}
    return SongDTO(**song_data)