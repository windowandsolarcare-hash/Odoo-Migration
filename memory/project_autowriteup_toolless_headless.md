---
name: project_autowriteup_toolless_headless
description: "App Building AUTO-WRITE-UP is LIVE on DJ's Surface (2026-10-14): a local Windows scheduled task polls pending-enrichment + runs a TOOL-LESS headless `claude -p` that drafts a card's title+problem. Also the REUSABLE pattern for safely running an UNATTENDED headless claude -p: isolation-by-construction + a deny-proof acceptance gate."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-14T13:50:16.255Z
---

Shipped/enabled 2026-10-14 (§15 Audit COMPLETE + Lead firsthand; plan `3_Documentation/review/auto_writeup/`, launcher `poll_and_enrich.py`, evidence `DENY_PROOF_EVIDENCE.md` a5af89b3; ship card `autowriteup`). DJ: "say it into the mic, everything starts from there" — on recording-stop the card writes itself up with no human/session.

**How it runs:** a Windows Task Scheduler task `WSC Auto Writeup` (every 2 min, runs as dj) → the TRUSTED launcher `C:\ProgramData\wsc_enrich\poll_and_enrich.py` → GET `/owner/api/ship/cards/pending_enrichment` (NOTIFY_SECRET, from the local file) → if pending, ONE one-shot **tool-less** `claude -p` drafts `[{card_id,title,problem}]` → launcher validates (card_id∈pending, caps, `json.loads` not eval) → POST `/owner/api/ship/card/enrich`. AI tokens (subscription, no API $) only when a card is pending.

**★ REUSABLE SAFETY PATTERN — running an UNATTENDED headless `claude -p` so an untrusted input can't reach any capability (the whole point; Audit+Lead hardened it over 4 rounds):**
1. **TOOL-LESS by ISOLATION, not just precedence.** `--settings <locked>` only MERGES ambient `~/.claude`+project settings (deny-by-precedence). TRUE isolation = run the subprocess with a **minimal `env` dict** (no inherited DJ env, NO ANTHROPIC_API_KEY, no ambient CLAUDE_*) + **`CLAUDE_CONFIG_DIR`=an isolated dir** AND **`cwd`=a dir OUTSIDE the user home** (`C:\ProgramData\wsc_enrich\cfg`). CLAUDE_CONFIG_DIR isolates the USER config; cwd-outside-~ stops Claude's PROJECT-config walk-UP from reaching `~/.claude` (ANY dir under C:\Users\dj has ~/.claude as an ancestor → it'd load as a "project" config). Belts on top: `--restricted` (removes built-ins) + full `--disallowedTools Bash Read Edit Write Glob Grep WebFetch WebSearch Task NotebookEdit` (deny>allow) + `--permission-prompts none` (non-interactive → unlisted = auto-denied).
2. **The launcher (trusted) does ALL I/O + holds the secret** (header, from the local file, never in the prompt/args). The model only emits text. **Fold B:** invoke via `subprocess` **argv-list, shell=False, prompt via STDIN** — never a shell-interpolated string (an untrusted transcript with `$()`/`;`/backticks can't inject the launcher).
3. **Auth in isolation:** copy ONLY `~/.claude/.credentials.json` into the isolated CFGDIR so the run authenticates while inheriting no ambient tool-allow. ACL the dir **DJ-only at mkdir, BEFORE** copying the cred (`icacls /inheritance:r /grant:r dj:(OI)(CI)F`) — ProgramData is broadly readable by default.
4. **DENY-PROOF acceptance gate (named, before unattended run):** install the task DISABLED; run the exact invocation against a HOSTILE transcript (tries Bash + write a file + read `.credentials.json` + fetch a URL) in DJ's REAL env; it MUST produce NO side-effect file, NO cred leak, and still produce text (auth works). Capture durable EVIDENCE (exact input + full stdout + run-log line + `dir` showing no side-effect file); Lead reads it FIRSTHAND + Audit construction-confirms; ONLY a clean refuse enables the task. (Proven: a 3-vector injection was refused, zero side-effects — the model even detected the injection.) A hostile-ONLY input yields NO JSON (wholesale refusal) — correct; the launcher fail-safes (no POST on non-JSON). The benign→valid-JSON path is proven by a separate 1-pending functional test (run.log `enriched=1`).
5. **Install = DJ's OWN firsthand picker** in the executing session (like the nudge hook) — a relayed decision scopes it, never authorizes the machine change. PID-liveness lock (steal dead/stale, never wedge) + append-only run-log.

Ties [[feedback_audit_stamp_confirm_firsthand]], [[feedback_never_relay_credential_via_session]], [[project_fleet_ship_system]] (the enricher this feeds), [[feedback_deploy_tap_reaches_executor_not_relayed]].
