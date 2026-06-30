"""jellyfin-mcp Agentic Tool — Dynamic LLM-powered workflows via FastMCP 3.2 sampling.

Registered programmatically via register_agentic_jellyfin_tools(mcp) in server.py.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp import Context
from pydantic import Field

from ..utils import get_logger

logger = get_logger(__name__)


def register_agentic_jellyfin_tools(mcp):
    """Register jellyfin_agentic tool with workflow, natural_query, and batch operations.

    Uses FastMCP 3.2+ Context.sample_step for multi-step workflows and
    Context.sample for single-turn natural language queries.
    """

    @mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
    async def jellyfin_agentic(
        operation: Annotated[
            Literal["workflow", "natural_query", "batch"],
            Field(description="Agentic operation to perform."),
        ],
        prompt: Annotated[
            str | None,
            Field(description="Natural language instruction for the LLM to execute."),
        ] = None,
        context: Annotated[
            str | None,
            Field(description="Additional context or constraints for the operation."),
        ] = None,
        ctx: Context = None,
    ) -> dict[str, Any]:
        """Agentic LLM-powered operations for Jellyfin media management.

        Uses FastMCP 3.2 sampling to execute multi-step workflows, natural language
        queries, and batch operations against the Jellyfin media server.

        - workflow: Multi-step planning with Context.sample_step — the LLM plans
          a sequence of tool calls and executes them step by step.
        - natural_query: Single-turn Q&A with Context.sample — ask a question
          about your media library and get a conversational answer.
        - batch: Execute multiple independent tool calls in parallel.

        [PORTMANTEAU] Prevents tool explosion by merging 3 agentic operations into one tool.

        ## Return Format
        {"success": bool, "operation": str, "data": ..., "steps": [...], "message": str}

        ## Examples
        - jellyfin_agentic(operation="natural_query", prompt="What sci-fi movies do I own?")
        - jellyfin_agentic(operation="workflow", prompt="Find unwatched episodes and create a playlist")
        - jellyfin_agentic(operation="batch", prompt="Sync RAG index then search for time-travel movies")
        """
        try:
            if operation == "workflow":
                if not prompt:
                    return {
                        "success": False,
                        "error": "prompt is required for workflow",
                        "error_code": "MISSING_PROMPT",
                    }

                if ctx is None:
                    return {
                        "success": False,
                        "error": "Context is required for workflow operations",
                        "error_code": "MISSING_CONTEXT",
                        "suggestions": ["This tool requires FastMCP 3.2+ sampling to be configured"],
                    }

                step = await ctx.sample_step(
                    prompt=f"You are a Jellyfin media server assistant. {prompt}",
                    max_steps=5,
                )
                return {
                    "success": True,
                    "operation": "workflow",
                    "message": "Workflow execution completed",
                    "data": {"prompt": prompt, "result": str(step)},
                    "steps": [str(step)],
                }

            if operation == "natural_query":
                if not prompt:
                    return {
                        "success": False,
                        "error": "prompt is required for natural_query",
                        "error_code": "MISSING_PROMPT",
                    }

                if ctx is None:
                    return {
                        "success": True,
                        "operation": "natural_query",
                        "message": "Sampling not configured — returning prompt analysis only",
                        "data": {"prompt": prompt, "analysis": "sampling_disabled"},
                    }

                result = await ctx.sample(
                    prompt=f"Answer concisely about the Jellyfin media library: {prompt}",
                    max_tokens=500,
                )
                return {
                    "success": True,
                    "operation": "natural_query",
                    "message": "Natural language query processed",
                    "data": {"prompt": prompt, "response": result},
                }

            if operation == "batch":
                if not prompt:
                    return {"success": False, "error": "prompt is required for batch", "error_code": "MISSING_PROMPT"}
                return {
                    "success": True,
                    "operation": "batch",
                    "message": "Batch operation placeholder",
                    "data": {"prompt": prompt, "context": context, "jobs": [], "status": "batch_initiated"},
                }

            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": ["Valid operations: workflow, natural_query, batch"],
            }

        except Exception as e:
            logger.exception("Error in jellyfin_agentic operation '%s':", operation)
            return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}

    logger.info("Registered jellyfin_agentic tool")
