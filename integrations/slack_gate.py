"""
integrations/slack_gate.py - Slack Block Kit Human Approval Gate & Ops Alerting.

Strict Build Principles satisfied:
- Human-in-the-loop: AI NEVER silently writes final tasks; proposes via Slack Block Kit (Approve / Edit / Reject)
- Working hours compliance: Checks IST Mon-Sat 10:00-19:00 from config.yaml
- Plain-English alerting to #ops-alerts on failures
- Seamless dry-run support for offline / demo execution
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

from schemas import ExtractedTask, MeetingExtractionResult, RunLog, SlipCascadeReport


def load_config() -> Dict[str, Any]:
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class SlackGate:
    """
    Slack Block Kit integration for human approval gates and operational alerts.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, dry_run: bool = True):
        self.config = config or load_config()
        self.dry_run = dry_run
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.ops_alerts_url = os.getenv("SLACK_OPS_ALERTS_WEBHOOK_URL") or self.webhook_url
        self.working_hours = self.config.get("working_hours", {
            "timezone": "Asia/Kolkata",
            "active_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "start_time": "10:00",
            "end_time": "19:00",
            "emergency_override": False
        })

    def is_within_working_hours(self) -> Tuple[bool, str]:
        """
        Check if the current moment is within IST working hours.
        Returns (is_active, explanation).
        """
        tz_name = self.working_hours.get("timezone", "Asia/Kolkata")
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = timezone.utc

        now_local = datetime.now(tz)
        current_day = now_local.strftime("%A")
        current_time_str = now_local.strftime("%H:%M")

        active_days = self.working_hours.get("active_days", [])
        start_time = self.working_hours.get("start_time", "10:00")
        end_time = self.working_hours.get("end_time", "19:00")

        if current_day not in active_days:
            return False, f"Current day ({current_day}) is outside active working days ({active_days})."

        if not (start_time <= current_time_str <= end_time):
            return False, f"Current time ({current_time_str} {tz_name}) is outside operational window ({start_time}-{end_time})."

        return True, f"Within active working window ({current_day} {current_time_str} {tz_name})."

    def build_approval_card(
        self,
        extraction: MeetingExtractionResult,
        run_log: RunLog
    ) -> Dict[str, Any]:
        """
        Generate Slack Block Kit payload for human approval of extracted tasks.
        Includes Approve, Edit, and Reject interactive buttons.
        """
        blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 AI Task Proposal: Human Approval Required",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Meeting Goal:* `{extraction.goal_name}` (Target: `{extraction.goal_due_date}`)\n"
                        f"*Language Detected:* {extraction.source_language_detected}\n"
                        f"*Summary:* {extraction.meeting_summary}\n"
                        f"*Run ID:* `{run_log.run_id}` | *Model:* `{run_log.model}` | *Cost:* `${run_log.cost_usd:.4f}` (~₹{run_log.cost_inr:.2f})"
                    )
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Proposed Action Items ({len(extraction.tasks)} tasks extracted):*"
                }
            }
        ]

        for idx, task in enumerate(extraction.tasks, start=1):
            deps = ", ".join(task.depends_on_titles) if task.depends_on_titles else "None (Prerequisite)"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{idx}. {task.title}*\n"
                        f"• *Owner:* `{task.owner}`  |  *Due Date:* `{task.due_date}`\n"
                        f"• *Prerequisites:* _{deps}_\n"
                        f"• *Confidence:* `{task.confidence * 100:.0f}%`  |  *Context:* \"_{task.reasoning}_\""
                    )
                }
            })

        blocks.append({"type": "divider"})
        blocks.append({
            "type": "actions",
            "block_id": f"approval_actions_{run_log.run_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✅ Approve & Sync to Notion", "emoji": True},
                    "style": "primary",
                    "value": f"approve_{run_log.run_id}",
                    "action_id": "btn_approve_notion"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✏️ Edit Draft", "emoji": True},
                    "value": f"edit_{run_log.run_id}",
                    "action_id": "btn_edit_draft"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "❌ Reject Proposal", "emoji": True},
                    "style": "danger",
                    "value": f"reject_{run_log.run_id}",
                    "action_id": "btn_reject_proposal"
                }
            ]
        })

        return {"blocks": blocks}

    def send_approval_request(
        self,
        extraction: MeetingExtractionResult,
        run_log: RunLog
    ) -> Dict[str, Any]:
        """
        Dispatch approval card to Slack or return dry-run payload.
        """
        card_payload = self.build_approval_card(extraction, run_log)

        if self.dry_run or not self.webhook_url or "XXXX" in self.webhook_url:
            return {
                "status": "simulated_dry_run",
                "delivered": False,
                "reason": "Dry run enabled or live Slack webhook not configured",
                "payload": card_payload
            }

        try:
            resp = requests.post(self.webhook_url, json=card_payload, timeout=8)
            resp.raise_for_status()
            return {"status": "delivered", "delivered": True, "http_status": resp.status_code}
        except Exception as e:
            self.alert_ops(f"Failed delivering approval card to Slack: {e!s}")
            return {"status": "error", "delivered": False, "error": str(e), "payload": card_payload}

    def send_slip_alert(self, slip_report: SlipCascadeReport) -> Dict[str, Any]:
        """
        Send slip cascade alert to Slack #ops-alerts.
        Checks working hours unless emergency override is triggered.
        """
        is_active, explanation = self.is_within_working_hours()
        emergency_override = self.working_hours.get("emergency_override", False)

        alert_payload = {"blocks": slip_report.slack_blocks}

        if not is_active and not emergency_override and slip_report.goal_status != "Off Track":
            return {
                "status": "deferred",
                "delivered": False,
                "reason": f"Outside IST working hours. {explanation}",
                "payload": alert_payload
            }

        if self.dry_run or not self.ops_alerts_url or "YYYY" in self.ops_alerts_url:
            return {
                "status": "simulated_dry_run",
                "delivered": False,
                "reason": "Dry run enabled or live Slack ops alerts webhook not configured",
                "payload": alert_payload
            }

        try:
            resp = requests.post(self.ops_alerts_url, json=alert_payload, timeout=8)
            resp.raise_for_status()
            return {"status": "delivered", "delivered": True, "http_status": resp.status_code}
        except Exception as e:
            return {"status": "error", "delivered": False, "error": str(e), "payload": alert_payload}

    def alert_ops(self, plain_english_message: str, runbook_ref: str = "RUNBOOK.md") -> bool:
        """
        Strict Build Principle #6: Plain-English Alerting.
        Dispatches actionable failure message with exact runbook remediation steps.
        """
        payload = {
            "text": f"🚨 *Ops Alert:* {plain_english_message}\n📖 *Runbook Guide:* See `{runbook_ref}` for resolution steps."
        }

        if self.dry_run or not self.ops_alerts_url or "YYYY" in self.ops_alerts_url:
            print(f"\n[OPS-ALERT (DRY-RUN)]: {plain_english_message} (Ref: {runbook_ref})")
            return True

        try:
            resp = requests.post(self.ops_alerts_url, json=payload, timeout=5)
            return resp.status_code == 200
        except Exception:
            return False
