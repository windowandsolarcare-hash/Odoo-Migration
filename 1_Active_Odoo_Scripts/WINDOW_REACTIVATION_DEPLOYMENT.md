# Window-Only Reactivation - Deployment Guide

**Author:** DJ Sanders  
**Generated:** 2026-03-06

---

## 🎯 PURPOSE

Filter reactivation campaigns to **ONLY target window cleaning customers** (exclude solar-only customers).

**Problem:** Current reactivation workflow targets ALL dormant customers, including those whose most recent order was solar-only.

**Solution:** Three new Server Actions that filter by most recent order type.

---

## 📂 FILES CREATED

### 1. `odoo_find_window_reactivation_candidates.py`
**What it does:** Displays filtered list of window cleaning customers  
**Use case:** Visual inspection of who qualifies before sending campaigns

### 2. `odoo_window_reactivation_filter_v2.py`
**What it does:** Same as #1, but can run from Contacts view (no SO selection needed)  
**Use case:** Quick scan of all customers to see who qualifies

### 3. `odoo_reactivation_launch_WINDOWS_ONLY.py`
**What it does:** Complete reactivation workflow (pricing, SMS, opportunity creation) - WINDOWS ONLY  
**Use case:** Production replacement for original `odoo_reactivation_launch.py`

---

## 🚀 DEPLOYMENT STEPS

### OPTION A: Filter & Review (Recommended First Step)

Use this to SEE who qualifies before sending campaigns.

1. **Go to:** Settings → Technical → Automation → Server Actions
2. **Click:** Create
3. **Fill in:**
   - **Name:** `Window Reactivation: 1+ Year (Filter Only)`
   - **Model:** Contact (`res.partner`)
   - **Action To Do:** Execute Python Code
   - **Python Code:** Copy/paste contents of `odoo_window_reactivation_filter_v2.py`
4. **Save**

**To Use:**
- Go to Contacts
- Click "Action" menu → "Window Reactivation: 1+ Year (Filter Only)"
- See filtered list of window customers

---

### OPTION B: Launch Reactivation Campaigns (Production)

Use this to actually CREATE opportunities and send SMS.

1. **Go to:** Settings → Technical → Automation → Server Actions
2. **Click:** Create
3. **Fill in:**
   - **Name:** `Reactivation Campaign - Windows Only`
   - **Model:** Sales Order (`sale.order`)
   - **Action To Do:** Execute Python Code
   - **Python Code:** Copy/paste contents of `odoo_reactivation_launch_WINDOWS_ONLY.py`
4. **Save**

**To Use:**
- Go to Sales → Orders
- Use your existing custom search to find dormant customers
- Select a Sales Order
- Click "Action" menu → "Reactivation Campaign - Windows Only"
- Script will:
  - ✅ Check if most recent order had windows
  - ✅ Create opportunity if yes
  - ⏭️ Skip if solar-only

---

## 🔍 HOW THE FILTER WORKS

### Logic:
```
For each contact:
  1. Find their MOST RECENT confirmed Sales Order
  2. Check products in that order:
     - Has "window" in product name? → INCLUDE
     - Has ONLY "solar" in product name? → EXCLUDE
  3. Return filtered list
```

### Examples:

| Customer | Last Order Products | Result |
|----------|---------------------|--------|
| John Doe | Windows In/Out + Solar | ✅ INCLUDE (has windows) |
| Jane Smith | Windows Outside Only | ✅ INCLUDE (has windows) |
| Bob Jones | Solar Panel Cleaning | ❌ EXCLUDE (solar-only) |
| Mary Brown | Solar + Windows | ✅ INCLUDE (has windows) |

---

## ⚙️ CONFIGURATION

Both scripts have a configuration section at the top:

```python
# --- CONFIGURATION ---
DAYS_THRESHOLD = 365  # 1 year (change to 730 for 2 years)
EXCLUDE_SOLAR_ONLY = True  # False = include all service types
```

**To change:**
- Edit the script in Odoo Server Action
- Adjust `DAYS_THRESHOLD` for different timeframes
- Set `EXCLUDE_SOLAR_ONLY = False` to include solar customers

---

## 📊 TESTING

### Test Case 1: Filter View
1. Run `odoo_window_reactivation_filter_v2.py` from Contacts
2. Check that displayed contacts have window services in their history
3. Verify solar-only customers are excluded

### Test Case 2: Campaign Launch
1. Find a dormant customer with window service in last order
2. Run `odoo_reactivation_launch_WINDOWS_ONLY.py`
3. Verify opportunity is created
4. Find a solar-only customer
5. Run script again
6. Verify it's skipped with message

---

## 🎛️ CUSTOM SEARCH (OPTIONAL)

If you want a **permanent filter** in the Contacts list view (without Server Action):

**Unfortunately:** Odoo's UI search filters can't easily check "most recent order's products" because it requires:
- Joining `res.partner` → `sale.order` → `sale.order.line` → `product.product`
- Filtering by MAX date
- Checking product names

**Recommendation:** Use the Server Action (Option A or B above) instead. It's more flexible and easier to maintain.

---

## 📝 NEXT STEPS

1. **Deploy Option A (Filter):** See who qualifies
2. **Review Results:** Check if the filter logic is correct
3. **Deploy Option B (Production):** Replace your current reactivation workflow
4. **Test:** Run on a few dormant window customers
5. **Monitor:** Check that solar-only customers are properly excluded

---

## 🔄 MIGRATION PATH

**Current Workflow:**
```
Sales Orders → Custom Search → Select Order → Run Reactivation
(Processes ALL service types)
```

**New Workflow:**
```
Sales Orders → Custom Search → Select Order → Run Windows-Only Reactivation
(Skips solar-only customers automatically)
```

**To Migrate:**
1. Keep your existing `odoo_reactivation_launch.py` for now
2. Deploy `odoo_reactivation_launch_WINDOWS_ONLY.py` as a separate action
3. Test both side-by-side for a week
4. Once confident, rename/disable the old one
5. Make the new one your default

---

## ❓ FAQ

**Q: What if a customer has BOTH window and solar?**  
A: They're INCLUDED (windows = primary service focus)

**Q: Can I adjust the 1-year threshold?**  
A: Yes, change `DAYS_THRESHOLD = 365` to any value (730 = 2 years, etc.)

**Q: What if I want to run a solar-only campaign later?**  
A: Set `EXCLUDE_SOLAR_ONLY = False` or create a separate "solar-only" version

**Q: Will this affect existing opportunities?**  
A: No, it only affects NEW opportunities created by the script

---

**Questions or issues?** Check the system log in Odoo (Settings → Technical → Logging) for detailed execution logs.
