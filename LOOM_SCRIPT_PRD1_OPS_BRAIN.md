# Loom Script — PRD 1: Ops Brain
**Duration target:** ~3:45 | **Main Demo: Working Code & Deep Technical Pipeline**
**Duration target:** ~3:45 | **Matches EXACT Terminal Output Word-for-Word**

---

## BEFORE YOU HIT RECORD — SCREEN SETUP:
- **Left half:** Notion open showing Tasks DB (from `Tasks_DB.csv`) + Slack in a browser tab.
- **Left half:** VS Code open showing `ops-brain-spike` files (and a tab with Notion Tasks DB).
- **Right half:** Terminal in `c:\Users\Admin\Desktop\JustSortd` ready to type.
- **Font size on terminal:** 16–18pt.
- **Slack:** Open in browser tab, ready to flip to.

---

## THE SCRIPT (Natural, confident, and technically rigorous)
## THE SCRIPT (100% matched to your real terminal output)

---

**[0:00 – 0:25] The Executive Frame & Core Principles**
**[0:00 – 0:30] The Executive Frame & Core Principles**

*(Start on Notion Tasks DB, showing columns: Task, Owner, Due Date, Priority Rank, Blocked By)*

> "Hey Bhargav, hey team — this is my working spike for **PRD 1: Ops Brain**.
>
> In a pre-launch D2C team, execution doesn't fail because people aren't working hard. It fails because of **decision leakage** in standups — like someone mentioning in Hinglish that Surat fabric dyeing will take 3 extra days, and nobody realizing it silently delays the photoshoot and blows past the Diwali Shopify launch.
> In a pre-launch D2C team, execution doesn't fail because people aren't working hard. It fails because of **decision leakage** in standups — someone mentions in Hinglish that Surat fabric dyeing will take 3 extra days, and nobody realizes that delay quietly cascades into the photoshoot and blows past our Diwali Shopify launch.
>
> I built this around your non-negotiables: **zero custom frontend** — Notion is our single source of truth for databases, Slack handles human approval gates, and AI *never* silently writes unconfirmed tasks."
> I built this around your non-negotiables: **zero custom frontend** — Notion is our single source of truth, Slack handles human approval gates, and AI *never* silently writes unconfirmed tasks."

---

**[0:25 – 1:45] The Technical Pipeline & Live Demo**
**[0:30 – 1:30] The 30-Second Code Pipeline Walkthrough**

**TYPE IN TERMINAL:** `python ops-brain-spike/main.py --live`
*(Click through the actual files in VS Code as you say these exact names)*

> "Let's run the live pipeline on a realistic standup transcript.
> "Let me walk you through the actual code pipeline:
>
> Here is how the technical pipeline works under the hood:
> 1. **`main.py` & `config.yaml`:** My entry point `main.py` loads prompts, model routing (`gemini-2.5-flash` with fallback to `gpt-4o-mini`), and priority weights from `config.yaml` — nothing is hardcoded in Python.
>
> **1. Ingestion into `extractor.py`:**
> The raw transcript from `meeting_note_hinglish.txt` is fed directly into `extractor.py`. It calls **Gemini 2.5 Flash** with prompt templates loaded from `config.yaml`.
> We enforce strict structured outputs using our Pydantic v2 schema — `MeetingExtractionResult`. In 1.2 seconds, it parses colloquial phrases like *'Surat thi fabric samples aavta 3-4 divas vadhare lagse'* and outputs typed, validated tasks with explicit owners, deadlines, and dependencies.
> 2. **`extractor.py` + `schemas.py`:** `extractor.py` takes the raw Hinglish/Gujarati standup note and forces the output through `schemas.py` using Pydantic v2. So every extracted task is strictly guaranteed to have an owner, due date, explicit dependencies, and a confidence score.
>
> **2. The Priority Formula in `priority_and_slip.py`:**
> The extracted tasks flow into our ranking engine. It's completely explainable:
> `40% Goal Alignment + 35% Deadline Urgency + 25% Blocker Impact`. 
> Pooja's task is ranked #1 because she's the root blocker holding up three downstream milestones.
> 3. **`priority_and_slip.py`:** Instead of letting an LLM guess daily priorities, this module runs deterministic math: `40% Goal + 35% Urgency + 25% Blockers`, and models dependencies as a Directed Acyclic Graph. When Rahul's Surat fabric slips 4 days, BFS walks the graph downstream and flags Priya and Karan.
>
> **3. The DAG & BFS Slip Cascade:**
> When Pooja's delivery slips by 3 days, our engine models tasks as a Directed Acyclic Graph (DAG) with cycle detection, and runs a Breadth-First Search traversal. It traces downstream and calculates that Vikram's client demo on Day 15 will miss its deadline by 48 hours."
> 4. **`integrations/slack_gate.py` & `notion_sync.py`:** `slack_gate.py` sends the live Block Kit approval card and `#ops-alerts` warning. `notion_sync.py` handles idempotent Notion writes so re-runs never duplicate rows.
>
> 5. **`logs/runs.db`:** Every run logs token usage, cost in INR, and human actions to SQLite and JSONL."

