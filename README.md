# synapse mcp server

Basic MCP server that connects AI clients to your Synapse backend API.

## tools exposed

- health_check
- search_memories
- list_recent_memories
- get_memory
- create_memory
- ask_synapse

## setup

1. Install dependencies

```bash
cd /home/pranav/work/synapse/mcp
pip install -r requirements.txt
```

2. Configure environment

```bash
cp .env.example .env
```

Set values in .env:

- SYNAPSE_API_URL: backend URL, example http://localhost:8000
- SYNAPSE_API_TOKEN: user JWT token from Synapse login
- SYNAPSE_API_TIMEOUT: optional, default 15 seconds

3. Run server

```bash
python server.py
```

## basic manual verification

After attaching this MCP server in your client (Claude/Cursor/VS Code), call tools in this order:

1. health_check
- Expected: backend ok and token_configured true.

2. list_recent_memories with limit 3
- Expected: ok true and memory list in data.

3. search_memories with a known query
- Expected: ok true and search results in data.

4. create_memory
- Example inputs:
  - memory_type: text
  - title: MCP smoke memory
  - text_content: created from mcp
- Expected: ok true and created memory in data.

5. get_memory with the id returned from create_memory
- Expected: same memory details.

6. ask_synapse with a simple question
- Expected: ok true and reply payload in data.

If any tool returns ok false:

- Check SYNAPSE_API_URL
- Check SYNAPSE_API_TOKEN validity
- Check backend logs for endpoint errors

## claude desktop config example

```json
{
  "mcpServers": {
    "synapse": {
      "command": "python",
      "args": ["/home/pranav/work/synapse/mcp/server.py"]
    }
  }
}
```
