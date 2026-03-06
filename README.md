# Synapse MCP Server

This is the Model Context Protocol (MCP) server for Synapse. It allows AI assistants like Claude Desktop to interact directly with your "Second Brain".

## 🚀 Features

Exposes the following tools to AI models:
- `search_memories`: Semantic search across your saved knowledge.
- `get_memory`: Fetch full details of a specific memory.
- `create_memory`: Save new notes or links directly from the chat.
- `ask_synapse`: RAG-powered chat grounded in your personal context.
- `list_recent_memories`: Overview of your latest captures.

## 🛠️ Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your details.
   ```bash
   cp .env.example .env
   ```
   *Note: You can get your API Token from the web app's local storage (synapse_token).*

3. **Run the Server**:
   ```bash
   python server.py
   ```

## 🔌 Connecting to Claude Desktop

Add this to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "synapse": {
      "command": "python",
      "args": ["/absolute/path/to/synapse/mcp/server.py"]
    }
  }
}
```

## 🏗️ Architecture

The MCP server acts as an adapter layer:
`AI Client (Claude) <-> MCP Server <-> Synapse Backend API <-> Postgres/Gemini`
