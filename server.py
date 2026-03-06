import os
import requests
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Configuration
API_URL = os.getenv("SYNAPSE_API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("SYNAPSE_API_TOKEN")

# Initialize FastMCP server
mcp = FastMCP("Synapse", dependencies=["requests", "python-dotenv"])

def get_headers():
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return headers

@mcp.tool()
def search_memories(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search through your Synapse memories using a natural language query.
    Returns a list of memories semantically relevant to the query.
    """
    try:
        response = requests.post(
            f"{API_URL}/api/search/hybrid",
            json={"query": query, "limit": limit},
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_memory(memory_id: str) -> Dict[str, Any]:
    """
    Retrieve the full details of a specific memory by its ID.
    Includes extracted text, summary, and metadata.
    """
    try:
        response = requests.get(
            f"{API_URL}/memories/{memory_id}",
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_memory(type: str, title: str, text_content: str, source_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new memory in Synapse.
    'type' should be one of: text, webpage, youtube.
    'text_content' is the main content to be stored and indexed.
    """
    try:
        # Step 1: Create memory record
        # A simple hash for contentHash since we don't have the file logic here
        import time
        content_hash = f"mcp-{int(time.time())}"
        
        payload = {
            "type": type,
            "title": title,
            "contentHash": content_hash,
            "extractedText": text_content,
            "sourceUrl": source_url,
            "status": "ready"
        }
        
        response = requests.post(
            f"{API_URL}/memories",
            json=payload,
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def ask_synapse(question: str) -> str:
    """
    Ask a question to Synapse. It will search through your memories 
    and provide a response grounded in your personal knowledge base.
    """
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"message": question, "history": []},
            headers=get_headers(),
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        return data.get("reply", "No response from Synapse.")
    except Exception as e:
        return f"Error connecting to Synapse: {str(e)}"

@mcp.tool()
def list_recent_memories(limit: int = 5) -> List[Dict[str, Any]]:
    """
    List the most recently saved memories.
    Useful for seeing what has been added to the brain lately.
    """
    try:
        response = requests.get(
            f"{API_URL}/memories",
            params={"take": limit},
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    mcp.run()
