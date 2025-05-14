

class LimitQueue(Exception):
    """Exception raised when the queue is full."""
    pass

class NotConnectedVoice(Exception):
    """Exception raised when the bot is not connected to a voice channel."""
    pass

class NotConnectedUser(Exception):
    """Exception raised when the user is not connected to a voice channel."""
    pass
