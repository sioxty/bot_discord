
class NotFoundSong(Exception):
    """Exception raised when a video is not found."""
    pass

class NotFoundPlaylist(Exception):
    """Exception raised when a playlist is not found."""
    pass

class LimitQueue(Exception):
    """Exception raised when the queue is full."""
    pass