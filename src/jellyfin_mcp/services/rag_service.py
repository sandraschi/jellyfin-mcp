"""RAG service — LanceDB semantic search over Jellyfin metadata.

Dependencies (lancedb, sentence-transformers) are lazy-loaded at first use.
If they are not installed, all RAG operations raise ImportError with install instructions.
"""

import logging
from pathlib import Path


class RAGService:
    """Semantic search over Jellyfin media metadata using LanceDB + sentence-transformers."""

    def __init__(self, db_path: str | None = None):
        self._logger = logging.getLogger("rag_service")
        self._model = None
        self._db = None
        self._table = None
        self._db_path = db_path or str(Path.home() / ".jellyfin-mcp" / "rag")

    async def initialize(self):
        """Lazy-load embedding model and database.

        Raises ImportError with install instructions if optional deps are missing.
        """
        try:
            import lancedb
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError("RAG dependencies not installed. Run: pip install lancedb sentence-transformers") from exc

        if not self._model:
            self._model = await self._run_in_executor(lambda: SentenceTransformer("all-MiniLM-L6-v2"))
        Path(self._db_path).mkdir(parents=True, exist_ok=True)
        self._db = await self._run_in_executor(lambda: lancedb.connect(self._db_path))
        # Reattach existing table if present
        if self._db and self._table is None:
            try:
                self._table = await self._run_in_executor(lambda: self._db.open_table("metadata"))
            except Exception:
                pass  # Table doesn't exist yet — will be created on first sync

    async def _run_in_executor(self, func, *args):
        import asyncio

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args)

    async def sync_metadata(self, items: list[dict]) -> dict:
        """Index media items for semantic search."""
        await self.initialize()

        # Import here (initialize already checked availability)
        import pyarrow as pa
        from sentence_transformers import SentenceTransformer  # noqa: F401 (already loaded)

        documents = []
        for item in items:
            text = (
                f"{item.get('name', '')} {item.get('overview', '')} "
                + " ".join(item.get("genres", []))
                + " "
                + str(item.get("production_year", ""))
            ).strip()
            if text:
                embedding = await self._run_in_executor(self._model.encode, text)
                documents.append(
                    {
                        "item_id": item.get("id", item.get("Id", "")),
                        "name": item.get("name", ""),
                        "type": item.get("type", item.get("Type", "")),
                        "text": text,
                        "vector": embedding.tolist(),
                    }
                )

        if documents:
            table = pa.Table.from_pylist(documents)
            self._table = await self._run_in_executor(
                lambda: self._db.create_table("metadata", table, mode="overwrite")
            )

        return {"indexed": len(documents), "total": len(items)}

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        """Semantic search over indexed metadata."""
        await self.initialize()

        if not self._table:
            self._logger.warning("No RAG table — run sync first")
            return []

        query_embedding = await self._run_in_executor(self._model.encode, query)

        results = await self._run_in_executor(
            lambda: self._table.search(query_embedding.tolist()).limit(limit).to_list()
        )

        return [
            {
                "item_id": r.get("item_id"),
                "name": r.get("name"),
                "type": r.get("type"),
                "score": r.get("_distance", 0),
            }
            for r in results
        ]

    async def get_status(self) -> dict:
        """Return RAG index status."""
        await self.initialize()
        row_count = 0
        if self._table:
            row_count = await self._run_in_executor(lambda: self._table.count_rows())
        return {
            "indexed_items": row_count,
            "db_path": self._db_path,
            "model": "all-MiniLM-L6-v2",
        }

    async def purge(self) -> dict:
        """Drop the metadata table from LanceDB."""
        await self.initialize()
        if self._db:
            try:
                await self._run_in_executor(lambda: self._db.drop_table("metadata"))
            except Exception:
                pass  # Already absent
        self._table = None
        return {"purged": True, "db_path": self._db_path}
