# Odoo Server Action: "WORKIZ_CLONE" — canonical Workiz job cloner (SINGLE SOURCE OF TRUTH).
# Lives in Odoo (always-up) instead of Render. Phase 5 (Zapier JSON-RPC), reactivation SA 563
# (in-process run), and Duplicate (Render odoo_rpc) all call this so the field set is in ONE place.
# Reads params from context, builds the canonical payload, GETs source from Workiz if a UUID is
# given, creates the job, and RETURNS the result via `action = {...}` (run() returns it to the caller).
#
# Context params: clone_source (dict) | clone_source_uuid (str); clone_job_type; clone_job_datetime
# (None = unscheduled); clone_job_source (default 'Referral'); clone_line_items; clone_tos_default
# ('Maintenance' for Phase 5, else 'On Request'); clone_extra (dict of phase-specific overrides).
# Standardized for all callers: Country='US', JobSource default, carry alternating + Email,
# frequency default 'Unknown'. Workiz requires Address on create.
# Odoo server-action rules: no imports, no 'response'/'result' var names, requests is available.

WZ_TOKEN  = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WZ_SECRET = "sec_334084295850678330105471548"
WZ_BASE   = "https://api.workiz.com/api/v1/" + WZ_TOKEN

ctx = env.context
src = ctx.get('clone_source')
src_uuid = ctx.get('clone_source_uuid')
job_type = ctx.get('clone_job_type')
job_datetime = ctx.get('clone_job_datetime')
job_source = ctx.get('clone_job_source') or 'Referral'
line_items = ctx.get('clone_line_items')
tos_default = ctx.get('clone_tos_default') or 'On Request'
extra = ctx.get('clone_extra') or {}

s = src
if not s and src_uuid:
    src_resp = requests.get(WZ_BASE + "/job/get/" + str(src_uuid) + "/", timeout=20)
    sd = src_resp.json().get('data')
    s = sd[0] if isinstance(sd, list) and sd else sd
s = s or {}

cid = s.get('ClientId')
try:
    cid = int(str(cid or '').replace('CL-', '').strip() or 0)
except Exception:
    cid = s.get('ClientId')

payload = {
    'auth_secret':         WZ_SECRET,
    'ClientId':            cid,
    'FirstName':           str(s.get('FirstName') or ''),
    'LastName':            str(s.get('LastName') or ''),
    'Phone':               str(s.get('Phone') or s.get('Phone2') or ''),
    'Country':             'US',
    'State':               str(s.get('State') or 'CA'),
    'JobType':             job_type or str(s.get('JobType') or 'Windows Inside & Outside Plus Screens'),
    'type_of_service_2':   str(s.get('type_of_service_2') or s.get('type_of_service') or tos_default),
    'frequency':           str(s.get('frequency') or 'Unknown'),
    'confirmation_method': str(s.get('confirmation_method') or 'Cell Phone'),
    'ok_to_text':          str(s.get('ok_to_text') or 'Yes'),
    'JobSource':           str(s.get('JobSource') or job_source or 'Referral'),
    'alternating':         str(s.get('alternating') or ''),
}
for fld in ['Address', 'City', 'PostalCode', 'Unit', 'ServiceArea', 'Email']:
    if s.get(fld):
        payload[fld] = str(s.get(fld))
gate = s.get('gate_code') or s.get('GateCode')
if gate:
    payload['gate_code'] = str(gate)
if s.get('pricing'):
    payload['pricing'] = str(s.get('pricing'))
if s.get('JobNotes'):
    payload['JobNotes'] = str(s.get('JobNotes'))
sdt = str(s.get('JobDateTime') or '').strip()
if sdt:
    payload['last_date_cleaned'] = sdt[:10]
if job_datetime:
    payload['JobDateTime'] = job_datetime
if line_items is not None:
    payload['next_job_line_items'] = line_items
if extra:
    for k in extra:
        if extra[k] is not None:
            payload[k] = extra[k]

new_uuid = ''
create_status = 0
try:
    create_resp = requests.post(WZ_BASE + "/job/create/", json=payload, timeout=20)
    create_status = create_resp.status_code
    cdata = create_resp.json().get('data')
    if isinstance(cdata, list) and cdata:
        new_uuid = cdata[0].get('UUID') or ''
except Exception:
    new_uuid = ''

action = {
    'ok': bool(new_uuid),
    'workiz_uuid': new_uuid,
    'workiz_link': ("https://app.workiz.com/root/job/" + new_uuid + "/1") if new_uuid else '',
    'create_status': create_status,
    'payload': payload,
}
