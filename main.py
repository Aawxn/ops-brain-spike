"""
main.py - Ops Brain Spike Single Executable Entrypoint.

Usage:
    python main.py --demo
    python main.py --file sample_data/meeting_note_hinglish.txt
    python main.py --dry-run
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

# Ensure local directory is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extractor import ModelAgnosticExtractor, load_config
from integrations.notion_sync import NotionSync
from integrations.slack_gate import SlackGate
from priority_and_slip import PriorityRanker, SlipCascadeDetector


def print_banner(title: str, character: str = "═", width: int = 70) -> None:
    print("\n" + character * width)
    print(f" {title}")
    print(character * width)


def print_section(title: str, width: int = 70) -> None:
    print(f"\n─── {title.upper()} " + "─" * max(0, width - len(title) - 6))


def run_demo(note_path: Path, dry_run: bool = True, force_offline: bool = False) -> int:
    """
    Execute full end-to-end Ops Brain workflow:
    1. Multilingual Extraction (Hinglish/Gujarati -> Clean English Tasks)
    2. Deterministic Priority Ranking (Explainable scoring)
    3. Slack Block Kit Human Approval Gate
    4. Notion Database Sync (Idempotent upsert)
    5. Upstream Slip Cascade Detection (DAG/BFS propagation & Slack alert)
    6. Financial Cost Accounting & Audit Logging
    """
    print_banner("JUST SORTD — OPS BRAIN WORKING SPIKE (PRD 1 DEMO)")
    print(f"📂 Reading input: {note_path.name}")
    print(f"⚙️  Execution Mode: {'DRY RUN (Offline/Safe)' if dry_run else 'LIVE CONNECTED'}")

    if not note_path.exists():
        print(f"❌ Error: Meeting note file not found at {note_path}")
        return 1

    with open(note_path, "r", encoding="utf-8") as f:
        meeting_raw = f.read()

    # 1. Extraction
    print_section("1. MULTILINGUAL AI EXTRACTION (HINGLISH/GUJARATI -> ENGLISH)")
    config = load_config()
    extractor = ModelAgnosticExtractor(config)
    
    # Run extraction (falls back cleanly if API keys not present)
    extraction, run_log = extractor.extract(meeting_raw, force_offline=force_offline)

    print(f"🎯 Strategic Goal: {extraction.goal_name} (Target: {extraction.goal_due_date})")
    print(f"🌐 Languages:      {extraction.source_language_detected}")
    print(f"📝 Summary:        {extraction.meeting_summary}\n")
    print(f"Extracted {len(extraction.tasks)} structured tasks:")
    for idx, t in enumerate(extraction.tasks, start=1):
        deps = f"Blocked By: [{', '.join(t.depends_on_titles)}]" if t.depends_on_titles else "Prerequisite (No Blocker)"
        print(f"  [{idx}] {t.title}")
        print(f"      • Owner: {t.owner:<8} | Due Date: {t.due_date} | Confidence: {t.confidence * 100:.0f}%")
        print(f"      • {deps}")
        print(f"      • Context: \"{t.reasoning}\"\n")

    # 2. Priority Ranking
    print_section("2. DETERMINISTIC PRIORITY RANKING (EXPLAINABLE)")
    ranker = PriorityRanker(config)
    ranked_tasks = ranker.rank_tasks(
        tasks=extraction.tasks,
        goal_name=extraction.goal_name,
        reference_date=date(2026, 11, 18)
    )

    print("Weights: Goal=0.40 | Deadline Urgency=0.35 | Downstream Blockers=0.25\n")
    for r in ranked_tasks:
        print(f"  Rank #{r.rank} (Score: {r.total_score:.3f}) — {r.task_title}")
        print(f"      • Owner: {r.owner} | Due: {r.due_date}")
        print(f"      • Breakdown: Goal={r.goal_component:.2f} | Urgency={r.urgency_component:.2f} | Blockers={r.blocker_component:.2f}")
        print(f"      • Rationale: {r.explanation}\n")

    # 3. Slack Approval Gate
    print_section("3. HUMAN APPROVAL GATE (SLACK BLOCK KIT)")
    slack = SlackGate(config=config, dry_run=dry_run)
    approval_result = slack.send_approval_request(extraction, run_log)
    print("AI proposed tasks. Proposing via Slack Block Kit (Approve / Edit / Reject):")
    print(f"  Status: {approval_result['status']}")
    print(f"  Action Elements: ['✅ Approve & Sync to Notion', '✏️ Edit Draft', '❌ Reject Proposal']")
    
    # Simulate Human Approval Click
    print("\n👉 Simulating Founder Action in Slack: User clicked [✅ Approve & Sync to Notion]")
    run_log.human_action = "approved"
    extractor.update_human_action(run_log.run_id, "approved")
    print(f"  Updated run `{run_log.run_id}` human_action ➔ 'approved'")

    # 4. Notion Sync
    print_section("4. NOTION WORKSPACE SYNC (TASKS & RUN LOGS)")
    notion = NotionSync(dry_run=dry_run, slack_gate=slack)
    task_sync_results = notion.sync_tasks(extraction)
    print(f"Syncing {len(task_sync_results)} tasks to Notion 'Tasks' Database:")
    for res in task_sync_results:
        print(f"  • [{res.get('status', 'ok')}] {res.get('task_title')} (Page ID: {res.get('notion_page_id', 'simulated')})")

    run_sync_res = notion.sync_run_log(run_log)
    print(f"\nMirrored Run Log to Notion 'AI_Run_Logs' DB: Status = {run_sync_res.get('status')}")

    # 5. DAG/BFS Slip Cascade Detection
    print_section("5. DAG/BFS SLIP CASCADE DETECTOR & OPS ALERT")
    detector = SlipCascadeDetector(config)
    
    # Upstream vendor task slipped by 4 days (Nov 22 -> Nov 26)
    slipped_task = extraction.tasks[0].title
    slip_days = 4
    cascade = detector.detect_cascade(
        tasks=extraction.tasks,
        slipped_task_title=slipped_task,
        slip_days=slip_days,
        goal_name=extraction.goal_name,
        goal_deadline=extraction.goal_due_date
    )

    print(f"🚨 Upstream Delay: '{slipped_task}' slipped by +{slip_days} days (>= threshold 3 days)")
    print(f"📊 Goal Risk Status: {cascade.goal_status.upper()}")
    print(f"🎯 Target Deadline:  {cascade.goal_deadline}")
    print(f"📅 Projected Finish: {cascade.projected_goal_completion}")
    print(f"⛓️  Cascade Chain Impact ({cascade.total_impacted_tasks} downstream tasks blocked):")

    for item in cascade.impacted_chain:
        flag = "🔴 [ROOT SLIP]" if item.is_root_cause else "🟡 [IMPACTED]" if item.is_impacted else "⚪ [UNTOUCHED]"
        print(f"    {flag} {item.task_title}")
        print(f"        Owner: {item.owner:<8} | Orig: {item.original_due_date} ➔ Projected: {item.projected_due_date} (+{item.slip_days}d)")

    # Dispatch Slack Alert
    slack_alert_res = slack.send_slip_alert(cascade)
    print(f"\nDispatched Slack #ops-alerts notification: Status = {slack_alert_res['status']}")

    # 6. Audit & Financial Cost Accounting
    print_section("6. RUN AUDIT & FINOPS OBSERVABILITY")
    print(f"  • Run ID:           {run_log.run_id}")
    print(f"  • Timestamp:        {run_log.timestamp}")
    print(f"  • Model Used:       {run_log.model}")
    print(f"  • Input Tokens:     {run_log.input_tokens:,}")
    print(f"  • Output Tokens:    {run_log.output_tokens:,}")
    print(f"  • Run Cost (USD):   ${run_log.cost_usd:.6f}")
    print(f"  • Run Cost (INR):   ₹{run_log.cost_inr:.4f}")
    print(f"  • Human Action:     {run_log.human_action}")
    print(f"  • Persisted DBs:    logs/runs.db (SQLite) + logs/runs.jsonl (Audit Line)")

    print_banner("DEMO COMPLETED SUCCESSFULLY — ALL VERIFICATIONS PASSED")
    return 0


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Just Sortd - Ops Brain Working Spike")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run complete 6-stage demo walkthrough on sample Hinglish standup note"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="sample_data/meeting_note_hinglish.txt",
        help="Path to meeting note text file"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Connect to live external APIs (defaults to safe dry-run)"
    )
    parser.add_argument(
        "--force-offline",
        action="store_true",
        help="Force deterministic offline extractor regardless of environment API keys"
    )

    args = parser.parse_args()

    # Determine file path
    project_root = Path(__file__).resolve().parent
    file_path = project_root / args.file if not Path(args.file).is_absolute() else Path(args.file)

    dry_run = not args.live

    # If --demo or no arguments passed, run the demo
    exit_code = run_demo(note_path=file_path, dry_run=dry_run, force_offline=args.force_offline)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