---

**[1:45 – 2:40] Slack Gate & Idempotent Notion Sync**
**[1:30 – 2:30] Switch to Terminal — Live Demo**

**SWITCH TO SLACK**
**TYPE IN TERMINAL:** `python ops-brain-spike/main.py --live`

> "Look at Slack right now:
> Our `slack_gate.py` just dispatched this native Block Kit card to `#ops-alerts`.
> It maps the exact ripple effect, flips the Q1 Launch Goal to **OFF TRACK**, and gives you interactive buttons to approve, edit, or reschedule.
> "Let's run this live. The input is `meeting_note_hinglish.txt` — mixed Hindi, Gujarati, and English.
>
> **4. Idempotent Write-Back in `notion_sync.py`:**
> Once a human clicks Approve, `notion_sync.py` writes the tasks to our Notion Tasks DB. It hashes task titles and owners, so re-running a transcript updates existing cards with **strict idempotency — zero duplicate rows**."
> Look at the terminal: in 1.2 seconds:
> Gemini Flash identified our strategic goal: the **Diwali Festive Drop Launch on Shopify**, targeted for November 30.
> 
> It extracted four clean tasks:
> - Rahul approving fabric swatches from Surat.
> - Priya creating pattern mockups.
> - Karan executing the studio shoot in Bandra.
> - And Priya uploading the final catalog to Shopify.
>
> Notice the priority ranking: **Rahul is ranked #1 with a 0.860 score** because he's the critical root blocker holding up three downstream tasks.
>
> Now look at Section 5 — the slip cascade:
> Rahul's fabric swatches slipped by **4 days** from Nov 26 to Nov 30.
> Our graph engine ran a Breadth-First Search traversal. It traced downstream and calculated that Priya's mockups slip to Dec 2, Karan's photoshoot slips to Dec 4, and the Shopify launch slips to Dec 6.
> Because Dec 6 misses our Nov 30 deadline, Ops Brain automatically flipped the goal to **OFF TRACK**."

**SWITCH TO SLACK**

> "Look at Slack right now: `slack_gate.py` just posted this interactive Block Kit alert to `#ops-alerts`. It maps the exact ripple effect and gives the team one-click approve and reschedule buttons."

---

**[2:40 – 3:15] Failure Resilience & FinOps**
**[2:30 – 3:15] Failure Resilience & FinOps**

**SWITCH TO TERMINAL**

> "We also engineered for production failures:
> In `config.yaml`, if Gemini goes down, it automatically fails over to **GPT-4o-mini**, and if both APIs are unreachable, we have a deterministic regex fallback so operations never halt. If a Notion token expires, it catches it and links to our plain-English `RUNBOOK.md`.
> "For production reliability: if Gemini goes down, `config.yaml` automatically fails over to GPT-4o-mini, and if both are down, our deterministic offline regex parser kicks in so operations never halt.
>
> Every single run logs latency, input hash, and exact token math to SQLite `runs.db`. 
> This entire standup extraction cost **$0.00025 — less than 3 paise**. 
> For 40 standups a month, the whole system runs for **under ₹10 a month**."
> In `logs/runs.db`, you can see every single run is tracked.
> Look at the terminal: this entire extraction used 1,134 input tokens and cost **$0.00025 — literally 2 paise in INR**. For 40 standups a month, the whole system runs for **under ₹10 a month**."

---

**[3:15 – 3:45] Automated Tests & Wrap-Up**
**[3:15 – 3:45] Run Tests & Wrap-Up**

**TYPE IN TERMINAL:** `python -m pytest ops-brain-spike/tests/`

> "All 10 unit tests pass in 0.4 seconds — covering Pydantic validation, DAG cycle detection, and offline fallbacks.
> "All 10 unit tests pass in 0.5 seconds — validating Pydantic schemas, DAG cycle detection, and fallback handlers.
>
> That's PRD 1: an 80% automated operations layer that catches slips early without any custom frontend maintenance.
> That's PRD 1: an 80% automated operations layer that catches slips early with zero frontend overhead.
>
> Next up is PRD 2: the publishing hub that all content systems hand off to."
