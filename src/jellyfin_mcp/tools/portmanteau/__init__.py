"""
jellyfin-mcp Portmanteau Tools Package.

Consolidates related operations into single, user-friendly interfaces.
Each tool uses an `operation` parameter with Literal types.
"""

from .arr_stack import jellyfin_arr_stack
from .collections import jellyfin_collections
from .enrichment import jellyfin_enrichment
from .ffmpeg import jellyfin_ffmpeg
from .help import jellyfin_help
from .integration import jellyfin_integration
from .library import jellyfin_library
from .livetv import jellyfin_livetv
from .media import jellyfin_media
from .metadata import jellyfin_metadata
from .playback import jellyfin_playback
from .playlist import jellyfin_playlist
from .plugin import jellyfin_plugin
from .rag import jellyfin_rag
from .recommend import jellyfin_recommend
from .reporting import jellyfin_reporting
from .search import jellyfin_search
from .server import jellyfin_server
from .streaming import jellyfin_streaming
from .subtitle import jellyfin_subtitle
from .user import jellyfin_user

__all__ = [
    "jellyfin_arr_stack",
    "jellyfin_collections",
    "jellyfin_enrichment",
    "jellyfin_ffmpeg",
    "jellyfin_help",
    "jellyfin_integration",
    "jellyfin_library",
    "jellyfin_livetv",
    "jellyfin_media",
    "jellyfin_metadata",
    "jellyfin_playback",
    "jellyfin_playlist",
    "jellyfin_plugin",
    "jellyfin_rag",
    "jellyfin_recommend",
    "jellyfin_reporting",
    "jellyfin_search",
    "jellyfin_server",
    "jellyfin_streaming",
    "jellyfin_subtitle",
    "jellyfin_user",
]
