"""Wikipedia enrichment: descriptive User-Agent and visible failures.

Wikimedia's User-Agent policy returns 403 for missing or generic UAs
(including httpx's default ``python-httpx/x.y``).
"""

from __future__ import annotations

import httpx
import respx

from jellyfin_mcp.services.enrichment_service import EnrichmentService

SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/Breaking_Bad"
REPO_URL = "https://github.com/sandraschi/jellyfin-mcp"


@respx.mock
async def test_wikipedia_request_sends_descriptive_user_agent():
    route = respx.get(SUMMARY_URL).mock(
        return_value=httpx.Response(200, json={"title": "Breaking Bad", "extract": "A TV series."})
    )

    result = await EnrichmentService().enrich_from_wikipedia("Breaking Bad")

    assert route.called
    user_agent = route.calls.last.request.headers["user-agent"]
    assert not user_agent.startswith("python-httpx")
    assert REPO_URL in user_agent
    assert result is not None
    assert result["title"] == "Breaking Bad"
    assert "error" not in result


@respx.mock
async def test_wikipedia_403_is_reported_not_swallowed(caplog):
    respx.get(SUMMARY_URL).mock(return_value=httpx.Response(403, text="Please set a user-agent"))

    with caplog.at_level("WARNING", logger="enrichment_service"):
        result = await EnrichmentService().enrich_from_wikipedia("Breaking Bad")

    assert result is not None
    assert result["source"] == "wikipedia"
    assert result["status_code"] == 403
    assert "403" in result["error"]
    assert any(r.levelname == "WARNING" and "403" in r.getMessage() for r in caplog.records)


@respx.mock
async def test_wikipedia_network_error_is_reported(caplog):
    respx.get(SUMMARY_URL).mock(side_effect=httpx.ConnectError("boom"))

    with caplog.at_level("WARNING", logger="enrichment_service"):
        result = await EnrichmentService().enrich_from_wikipedia("Breaking Bad")

    assert result is not None
    assert "boom" in result["error"]
    assert any(r.levelname == "WARNING" for r in caplog.records)
