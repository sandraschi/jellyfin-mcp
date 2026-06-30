"""Prefab card builders for jellyfin-mcp using prefab_ui."""

from prefab_ui import Badge, Card, DataTable, Grid, Metric, Row


def build_library_grid(libraries: list[dict]) -> Grid:
    """Build a grid of library cards with metrics."""
    cards = []
    for lib in libraries:
        cards.append(
            Card(
                children=[
                    Metric(label="Type", value=lib.get("collection_type", "unknown").title()),
                    Metric(label="Items", value=str(lib.get("item_count", 0))),
                ],
                title=lib.get("name", "Unknown"),
            )
        )
    return Grid(children=cards, columns=3)


def build_library_detail(library: dict) -> Grid:
    """Build a detailed library view."""
    badges = []
    if library.get("collection_type"):
        badges.append(Badge(label=library["collection_type"].title()))
    return Grid(
        children=[
            Metric(label="Items", value=str(library.get("item_count", 0))),
            Metric(label="Locations", value=str(len(library.get("locations", [])))),
            Metric(label="Type", value=library.get("collection_type", "unknown").title()),
        ],
        columns=3,
    )


def build_media_browser(items: list[dict], title: str = "Media") -> Grid:
    """Build a responsive media grid with poster cards."""
    cards = []
    for item in items[:24]:
        year = str(item.get("production_year", "")) if item.get("production_year") else ""
        cards.append(
            Card(
                children=[
                    Metric(label="Year", value=year) if year else None,
                    Metric(label="Type", value=item.get("type", "Unknown").title()),
                ],
                title=item.get("name", "Unknown"),
            )
        )
    return Grid(children=cards, columns=4)


def build_media_detail(item: dict) -> Grid:
    """Build a detailed media item view."""
    badges = []
    for genre in item.get("genres", [])[:4]:
        badges.append(Badge(label=genre))
    return Grid(
        children=[
            Metric(label="Year", value=str(item.get("production_year", "N/A"))),
            Metric(label="Rating", value=item.get("community_rating", "N/A")),
            Metric(label="Runtime", value=f"{item.get('run_time_ticks', 0) // 600000000} min"),
            Row(children=badges) if badges else None,
        ],
        columns=3,
    )


def build_server_status(status: dict) -> Grid:
    """Build a server status dashboard."""
    return Grid(
        children=[
            Metric(label="Version", value=status.get("version", "Unknown")),
            Metric(label="OS", value=status.get("operating_system", "Unknown")),
            Metric(label="Uptime", value=status.get("uptime", "Unknown")),
            Metric(label="Cache", value=status.get("cache_path", "")[:30]),
        ],
        columns=2,
    )


def build_streaming_session(sessions: list[dict]) -> DataTable:
    """Build a data table of active streaming sessions."""
    headers = ["User", "Media", "State", "Method", "Progress"]
    rows = []
    for s in sessions:
        rows.append(
            [
                s.get("user_name", "Unknown"),
                s.get("now_playing_item", {}).get("name", "Unknown")[:40],
                s.get("play_state", {}).get("play_method", "Unknown"),
                s.get("play_state", {}).get("method", ""),
                s.get("play_state", {}).get("position_ticks", ""),
            ]
        )
    return DataTable(headers=headers, rows=rows)


def build_plugin_catalog(plugins: list[dict]) -> Grid:
    """Build a plugin catalog grid."""
    cards = []
    for p in plugins:
        cards.append(
            Card(
                children=[
                    Metric(label="Version", value=p.get("version", "?")),
                    Metric(label="Status", value=p.get("status", "inactive")),
                ],
                title=p.get("name", p.get("id", "Unknown")),
            )
        )
    return Grid(children=cards, columns=3)


def build_transcode_monitor(jobs: list[dict]) -> DataTable:
    """Build a transcode queue monitor."""
    headers = ["Media", "Progress", "FPS", "Speed", "GPU"]
    rows = []
    for j in jobs:
        rows.append(
            [
                j.get("item", {}).get("name", "Unknown")[:40],
                f"{j.get('progress', 0):.1f}%",
                str(j.get("framerate", 0)),
                f"{j.get('speed', 0):.1f}x",
                j.get("hardware_accel", "CPU"),
            ]
        )
    return DataTable(headers=headers, rows=rows)
