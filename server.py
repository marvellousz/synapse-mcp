import os
import uuid
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env if present.
load_dotenv()

API_URL = os.getenv("SYNAPSE_API_URL", "http://localhost:8000").rstrip("/")
API_TOKEN = os.getenv("SYNAPSE_API_TOKEN", "").strip()
REQUEST_TIMEOUT = float(os.getenv("SYNAPSE_API_TIMEOUT", "15"))

ALLOWED_MEMORY_TYPES = {"pdf", "image", "video", "text", "webpage", "youtube"}

mcp = FastMCP("Synapse", dependencies=["requests", "python-dotenv"])

_session = requests.Session()


def _headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return headers


def _api_request(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{API_URL}{path}"
    try:
        response = _session.request(
            method=method,
            url=url,
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.RequestException as exc:
        return {"ok": False, "error": f"Network error: {exc}"}

    if response.status_code >= 400:
        detail = response.text[:500]
        return {
            "ok": False,
            "status": response.status_code,
            "error": f"API error {response.status_code}",
            "detail": detail,
        }

    if response.status_code == 204:
        return {"ok": True, "data": None}

    try:
        return {"ok": True, "data": response.json()}
    except ValueError:
        return {"ok": True, "data": response.text}


@mcp.tool()
def health_check() -> Dict[str, Any]:
    """Check whether MCP can reach Synapse backend and whether auth is configured."""
    result = _api_request("GET", "/")
    return {
        "mcp": "ok",
        "api_url": API_URL,
        "token_configured": bool(API_TOKEN),
        "backend": result,
    }


@mcp.tool()
def search_memories(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search memories by semantic+keyword hybrid search."""
    q = (query or "").strip()
    if not q:
        return {"ok": False, "error": "Query cannot be empty"}
    safe_limit = max(1, min(limit, 50))
    return _api_request("POST", "/api/search/hybrid", json={"query": q, "limit": safe_limit})


@mcp.tool()
def list_recent_memories(limit: int = 5) -> Dict[str, Any]:
    """List latest memories from the current authenticated user."""
    safe_limit = max(1, min(limit, 50))
    return _api_request("GET", "/memories", params={"take": safe_limit})


@mcp.tool()
def get_memory(memory_id: str) -> Dict[str, Any]:
    """Get full details for a memory by id."""
    memory_id = (memory_id or "").strip()
    if not memory_id:
        return {"ok": False, "error": "memory_id is required"}
    return _api_request("GET", f"/memories/{memory_id}")


@mcp.tool()
def create_memory(
    memory_type: str,
    title: str,
    text_content: str,
    source_url: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new memory record in Synapse."""
    memory_type = (memory_type or "").strip().lower()
    if memory_type not in ALLOWED_MEMORY_TYPES:
        return {
            "ok": False,
            "error": "Invalid memory_type",
            "allowed": sorted(ALLOWED_MEMORY_TYPES),
        }
    if not (title or "").strip():
        return {"ok": False, "error": "title is required"}
    if not (text_content or "").strip():
        return {"ok": False, "error": "text_content is required"}

    payload = {
        "type": memory_type,
        "title": title.strip(),
        "contentHash": f"mcp-{uuid.uuid4().hex}",
        "extractedText": text_content.strip(),
        "sourceUrl": (source_url or "").strip() or None,
        "category": (category or "").strip() or None,
        "status": "ready",
    }
    return _api_request("POST", "/memories", json=payload)


@mcp.tool()
def ask_synapse(question: str, use_internet: bool = False) -> Dict[str, Any]:
    """Ask a RAG chat question grounded in Synapse memories."""
    message = (question or "").strip()
    if not message:
        return {"ok": False, "error": "question cannot be empty"}
    return _api_request(
        "POST",
        "/api/chat",
        json={"message": message, "history": [], "useInternet": use_internet},
    )


if __name__ == "__main__":
    mcp.run()
