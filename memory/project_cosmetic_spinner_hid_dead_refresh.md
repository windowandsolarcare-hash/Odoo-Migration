# A cosmetic spinner hid a refresh button that never worked (V1 → V2)

**Type:** project
**Date:** 2026-09-01
**Found by:** cloud Lead, answering DJ's question "how does something we programmed get lost over time?"

## What DJ asked
The Command Center's ↻ refresh button didn't force past the cache, and there was no periodic
auto-refresh. DJ assumed one of two things: it was lost in the V1→V2 redesign, or a session broke
working code despite the "never change code that isn't broken" rule.

## What the git history actually shows
Neither. Traced `git log -S` across `static/owner/schedule_hub.html` (V1, archived 2026-07-30) and
`static/owner/v2_command.html` (V2, born 2026-07-18):

1. **The periodic auto-refresh NEVER EXISTED** — not in V1, not in V2. Both only ever refreshed on
   `pageshow(persisted)` and `visibilitychange`. The V1 comment states the design outright: "pageshow
   + visibilitychange force a fresh pull." Refresh-when-you-return was the whole design. DJ
   remembered the *intent*; it was never built.
2. **The ↻ button never bypassed the cache either.** In BOTH versions `refreshCC()` nulls the
   in-memory copies (`DATA.on`, `DATA.need`) and then calls loaders that go through `cjson()`, which
   is cache-first: it returns the IndexedDB copy immediately and only revalidates in the background.
   So the one control meant to get past the cache re-read the same cache.
3. **V2 copied V1's refresh block nearly line-for-line** — same `refreshCC(manual)` shape, same 5s
   throttle, same two event listeners. No rule was broken. Nothing was deleted.

## The real lesson — WHY it survived a year unnoticed
V1's button did this:
```js
if(b && manual){ b.classList.add('spin'); setTimeout(function(){ b.classList.remove('spin'); }, 1200); }
```
**The spinner ran on a TIMER, not on the actual work.** It span for 1.2 seconds and stopped whether
or not anything refreshed, whether or not there was signal. So the button always LOOKED like it
worked. That is precisely why nobody ever filed it as broken. V2 dropped even the fake spinner,
which is why DJ finally noticed.

## How to apply
- **A progress indicator must be driven by the operation, not by a timer.** Start it when the work
  starts, stop it when the work resolves, and report which outcome happened. A `setTimeout`-driven
  spinner is worse than none: it manufactures false confidence and hides a dead feature for months.
- **When a feature "gets lost," check whether it ever existed** before assuming a regression. Run
  `git log -S '<distinctive token>' --follow -- <file>` on BOTH the V2 file and its `_archive_v1/`
  predecessor. Here the honest answer ("never built") beat the assumed one ("broken by a session"),
  and it points at different work.
- **Cache-first + a refresh button is a trap.** If a screen is cache-first by design (correct here —
  DJ must never see a blank Command Center without signal), the manual refresh MUST have an explicit
  network-first path, and must say which copy you are looking at ("Up to date" vs "No connection —
  showing last saved"). Otherwise the cache silently wins and the user is never told.
- Fixed 2026-09-01 in `v2_command.html`: `_forceNet` flag makes manual ↻ network-first,
  real spinner tied to the awaited work, honest toast, 3-minute background retry while visible, and
  `/api/sched/states` raised 6s→15s (its silent timeout was leaving confirmed jobs showing "NOT SENT").
