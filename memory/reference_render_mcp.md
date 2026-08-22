---
name: Render MCP Server
description: Official Render MCP server setup — allows Claude Code to deploy, check logs, manage services directly
type: reference
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
# Render MCP Server

**Added:** 2026-04-19
**Status:** Added to local config, needs API key + Claude Code restart to activate

## Setup
- Added via: `claude mcp add render --transport http https://mcp.render.com/sse`
- Config file: `C:\Users\dj\.claude.json` (project: Migration to Odoo)
- Official docs: https://render.com/docs/mcp-server
- GitHub: https://github.com/render-oss/render-mcp-server

## API Key
- Get from: render.com → avatar → Account Settings → API Keys
- NOT YET CONFIGURED — needs key entered after Claude Code restart

## What it can do
- Deploy services
- Check logs and deployment status
- Manage env vars
- Monitor service metrics
- Query Postgres databases

## Next step
1. Get API key from Render Account Settings
2. Restart Claude Code
3. Enter API key when prompted
