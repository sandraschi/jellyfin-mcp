"""Media enrichment service — TMDB, Wikipedia, OMDb metadata augmentation."""

import logging

import httpx


class EnrichmentService:
    """Fetch external metadata to enrich Jellyfin media items."""

    TMDB_BASE = "https://api.themoviedb.org/3"
    WIKIPEDIA_BASE = "https://en.wikipedia.org/api/rest_v1"

    def __init__(self, tmdb_api_key: str | None = None):
        self.tmdb_api_key = tmdb_api_key
        self._logger = logging.getLogger("enrichment_service")

    async def enrich_from_tmdb(self, title: str, year: str | None = None, media_type: str = "movie") -> dict | None:
        """Fetch metadata from TMDB."""
        if not self.tmdb_api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                if media_type == "movie":
                    url = f"{self.TMDB_BASE}/search/movie"
                elif media_type in ("tv", "series"):
                    url = f"{self.TMDB_BASE}/search/tv"
                else:
                    return None

                params = {"api_key": self.tmdb_api_key, "query": title}
                if year:
                    params["year"] = year

                resp = await client.get(url, params=params)
                data = resp.json()
                results = data.get("results", [])

                if not results:
                    return None

                best = results[0]
                return {
                    "source": "tmdb",
                    "title": best.get("title") or best.get("name"),
                    "overview": best.get("overview"),
                    "rating": best.get("vote_average"),
                    "year": (best.get("release_date") or best.get("first_air_date", ""))[:4],
                    "poster": f"https://image.tmdb.org/t/p/w500{best.get('poster_path')}"
                    if best.get("poster_path")
                    else None,
                }
        except Exception as e:
            self._logger.debug("TMDB enrichment failed: %s", e)
            return None

    async def enrich_from_wikipedia(self, title: str) -> dict | None:
        """Fetch summary from Wikipedia."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.WIKIPEDIA_BASE}/page/summary/{title.replace(' ', '_')}")
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "source": "wikipedia",
                        "title": data.get("title"),
                        "summary": data.get("extract", "")[:500],
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
                        "thumbnail": data.get("thumbnail", {}).get("source"),
                    }
        except Exception as e:
            self._logger.debug("Wikipedia enrichment failed: %s", e)
        return None

    async def enrich(self, title: str, year: str | None = None, media_type: str = "movie") -> list[dict]:
        """Run all enrichment sources and return results."""
        results = []
        tmdb = await self.enrich_from_tmdb(title, year, media_type)
        if tmdb:
            results.append(tmdb)
        wiki = await self.enrich_from_wikipedia(title)
        if wiki:
            results.append(wiki)
        return results
