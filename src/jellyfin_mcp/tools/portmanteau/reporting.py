"""jellyfin-mcp Reporting & Analytics Portmanteau Tool."""

from collections import Counter
from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_reporting(
    operation: Annotated[
        Literal["stats", "popular", "recent", "genres", "resolution", "codec", "user_activity", "export"],
        Field(description="Reporting operation to perform."),
    ],
    library_id: Annotated[str | None, Field(description="Library ID to scope the report.")] = None,
    days: Annotated[int | None, Field(description="Lookback window in days (e.g. 30).")] = 30,
    limit: Annotated[int | None, Field(description="Max results (default: 20).")] = 20,
    user_id: Annotated[str | None, Field(description="User ID for activity reports.")] = None,
    format: Annotated[str | None, Field(description="Export format: 'json' or 'csv'.")] = None,
) -> dict[str, Any]:
    """Library reporting and analytics for Jellyfin.

    Consolidates all reporting operations into a single portmanteau interface:
    stats, popular items, recently added, genre distribution, resolution breakdown,
    codec usage, user activity, and report export.

    [PORTMANTEAU] Prevents tool explosion by merging 8 reporting operations into one tool.

    ## Return Format
    {"success": bool, "operation": str, "data": [...], "count": int, "message": str}

    ## Examples
    - jellyfin_reporting(operation="stats")
    - jellyfin_reporting(operation="popular", limit=10)
    - jellyfin_reporting(operation="genres", library_id="abc123")
    - jellyfin_reporting(operation="user_activity", user_id="user123")
    - jellyfin_reporting(operation="export", format="csv")
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "stats":
            # /Items/Counts returns per-type totals, optionally scoped to a library
            params: dict[str, Any] = {}
            if library_id:
                params["ParentId"] = library_id
            counts = await jf._get("/Items/Counts", **params)
            return {
                "success": True,
                "operation": "stats",
                "message": "Library statistics",
                "data": {
                    "library_id": library_id,
                    "movies": counts.get("MovieCount", 0),
                    "series": counts.get("SeriesCount", 0),
                    "episodes": counts.get("EpisodeCount", 0),
                    "music_artists": counts.get("ArtistCount", 0),
                    "albums": counts.get("AlbumCount", 0),
                    "songs": counts.get("SongCount", 0),
                    "books": counts.get("BookCount", 0),
                },
            }

        if operation == "popular":
            uid = user_id or await jf.get_default_user_id()
            params = {
                "SortBy": "PlayCount",
                "SortOrder": "Descending",
                "Limit": limit or 20,
                "Recursive": "true",
                "Filters": "IsPlayed",
            }
            if library_id:
                params["ParentId"] = library_id
            raw = await jf._get(f"/Users/{uid}/Items", **params)
            items = raw.get("Items", []) if isinstance(raw, dict) else []
            return {
                "success": True,
                "operation": "popular",
                "message": f"Top {len(items)} most-played items",
                "data": items,
                "count": len(items),
            }

        if operation == "recent":
            uid = user_id or await jf.get_default_user_id()
            params = {"Limit": limit or 20}
            if library_id:
                params["ParentId"] = library_id
            items = await jf._get(f"/Users/{uid}/Items/Latest", **params)
            if not isinstance(items, list):
                items = items.get("Items", []) if isinstance(items, dict) else []
            return {
                "success": True,
                "operation": "recent",
                "message": f"{len(items)} recently added items",
                "data": items,
                "count": len(items),
            }

        if operation == "genres":
            params = {}
            if library_id:
                params["ParentId"] = library_id
            raw = await jf._get("/Genres", **params)
            genres = raw.get("Items", []) if isinstance(raw, dict) else []
            return {
                "success": True,
                "operation": "genres",
                "message": f"{len(genres)} genres in library",
                "data": [{"name": g.get("Name"), "id": g.get("Id")} for g in genres],
                "count": len(genres),
                "library_id": library_id,
            }

        if operation == "resolution":
            params = {
                "Fields": "MediaStreams",
                "Recursive": "true",
                "IncludeItemTypes": "Movie,Episode",
                "Limit": 5000,
            }
            if library_id:
                params["ParentId"] = library_id
            raw = await jf._get("/Items", **params)
            items = raw.get("Items", []) if isinstance(raw, dict) else []
            buckets: Counter = Counter()
            for item in items:
                for stream in item.get("MediaStreams", []):
                    if stream.get("Type") == "Video":
                        width = stream.get("Width", 0) or 0
                        if width >= 3840:
                            buckets["4K"] += 1
                        elif width >= 1920:
                            buckets["1080p"] += 1
                        elif width >= 1280:
                            buckets["720p"] += 1
                        else:
                            buckets["SD"] += 1
                        break  # one video stream per item is enough
            return {
                "success": True,
                "operation": "resolution",
                "message": f"Resolution breakdown across {len(items)} items",
                "data": dict(buckets),
                "total_items": len(items),
            }

        if operation == "codec":
            params = {
                "Fields": "MediaStreams",
                "Recursive": "true",
                "IncludeItemTypes": "Movie,Episode",
                "Limit": 5000,
            }
            if library_id:
                params["ParentId"] = library_id
            raw = await jf._get("/Items", **params)
            items = raw.get("Items", []) if isinstance(raw, dict) else []
            video_codecs: Counter = Counter()
            audio_codecs: Counter = Counter()
            for item in items:
                for stream in item.get("MediaStreams", []):
                    codec = (stream.get("Codec") or "unknown").lower()
                    if stream.get("Type") == "Video":
                        video_codecs[codec] += 1
                    elif stream.get("Type") == "Audio":
                        audio_codecs[codec] += 1
            return {
                "success": True,
                "operation": "codec",
                "message": f"Codec breakdown across {len(items)} items",
                "data": {"video": dict(video_codecs), "audio": dict(audio_codecs)},
                "total_items": len(items),
            }

        if operation == "user_activity":
            uid = user_id or await jf.get_default_user_id()
            raw = await jf._get("/System/ActivityLog/Entries", Limit=limit or 50, UserId=uid)
            entries = raw.get("Items", []) if isinstance(raw, dict) else []
            return {
                "success": True,
                "operation": "user_activity",
                "message": f"{len(entries)} activity log entries for user",
                "data": entries,
                "count": len(entries),
                "user_id": uid,
            }

        if operation == "export":
            if not format:
                return {"success": False, "error": "format is required for export", "error_code": "MISSING_FORMAT"}
            if format not in ("json", "csv"):
                return {
                    "success": False,
                    "error": f"Unsupported format '{format}'. Use: json, csv",
                    "error_code": "INVALID_FORMAT",
                }
            counts = await jf._get("/Items/Counts")
            genres_raw = await jf._get("/Genres")
            genre_names = [g.get("Name") for g in (genres_raw.get("Items", []) if isinstance(genres_raw, dict) else [])]
            report = {"library_id": library_id, "counts": counts, "genres": genre_names}
            if format == "csv":
                lines = ["metric,value"]
                for k, v in counts.items():
                    lines.append(f"{k},{v}")
                return {"success": True, "operation": "export", "format": format, "data": "\n".join(lines)}
            return {"success": True, "operation": "export", "format": format, "data": report}

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Valid operations: stats, popular, recent, genres, resolution, codec, user_activity, export"],
        }

    except Exception as e:
        logger.exception("Error in jellyfin_reporting operation '%s':", operation)
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}
