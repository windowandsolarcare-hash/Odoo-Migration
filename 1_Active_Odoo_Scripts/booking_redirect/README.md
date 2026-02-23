# Booking Redirect Module for Odoo

## Overview
This custom module creates short booking URLs that redirect to Calendly with prefilled contact data.

## What It Does
- **Short URL**: `https://window-solar-care.odoo.com/book/12345`
- **Looks up**: Contact data from Odoo (name, address, city)
- **Redirects to**: `https://calendly.com/wasc/{city_slug}?name=...&a1=...&a2=...`

## Installation Steps

### 1. Upload Module to Odoo
**Option A - Via FTP/File Manager:**
- Upload the entire `booking_redirect` folder to your Odoo addons directory
- Typically: `/mnt/extra-addons/` or check with Odoo support

**Option B - Via Odoo.sh (if you have access):**
- Commit this folder to your Odoo.sh git repository
- Push to trigger deployment

### 2. Update Apps List
1. Go to **Apps** menu in Odoo
2. Click the **three dots** (⋮) menu
3. Select **Update Apps List**
4. Click **Update** (this scans for new modules)

### 3. Install the Module
1. In **Apps**, remove the "Apps" filter
2. Search for: **"Booking Redirect"**
3. Click **Install**

### 4. Verify Installation
Test the redirect:
- Visit: `https://window-solar-care.odoo.com/book/23951`
- Should redirect to Calendly with prefilled data
- Replace `23951` with an actual contact ID from your system

## Usage

### In Your Odoo Scripts
Update `odoo_reactivation_launch.py` and `odoo_reactivation_preview.py`:

**Change this:**
```python
cal_url = f"https://calendly.com/wasc/{city_slug}?a1={contact.id}"
```

**To this:**
```python
cal_url = f"https://window-solar-care.odoo.com/book/{contact.id}"
```

Much cleaner URL in SMS!

## City Mapping
The module automatically maps cities to Calendly event slugs:
- Palm Springs → `pmsg`
- Rancho Mirage → `rm`
- Palm Desert → `pd`
- Indian Wells → `iw`
- Indio/La Quinta → `indlaq`
- Hemet → `ht`
- Default → `gb` (General Booking)

## URL Parameters Sent to Calendly
- `name` - Full contact name
- `a1` - Contact ID (for tracking)
- `a2` - Street address

## Error Handling
- Invalid contact ID → Shows 404 page
- Missing data → Uses defaults ("Client", empty address)
- Exceptions → Logged to Odoo logs + shows 404

## Support
If the module doesn't appear after "Update Apps List":
1. Check file permissions (should be readable by Odoo process)
2. Check Odoo logs for errors
3. Verify folder structure matches this README
4. Contact Odoo support if using Odoo.sh

## Version History
- **v1.0** - Initial release with city mapping and error handling
