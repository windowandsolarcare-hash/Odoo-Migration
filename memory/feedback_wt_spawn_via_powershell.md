---
name: feedback_wt_spawn_via_powershell
description: "When a session spawns a fleet tab with `wt ... cmd /k claude -n <Role> /be-<role>`, run it via the PowerShell tool, NOT the Bash/git-bash tool — git-bash's MSYS path conversion mangles the slash-args (/k, /be-<role>) so the inner command breaks and NO tab opens (silent: wt still exits 0). Fixes the respawn procedure."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-19T21:28:49.979Z
---

**Incident 2026-09-19 (standing up Builder-2).** Lead spawned a new role tab from the **Bash (git-bash) tool** with the documented respawn command:
`wt -w wscfleet new-tab --title Builder-2 -d "<projdir>" cmd /k claude -n Builder-2 /be-builder2`
The `wt` call returned exit 0 ("dispatched"), but **no tab opened** — DJ saw nothing, Builder-2 never appeared in `ListAgents`. Re-running the IDENTICAL command from the **PowerShell tool** worked instantly (Builder-2 [ba8762] live in ~30s).

**Root cause:** git-bash/MSYS **auto-converts arguments that start with `/`** into Windows paths (`/k` → `C:/Program Files/Git/k`, `/be-builder2` → a bogus path). So the `cmd /k claude … /be-builder2` tail got mangled → the inner shell command was garbage → the tab failed to launch (and `wt` itself still exited 0, so it looked like it worked — a SILENT failure).

**The rule:** **spawn fleet tabs via the PowerShell tool, not Bash.** PowerShell does no MSYS path conversion, so `/k` and `/be-<role>` pass through intact. This applies to the whole [[feedback_respawn_session_procedure]] step 2 ("the session launches the new tab itself") and any `wt`/`cmd`-with-slash-args launch.
- PowerShell form (verified): `wt -w wscfleet new-tab --title <Role> -d "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo" cmd /k claude -n <Role> /be-<role>`
- If you MUST use git-bash, prefix `MSYS_NO_PATHCONV=1 ` (disables the conversion) — but PowerShell is simpler + is the standard now.
- **Verify the spawn actually took:** `wt` exit 0 ≠ tab opened. Confirm the new session shows in `ListAgents` (or DJ sees the tab) before reporting it live.

See [[feedback_respawn_session_procedure]], [[project_fleet_role_boot_identity]].
