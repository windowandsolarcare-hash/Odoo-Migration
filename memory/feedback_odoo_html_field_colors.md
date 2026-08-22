---
name: Odoo HTML field color technique
description: How to create colored status indicators in Odoo form fields using HTML field type + Bootstrap classes
type: feedback
---

Use an HTML field type (not char) with Bootstrap CSS classes to display colored text in Odoo form views. DJ likes this pattern and wants to use it more.

**Why:** Char fields cannot render HTML. HTML fields with Bootstrap classes survive Odoo's sanitizer (inline `style="color:red"` gets stripped, but `class="text-danger"` works). The field must be `readonly="True"` in the view so users don't see the rich text editor.

**How to apply — full recipe:**

**Step 1: Create the HTML field via API**
```bash
curl -X POST "https://window-solar-care.odoo.com/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"service":"object","method":"execute_kw","args":["window-solar-care",2,"API_KEY","ir.model.fields","create",[{"model_id":<MODEL_ID>,"name":"x_studio_my_flag","field_description":"My Flag","ttype":"html","store":true}]]}}'
```
Get model_id first: search `ir.model` where `model = 'sale.order'` → ID 670.

**Step 2: Add to form view as readonly**
```xml
<field name="x_studio_my_flag" readonly="True" string="My Flag"/>
```

**Step 3: Write colored HTML from server action or Phase code**
```python
# Green
'<span class="text-success"><b>OK - details here</b></span>'

# Red
'<span class="text-danger"><b>MISMATCH - details here</b></span>'

# Orange/warning
'<span class="text-warning"><b>PENDING - details here</b></span>'

# Blue/info
'<span class="text-info"><b>INFO - details here</b></span>'
```

**Bootstrap color classes available in Odoo:**
- `text-success` → green
- `text-danger` → red
- `text-warning` → orange/yellow
- `text-info` → blue
- `text-muted` → grey

**Important gotchas:**
- If field already exists as char: must remove from all views first, then unlink field, then recreate as html, then re-add to views
- Odoo blocks deleting fields that are still in views — error: "Cannot rename/delete fields that are still present in views"
- Find which views reference the field: search `ir.ui.view` where arch_db contains the field name
- Remove field from view arch_db → delete field → create as html → re-add to view
- Sale.order model ID = 670 (for this Odoo instance)
- Studio customization view ID = 1385 (sale.order Studio form customization)
