# Just Sortd — Ops Brain Non-Technical Runbook

> **Target Audience:** Ops leads, founders, and non-technical coordinators.  
> **Rule:** Every failure posts to `#ops-alerts` in plain English with an immediate link to this guide.

---

## Quick Reference: Alert Message to Action

| Plain-English Slack Alert | Root Cause | 2-Minute Fix | Escalation Contact |
|---|---|---|---|
| `"Notion API token expired or invalid"` | Notion integration token was rotated or permissions changed | 1. Go to **Notion Settings** > **Connections**.<br>2. Find "Just Sortd Ops Brain" integration.<br>3. Copy the token and paste it into `.env` as `NOTION_API_KEY`.<br>4. Restart service. | Ops Lead / Admin |
| `"Notion database ID not found during task sync"` | Database was renamed, unshared, or ID was miscopied | 1. Open your Notion **Tasks** or **AI_Run_Logs** database in browser.<br>2. Copy the 32-character string from the URL between the `/` and `?`.<br>3. Paste into `.env` as `NOTION_TASKS_DB_ID`.<br>4. Ensure connection is invited to the page. | Notion Workspace Admin |
| `"Slack webhook URL broken or inactive"` | Slack app incoming webhook was revoked or channel deleted | 1. Visit `api.slack.com/apps` > Incoming Webhooks.<br>2. Generate new webhook for `#ops-alerts`.<br>3. Update `SLACK_WEBHOOK_URL` in `.env`. | Slack Workspace Owner |
| `"AI quota exceeded, retrying with fallback"` | Gemini 2.5 Flash rate limit / quota hit | System automatically fails over to `gpt-4o-mini`. No immediate action needed. If fallback also fails, verify billing in Google AI Studio. | Tech Lead |
| `"AI returned malformed tasks (Schema error)"` | Meeting note was too ambiguous or non-standard | 1. The raw notes are preserved in `logs/runs.jsonl`.<br>2. Open `config.yaml` > `prompts.extraction_prompt`.<br>3. Add a clarifying example or re-run with clearer note formatting. | AI Engineer |
| `"Upstream delay of +X days exceeds threshold"` | Upstream vendor or team task slipped by ≥ 3 days | 1. Review the Slack alert message showing downstream affected owners.<br>2. Click **"Acknowledge Slip Alert"** or **"Open Notion Dependency Chain"**.<br>3. Reassign buffer or authorize emergency expediting. | Project Owner / Founder |

---

## How to Handle Operational Changes (Without Code)

### 1. Adjusting Priority Weights
If the founder feels urgency should matter more than downstream blockers:
1. Open `config.yaml`.
2. Locate `priority_weights`:
   ```yaml
   priority_weights:
     goal_weight: 0.40              # Strategic importance of the goal
     deadline_urgency: 0.35         # Closeness of deadline
     downstream_blocker_count: 0.25 # Number of tasks blocked
   ```
3. Update the decimal values (ensure they sum to 1.0).
4. Save file. Changes take effect on the very next run without touching any Python code.

### 2. Changing the Slip Alert Threshold
By default, any slip of **≥ 3 days** triggers an emergency cascade alert.
To change this threshold:
1. Open `config.yaml` > `slip_rules`.
2. Update `threshold_days: 3` to `threshold_days: 2` (stricter) or `4` (more lenient).

### 3. Modifying Working Hours / Alert Window (IST)
Alerts respect Indian Standard Time (IST) working hours:
1. Open `config.yaml` > `working_hours`.
2. Modify `start_time: "10:00"` and `end_time: "19:00"`.
3. Set `emergency_override: true` during launch weeks if Off-Track alerts must ring immediately at night.

---

## Verifying Health & Running Demo
To run a complete diagnostic test locally:
```bash
python ops-brain-spike/main.py --demo
```
If you see `DEMO COMPLETED SUCCESSFULLY — ALL VERIFICATIONS PASSED`, all systems and dry-run handlers are healthy.
