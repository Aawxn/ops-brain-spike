"""
tests/test_priority_and_slip.py - Tests for priority ranking and DAG/BFS slip cascade.
"""

from datetime import date
import pytest

from priority_and_slip import PriorityRanker, SlipCascadeDetector
from schemas import ExtractedTask


@pytest.fixture
def sample_4_task_chain():
    return [
        ExtractedTask(
            title="Task 1: Vendor fabric swatch approval",
            owner="Rahul",
            due_date="2026-11-26",
            goal_name="Diwali Festive Drop",
            depends_on_titles=[],
            confidence=0.95
        ),
        ExtractedTask(
            title="Task 2: Pattern mockups",
            owner="Priya",
            due_date="2026-11-28",
            goal_name="Diwali Festive Drop",
            depends_on_titles=["Task 1: Vendor fabric swatch approval"],
            confidence=0.92
        ),
        ExtractedTask(
            title="Task 3: Lookbook photoshoot",
            owner="Karan",
            due_date="2026-11-30",
            goal_name="Diwali Festive Drop",
            depends_on_titles=["Task 2: Pattern mockups"],
            confidence=0.90
        ),
        ExtractedTask(
            title="Task 4: Shopify catalog upload",
            owner="Priya",
            due_date="2026-12-02",
            goal_name="Diwali Festive Drop",
            depends_on_titles=["Task 3: Lookbook photoshoot"],
            confidence=0.97
        ),
    ]


def test_priority_ranking_stability(sample_4_task_chain):
    ranker = PriorityRanker()
    ranked = ranker.rank_tasks(
        tasks=sample_4_task_chain,
        goal_name="Diwali Festive Drop",
        reference_date=date(2026, 11, 18)
    )

    # Task 1 blocks all other 3 tasks, so it must rank #1
    assert ranked[0].task_title == "Task 1: Vendor fabric swatch approval"
    assert ranked[0].rank == 1
    assert ranked[0].blocker_component == 1.0  # Max blocker score
    assert "Rank #1" in ranked[0].explanation

    # Scores should be strictly descending
    scores = [r.total_score for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_slip_cascade_detector(sample_4_task_chain):
    detector = SlipCascadeDetector()
    report = detector.detect_cascade(
        tasks=sample_4_task_chain,
        slipped_task_title="Task 1: Vendor fabric swatch approval",
        slip_days=4,
        goal_name="Diwali Festive Drop",
        goal_deadline="2026-11-30"
    )

    assert report.threshold_triggered is True
    assert report.total_impacted_tasks == 3
    assert report.goal_status == "Off Track"
    assert report.projected_goal_completion > "2026-11-30"
    assert len(report.slack_blocks) > 0


def test_slip_cascade_below_threshold(sample_4_task_chain):
    detector = SlipCascadeDetector()
    report = detector.detect_cascade(
        tasks=sample_4_task_chain,
        slipped_task_title="Task 1: Vendor fabric swatch approval",
        slip_days=1,  # < threshold of 3 days
        goal_name="Diwali Festive Drop",
        goal_deadline="2026-12-10"  # Far in future
    )

    assert report.threshold_triggered is False
    assert report.goal_status == "On Track"
