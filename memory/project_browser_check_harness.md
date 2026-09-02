# Test it in a BROWSER before shipping — `scripts/browser_check.py`
**Type:** project
**Created:** 2026-09-02 (Lead, cloud)
**Trigger:** DJ: *"one session came along and just tested everything for me and told me they tested
it before shipping. Then that kind of got lost. Did you test your changes the same way I test them?"*
Honest answer at the time: **server half yes, screen half no.** Every UI change that week shipped on
`node --check`. This is the fix, made repeatable so it does not get lost a second time.

## The distinction that matters
- `curl` proves the **endpoint** returns the right JSON. Real, but it is half the job.
- `node --check` proves the JS **parses**. It says nothing about whether anything renders.
- Neither one can tell you the panel appeared, the menu item is reachable, the redirect fired, or
  the header wrapped into a ragged block on a 414px phone.

**A change to a `.html`/`.js` file is NOT tested until a browser has rendered it.**

## The tool
`scripts/browser_check.py` (app repo). `python3 scripts/browser_check.py all` (or `catchup` /
`currentjob` / `inbox`). Exits non-zero on any failure, so it can gate a push.

How it is wired, and why:
- **Pages + JS are served from YOUR CHECKOUT** on 127.0.0.1 — so you test the code in front of you,
  not whatever happens to be deployed. This is what makes it useful BEFORE a push.
- **Every `/owner/api/*` and `/book/api/*` call is relayed to the LIVE app** with `requests`, so the
  page runs its real code against real production data (a stub would only prove the stub matches).
- **READ-ONLY by default** — the relay refuses non-GET. A browser test must never text a customer or
  move a job. `--allow-writes` exists and should almost never be used.
- `--shots <dir>` drops a PNG per check; read it, layout bugs are invisible in text.

## Cloud gotcha (cost an attempt on 2026-09-02)
In a CLOUD session **Chromium cannot reach the internet** — the egress relay resets the browser's
tunnels (`ws_closed_mid_exchange`) even though `curl` to the same host works fine. That is exactly
why the harness relays API calls through `requests` instead of letting the page fetch directly.
Locally the browser has normal network, and the same harness still works.
Chromium lives at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` in the cloud image
(`pip install playwright`; do NOT run `playwright install` there). Override with `WSC_CHROME`.

## It earns its keep immediately
First run found a defect no curl could ever see: the catch-up panel put its title and the last-job
line side by side, which on a 414px phone wrapped into a ragged four-line header. Fixed before DJ
ever saw it.

## How to apply
Add a check function to `CHECKS` whenever you ship a UI change worth keeping working. Assert what
DJ would look for — *does it show up, is it reachable, is it in the right place, did it fill in* —
not internal state. And when you report to DJ, say plainly which half you tested; an "it's tested"
that means "the endpoint returns JSON" is the claim that eroded this in the first place.
