---
name: project_twilio_port_details
description: "The exact numbers + CSR/PIN/losing-account-SID to port DJ's Workiz business numbers onto his own Twilio account (from Workiz porting team 6/22/2026)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
---

**Porting DJ's Workiz phone numbers → his own Twilio account ([TWILIO_ACCOUNT_SID — in Render env]).** Workiz's porting team (porting@workiz.com, ticket "Window & Solar Care (25699) - US Port-Out Request Submitted") provided the port-out details 2026-06-22. A2P is now approved (2026-07-09) so the port is cleared to proceed.

**Numbers to port (7):**
- Local (require **PIN 9634**): 760-334-5315, 760-334-5350, 760-334-5355, 951-223-4602, 951-927-8680
- Toll-free (no PIN; Workiz approves via their Console): 800-283-8765, **855-245-2273** (DJ's main business line)

**Port credentials:**
- **Losing carrier = Workiz's Twilio account, SID `[TWILIO_ACCOUNT_SID — in Render env]`** (account number = last 8 of that SID; if the gaining form rejects letters, use last 8 digits only).
- **PIN: 9634** (local numbers).
- CSR on file: Twilio Inc, 548 Market St #14510, San Francisco, CA 94104.

**Workiz's instructions / gotchas:**
- DO NOT release the numbers from Workiz's Twilio account — they must stay ACTIVE for the port to succeed. Keep Workiz active until the port completes.
- Disable the emergency (E911) configuration on the numbers before submitting the port-out.
- Bulk: have the gaining carrier (Twilio, DJ's account) submit ALL numbers in ONE porting request.
- End-user submits the port to the gaining provider using their own LOA info + the Twilio account number/SID.

**Twilio side:** port ticket **27332980** (Rakesh Kumar, support+id00D20P-0165K@twilio.zendesk.com) has been held open; Rakesh said "give me all the details and approval and we'll proceed with transferring the number." Two parked Gmail drafts as of 2026-07-09: (1) reply to Rakesh "ready to proceed"; (2) DJ's reply to porting@workiz.com. AFTER port completes: add the ported numbers to messaging service MG9d920... sender pool (auto-registers to the approved A2P campaign) + wire voice catch-net. See [[project_twilio_a2p_and_entity]] [[project_twilio_port_from_workiz]].
