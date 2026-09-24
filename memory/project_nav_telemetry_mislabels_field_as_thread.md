---
name: project_nav_telemetry_mislabels_field_as_thread
description: "Nav-telemetry gotcha (nav v1.1, 2026-09-24): the client page() label maps BOTH v2_field.html AND the thread view to 'thread', so a v2_command → v2_field.html?open_so job-open deep-link is RECORDED AS page='thread' in wsc_client_telemetry. Do NOT infer 'no v2_field nav happened' from the absence of a 'field' page label. Also: the 'page' field stores a truncated URL slice WITHOUT the query string (?open_so=), and DJ's device IP rotates (cellular) — query nav traces by client_id, not remote_ip."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-24T15:31:49.933Z
---

# Reading nav telemetry: v2_field is mislabeled 'thread', page drops the query string, IP rotates

**2026-09-24, diagnosing the Command-Center name-tap "bare Field Day flash."** Three traps when reading `wsc_client_telemetry` (the client nav/failure beacon → PG `dpg-danl5vqjnfac7390g8g0-a`, table `wsc_client_telemetry`, also surfaced via `/owner/api/telemetry/nav_stats`):

1. **The `page()` label maps BOTH `v2_field.html` and the thread view to `'thread'`** (a known nav-v1.1 page-label bug Specialists logged). So a `v2_command → v2_field.html?open_so=<id>` job-open deep-link shows up in the data as `prev_page=…v2_command.html, page='thread'`. **A `page='thread'` row is NOT necessarily the conversation thread — it may be a v2_field job-open.** Do NOT conclude "no v2_field navigation happened" from the absence of a 'field' label — I did, and the deep-link was there all along, mislabeled. The v1.1 fix disambiguates the label.
2. **`page` is a truncated trailing slice of the URL WITHOUT the query string** — e.g. `.../v2_field.html?open_so=17370` is stored as `ic/owner/v2_command.html`-style fragments and the `?open_so=` is dropped. So telemetry cannot distinguish a bare page load from a deep-linked one, and cannot see intra-page render sequences at all (nav telemetry logs page-to-page hops, not paint order — an in-page flash is invisible to it by design).
3. **DJ's device IP rotates** (cellular in the field) — 207.212.33.60 one day, 76.90.35.160 / 107.116.170.45 the next. **Query his nav trace by `client_id` (stable per device), not `remote_ip`.** Grab his `client_id` from any recent row, then filter by it across days.

## How to apply
When you need one device's nav pairs: `SELECT ... WHERE client_id IN (SELECT client_id FROM wsc_client_telemetry WHERE remote_ip='<a known IP>') AND ts::date='<day>' AND step='nav'`. Treat `page='thread'` as ambiguous (thread OR v2_field). For anything about intra-page render/flash order, telemetry is inconclusive BY DESIGN — read the CODE (ties to [[project_static_gates_miss_semantic_placement]] / verify-by-content). MIRROR to Odoo-Migration/memory/.
