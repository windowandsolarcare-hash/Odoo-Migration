---
name: Claude Code Remote Control auto-start setup
description: Claude Code Remote Control is configured to auto-start at login so DJ can control it from his Galaxy Z Fold 5 via the Claude mobile app
type: project
originSessionId: 5d8f5a0f-43bb-4afc-ba26-1b224b7d8424
---
Claude Code Remote Control is set up for auto-start on DJ's Windows 11 machine. Set up 2026-04-20.

**Components:**
- Scheduled task: `ClaudeRemoteControl` (registered via PowerShell `Register-ScheduledTask`, not schtasks — schtasks returned Access Denied)
- Startup script: `C:\Users\dj\start-claude-remote.bat` — 30s timeout, cd to Migration to Odoo folder, launch `claude.exe remote-control --name "WSC-Auto"`
- Session name visible in Claude app: `WSC-Auto`
- Trigger: At user logon (user-scoped, no admin needed)
- Claude CLI location: `C:\Users\dj\.local\bin\claude.exe` (native Windows binary, not a bash script)

**Why:** DJ wanted to control Claude Code from his phone while on the road. Remote Control is the official Claude Code feature — gives full local environment access (files, MCP servers, configs) via Claude mobile app or browser.

**How to apply:**
- If DJ reports remote control isn't working: check Task Manager for `claude.exe`, verify `ANTHROPIC_API_KEY` env var is NOT set (it blocks remote control, requires OAuth via `claude auth login`), check the scheduled task state with `Get-ScheduledTask -TaskName 'ClaudeRemoteControl'`
- To test manually: `powershell -Command "Start-ScheduledTask -TaskName 'ClaudeRemoteControl'"`
- To disable/remove: `powershell -Command "Unregister-ScheduledTask -TaskName 'ClaudeRemoteControl' -Confirm:\$false"` and delete the .bat file
- Push notifications enabled via `/config` inside Claude Code → "Push when Claude decides" (Claude mobile app, signed in with windowandsolarcare@gmail.com)
- Task runs hidden — no visible terminal. Verify it started via Claude app session list, not by looking for a window.
- Requires Claude Code v2.1.110+ (DJ has 2.1.114 as of setup date)

**Gotchas discovered during setup:**
- `schtasks /create` from Git Bash mangles `/` flags — use `cmd.exe //c "schtasks..."` or PowerShell's Register-ScheduledTask instead
- `schtasks /create` returned "Access is denied" even for user-scoped tasks — PowerShell's `Register-ScheduledTask` with `-LogonType Interactive -RunLevel Limited` worked without admin
- If machine sleeps, session pauses — DJ must wake the PC before connecting from the road (future: consider wake-on-LAN if this becomes a pain point)
