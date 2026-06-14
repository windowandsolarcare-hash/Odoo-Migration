# Calendly booking CAPTURE (capture-first). Stores raw payload to a durable queue and
# returns fast (<10s) so Calendly marks delivered. A separate cron processes the queue
# idempotently (the real 6-phase booking). Odoo server-action rules: no imports; json,
# requests, datetime (module) available.
if isinstance(payload, str):
    payload = json.loads(payload)

raw = json.dumps(payload)

p = payload.get('payload') if isinstance(payload.get('payload'), dict) else payload
key = ''
if isinstance(p, dict):
    key = p.get('uri') or ''
    if not key:
        inv = p.get('invitee')
        if isinstance(inv, dict):
            key = inv.get('uri') or ''
    if not key:
        ev = p.get('scheduled_event') if isinstance(p.get('scheduled_event'), dict) else {}
        key = str(p.get('email') or '') + '|' + str(ev.get('start_time') or p.get('start_time') or '')
if not key:
    key = 'cal-' + str(datetime.datetime.now())

ICP = env['ir.config_parameter'].sudo()
ICP.set_param('calendly.raw.' + key, raw)

q_raw = ICP.get_param('calendly.queue') or '[]'
try:
    q = json.loads(q_raw)
except Exception:
    q = []
already_done = ICP.get_param('calendly.done.' + key)
if (key not in q) and (not already_done):
    q.append(key)
    ICP.set_param('calendly.queue', json.dumps(q))

ICP.set_param('calendly.last_raw', raw[:12000])
ICP.set_param('calendly.last_received', str(datetime.datetime.now()))
