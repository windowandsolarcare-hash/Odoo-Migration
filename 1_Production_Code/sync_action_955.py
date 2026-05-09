# Calls Phase 4 full sync on the Render app (header + lines + tasks).
# Replaces the old 289-line local implementation — Render handles all logic.

_url = 'https://wsc-field-assistant.onrender.com/owner/api/sync/phase4'
_body = '{"so_id": ' + str(record.id) + ', "secret": "wsc-daily-sync-2026"}'

_api_resp = requests.post(
    _url,
    data=_body,
    headers={'Content-Type': 'application/json'},
    timeout=60
)

_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if _api_resp.status_code == 200:
    _result = _api_resp.json()
    _ok = _result.get('ok', False)
    _msg = _result.get('message', 'Synced')
    _fields = _result.get('fields_updated', 0)
    _tasks = _result.get('tasks_updated', 0)
    if _ok:
        record.message_post(body='✅ [' + _ts + '] Phase 4 sync | fields: ' + str(_fields) + ' | tasks: ' + str(_tasks) + ' | ' + _msg)
    else:
        _err = _result.get('error') or _msg
        record.message_post(body='⚠️ [' + _ts + '] Phase 4 sync failed | ' + _err)
else:
    record.message_post(body='⚠️ [' + _ts + '] Phase 4 sync HTTP ' + str(_api_resp.status_code) + ' | ' + _api_resp.text[:200])

action = False
