"""
aiosoundcloud

A Python library for interacting with the SoundCloud API asynchronously.

Modules:
    soundcloud_client (module): Contains the `SoundCloudClient` class for interacting with SoundCloud.
    soundcloud_client_dto (module): Contains the `SoundCloud` data transfer object.
    utils (module): Provides utility functions, such as `get_client_id`.
"""

__version__ = "0.2.0"
__author__ = "Sioxty"
__license__ = "MIT"

from .soundcloud_client import SoundCloudClient
from .soundcloud_client_dto import SoundCloud
from .utils import get_client_id
