---
name: project_memory_pillar_utf8_cold_connect_500
description: "wsc-memory-pillar Postgres is UTF8 + psycopg3 (Unicode stores fine); a 'Unicode 500' is usually a client sending cp1252 bytes, not a server bug."
metadata:
  node_type: memory
  type: project
  originSessionId: 71d8a955-480c-46cd-92bf-c963ba9d5a16
  modified: 2026-10-10T14:55:51.877Z
---

**wsc-memory-pillar Postgres (MEMORY_DB_URL, dpg-danl5vqjnfac7390g8g0-a, v18 Oregon) is UTF8/UTF8 and all routers use psycopg3 (`import psycopg`, which ALWAYS forces client_encoding=UTF8). Unicode — em dashes, smart quotes, emoji — stores fine through parametrized inserts. A 500 on a write seen right after a deploy is almost always a cold-connect transient, NOT the data.**

**Why:** 2026-10-10 Operator hit a 500 seeding the hiring_compare dial-check candidate when the name had an em dash ("TEST — Dial Check"); an ASCII-hyphen retry worked, so it looked like a server Unicode bug threatening the shared notes box. Investigation (read-only `mcp__render__query_render_postgres`) disproved the server theory: server_encoding=UTF8, client_encoding=UTF8, and the SAME psycopg write path already holds 1067 non-ASCII rows in `mem_records.search_text` and smart quotes (U+2019) in `thumbtack_message.body`. An em dash cannot 500 a parametrized psycopg3 insert without also breaking those. **Confirmed cause (Operator live rate-test, 0 failures / 6): the 500 was CLIENT-SIDE — Operator's Windows `curl` encoded the em dash as cp1252 bytes, sending invalid UTF-8 in the JSON body, which the server rejected. Re-running with a proper UTF-8 em dash gave 5/5 extras + 1/1 notes all 200.** (My earlier cold-connect-transient hypothesis was plausible but wrong — it was the request bytes, not the DB connection.)

**How to apply:** Before blaming Unicode/encoding for a memory-pillar write 500, confirm the layer with `query_render_postgres` (encodings + whether non-ASCII already round-trips in a sibling table) — then get a RATE through the live endpoint, don't conclude from one occurrence ([[feedback_sporadic_bugs_repeat_test]]). The usual real culprit for a "Unicode 500" is the CLIENT: Windows `curl`/PowerShell encoding non-ASCII as cp1252 instead of UTF-8 in the request body. Reproduce with a known-UTF-8 client before touching server code. Workspace for render MCP = tea-d78l9fqdbo4c7388n9og (Dan's workspace), never ask DJ. Verify by content, not HTTP status ([[feedback_odoo_verify_content_not_status]]).
