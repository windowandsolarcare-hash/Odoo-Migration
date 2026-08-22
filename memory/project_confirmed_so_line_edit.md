---
name: project_confirmed_so_line_edit
description: "Editing sale.order lines on a CONFIRMED SO: DJ's chosen fix = UNCONFIRM (cancel->draft) -> replace lines freely (real delete + product change) -> RECONFIRM -> restore snapshotted date_order (action_confirm wipes it to now). Odoo blocks removing/repricing-product on a confirmed line directly. Also: writing qty without price_unit recomputes price."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-05T20:29:24.426Z
---

## ★ CHOSEN APPROACH (DJ 2026-08-05): UNCONFIRM → edit freely → RECONFIRM → restore date_order.
On a confirmed job Odoo blocks removing a line AND changing a line's product. Rather than work around each block, DJ's rule: **a draft opens everything up**, so `/api/job/lines` now, when `state in ('sale','done')`:
1. **Snapshot `date_order`** (+ `commitment_date` if set) FIRST — `action_confirm` will wipe date_order to `now()`.
2. `action_cancel` → `action_draft` (unconfirm).
3. `write order_line = [(5,0,0)] + [(0,0,vals)...]` — clean full replace; add/edit/**delete**/product-change all allowed in draft.
4. `action_confirm`.
5. **`write({'date_order': saved})`** to put the scheduled slot back (else the job jumps to today + falls off its scheduled day).
6. Safety net: re-read state; if not sale/done, action_confirm again + restore date_order (never strand the job off-schedule).
- **Verified end-to-end 2026-08-05** on a throwaway confirmed SO: removed a product + added another → $330, exactly 2 lines (removed line truly GONE, NO qty-0 zombie), date_order preserved (Aug 19 8am), still confirmed. This SUPERSEDES the product-keyed / qty-0 approach below (no more zombie lines).
- **Fields:** only `date_order` matters (start; the schedule gate + Render derive the slot from it). sale.order in this Odoo 19 has **NO `date_deadline`** (KeyError) — end time is NOT stored separately; `commitment_date`/`expected_date` are usually blank. Rule #8: always write date_order back after action_confirm.
- **Guard:** still refuse if `invoice_ids` present (can't unconfirm an invoiced SO cleanly). Draft SOs skip the dance — plain `(5,0,0)`+re-add.

## ★ THE "only the last line saves / total wrong" BUG (root cause, fixed 2026-08-05)
Separate from the Odoo write errors. The field **pricing editor** (`v2_field.html` `fdSaveLines`) filters `_fdLines.filter(l => l.product_id)` before POSTing — it DROPS any line with no product_id. But the READ endpoint **`/api/so_full`** (dashboard.py ~L7697) returned each line as `{name,qty,price,subtotal}` **WITHOUT `product_id`**. So every pre-existing line loaded back with `product_id:0` → got filtered out on the next Save → only the just-added dropdown item (which carries a real product_id) survived. Symptom: add 5 items, Save, reopen → only the last one; totals wrong.
- **Fix:** `so_full` now reads `product_id` + `display_type` and returns `product_id: l['product_id'][0] if l.get('product_id') else 0`, filtering out `display_type` (note/section) lines. Verified live on SO 17389: lines came back `pid None` (old) → `pid 80/81/83` (new). Editor now round-trips product_id so loaded lines survive Save.
- **Latent note (not fixed):** the editor's Save does a FULL order_line replace (only product lines). An SO carrying a `display_type='line_note'` line (e.g. Render Quote Tool blob, see [[project_quote_line_note_and_quotes_shadow]]) would lose that note line on a pricing-editor Save. Pre-existing behavior; John Bullock had none. Revisit if quotes get edited via the field pricing editor.

---

**(reference) The two underlying Odoo traps that forced the unconfirm approach — both hit 2026-08-05 on `/api/job/lines`, SO 004557/John Bullock:**

1. **Cannot REMOVE a line on a confirmed SO.** `(5,0,0)` (clear all), `(2,id)`, `(3,id)` all raise `UserError: "Once a sales order is confirmed, you can't remove one of its lines (we need to track if something gets invoiced or delivered). Set the quantity to 0 instead."` The old code did `cmds=[(5,0,0)]` then re-add → crashed every time DJ edited line items on a scheduled (confirmed) job.

1b. **Cannot MODIFY the product_id of an existing line on a confirmed SO.** `(1, id, {'product_id': other})` raises `UserError: "You cannot modify the product of this order line."` So you can't just reuse existing line SLOTS positionally and reassign products (my first fix attempt did that → this error). You CAN change qty / price_unit / name on a confirmed line — just not the product.
   - **Fix pattern (shipped in `/api/job/lines`, verified end-to-end 2026-08-05):** if `state in ('sale','done')`, match new lines to existing ones **BY PRODUCT**: same product → `(1, id, {name,qty,price})` update in place (NEVER send product_id); brand-new product → `(0,0,{vals})` add; existing product no longer wanted → `(1, id, {'product_uom_qty': 0})` zero it (can't delete, can't repurpose). Draft SOs keep the clean `(5,0,0)`+re-add.
   - **Side effect (accepted):** a removed line becomes a **qty-0 / $0 "zombie" line** that stays on the SO (Odoo won't let it go). Total is correct. If these ever clutter a customer invoice/quote, filter `product_uom_qty > 0` when building the invoice display (payments.py / dashboard `_create_stripe_tip_link`) — NOT yet done.

2. **Writing `product_uom_qty` (or product_id) WITHOUT `price_unit` RECOMPUTES price_unit** from the product's list/pricelist price. A "no-op" `write (1,id,{'product_uom_qty': same_qty})` on SO 17389 silently dropped the total $445→$106 (Windows $300+Solar $145 → their default prices). **Always write `price_unit` explicitly in the same command** when updating a line, or you'll wipe the agreed price. (The real endpoint always sends product_id+name+qty+price together, so it's safe — the damage came from a verify script that omitted price.)

**How to apply:** any code touching `order_line` on a confirmed SO must (a) never unlink, (b) always include price_unit when it writes qty/product. See [[project_status_label_vs_so_state]] (confirmed = on the schedule) and [[feedback_odoo_rpc_write_pattern]].
