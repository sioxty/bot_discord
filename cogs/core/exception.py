class BaseBotException(Exception):
    """Base exception for the bot."""


class LimitQueue(BaseBotException):
    """Exception raised when the queue is full."""

    pass


class NotConnectedVoice(BaseBotException):
    """Exception raised when the bot is not connected to a voice channel."""

    pass


class NotConnectedUser(BaseBotException):
    """Exception raised when the user is not connected to a voice channel."""

    pass


class NotPlaySound(BaseBotException):
    pass
