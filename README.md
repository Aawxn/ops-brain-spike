# Just Sortd — Ops Brain (PRD 1)

> **Goal:** Autonomously turns messy multilingual standups (Hindi/Gujarati/English) into owned, dated Notion tasks, ranks them with an explainable priority formula, and catches supplier deadline slips via DAG/BFS before they break company launch goals.  
> 📄 **Core Documents:** [1-Page Build Plan](BUILD_PLAN.md) | [Ops Runbook](RUNBOOK.md) | [Loom Script](LOOM_SCRIPT_PRD1_OPS_BRAIN.md)

---

### 1. File Flow
* **`main.py` & `config.yaml`:** CLI entry point loads model routing (`gemini-2.5-flash` with `gpt-4o-mini` fallback), prompt templates, and priority weights without hardcoding.
* **`extractor.py` + `schemas.py`:** Parses colloquial standup transcripts into typed, validated tasks using Pydantic v2 schemas (`MeetingExtractionResult`).
* **`priority_and_slip.py`:** Runs deterministic priority math (`40% Goal + 35% Urgency + 25% Blockers`) and walks task dependencies via a Directed Acyclic Graph (DAG) + Breadth-First Search (BFS) when a task slips $\ge 3$ days.
* **`integrations/` & `logs/`:** `slack_gate.py` sends live Block Kit approval cards to `#ops-alerts`; `notion_sync.py` handles idempotent task write-backs; `logs/runs.db` tracks tokens, INR cost, and human actions.

---

### 2. Run Locally
```bash
# 1. Install dependencies & configure environment
pip install -r requirements.txt
cp .env.example .env

# 2. Run the live spike (or --demo for offline simulation)
python main.py --live

# 3. Run test suite
python -m pytest tests/
```

---

### 3. Integration Status
* **Gemini & Slack Webhooks:** Live and verified (dispatches native Block Kit proposal cards and slip cascade warnings directly to Slack).
* **Notion Database Sync:** Operates with strict idempotency using included `Tasks_DB.csv` and `Goals_DB.csv` schemas; runs safe payload dry-run sync (`notion_sync.py`), ready for live production database IDs.

---

### 4. Tests & Monthly Cost
* **Automated Tests:** **10 / 10 passed** (`python -m pytest tests/` in ~0.5s).
* **Monthly Running Cost:** **~$0.05 / month (~₹4.30 / mo)** for 40 standups (~600 tasks) on Gemini 2.5 Flash. Total team operating cost under ₹10/month.
