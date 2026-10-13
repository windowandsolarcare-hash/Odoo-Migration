---
name: project_inbox_audio_range_and_allpill_cache
description: "Two reusable gotchas (2026-10-13): (1) inline <audio> on Android WebView needs an HTTP Range/206 response or it shows '0 of 0 minutes' and won't play — /voice/rec (voice.py) now serves 206 slices. (2) sms.py inbox_list caches the SORTED `out` per `filter`, so any sort/order variant (e.g. the 'All' pill's pure-newest-first) MUST be applied POST-cache on a copy, keyed on a separate param (pin), never gated at build-time — else the cache collides between callers sharing a filter value. Plus: the FE 'All' pill remaps to filter=active before sending."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-13T14:52:46.267Z
---

## (1) Inline `<audio>` on Android needs HTTP Range (206), else "0 of 0 minutes"
`/owner/voice/rec` (`routers/owner/voice.py voice_rec`) proxies the Twilio recording mp3. It used to return the full bytes as a plain **200** with no `Accept-Ranges`. An inline `<audio controls>` — **especially Android WebView (DJ's phone)** — needs a **206 range** response to establish duration/seek; without it the player shows **"0 of 0 minutes" and won't play**. (A direct-link full-page open tolerates a plain 200 — that's why "opens via direct link" ≠ "plays inline".)
**Fix (2026-10-13):** `voice_rec(request: Request, sid)` now reads the `Range` header; always sets `Accept-Ranges: bytes` + `Content-Length`; returns a **206** slice with `Content-Range: bytes start-end/total` when a Range header is present (416 on an unsatisfiable range; full-200 fallback on any parse issue; 404/502 guards kept). Same endpoint feeds the candidate-compare player AND the inbox voicemail/recording players — one fix covers both surfaces. **Rule: any inline-audio endpoint we proxy must support Range.**

## (2) inbox_list caches the SORTED list per `filter` → sort variants go POST-cache on a copy
`sms.py inbox_list` (`@router.get('/api/inbox/list')`, ~line 2304) builds `out`, sorts it (newest-first then Priority-pin float at ~:2376-2377), merges split-numbers, and **caches the finished sorted `out` keyed ONLY by `filter`** (`_INBOX_CACHE` + `_INBOX_LASTGOOD`). So **you cannot gate the sort at build-time by a new flag** — two callers sharing the same `filter` value would collide on one cached list (first build wins, wrong order for the other). Label/source/view filters already dodge this by running **post-cache on a fresh list**.
**Pattern (the 'All' pill pure-newest-first fix, 2026-10-13):** added `pin: int = 1` to `inbox_list`; when `pin=0`, re-sort **post-cache on a COPY** (`out = sorted(out, key=last_ts, reverse=True)`) right before pagination — never mutates the cached/last-good list, and `pin` defaults to 1 (pin-on) so every existing caller + the internal SWR calls are byte-identical. SORT only, never inclusion.
**Also non-obvious:** the FE **"All" pill remaps to `filter=active`** before calling the server (`static/owner/v2_inbox.html:314` `FILTER==='all'?'active':FILTER`), so the server can't distinguish "All" from the default `active` by filter value — behavior that must differ for "All" has to ride a **separate query param** (here `&pin=0`), not the filter. The Priority-pin float itself is the deliberate Nick Conway fix (2026-09-22) — keep it ON for every other pill.

See [[feedback_lazy_on_demand_not_prefetch]], [[feedback_hud_cards_live_not_inbox]], [[project_two_quote_pages_two_launchers]].
