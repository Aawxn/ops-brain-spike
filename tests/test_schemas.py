"""
tests/test_schemas.py - Unit tests for Pydantic v2 data models.
"""

import pytest
from pydantic import ValidationError

from schemas import ExtractedTask, MeetingExtractionResult, RunLog, TaskSlipStatus


def test_extracted_task_valid():
    task = ExtractedTask(
        title="Coordinate fabric swatches with Surat vendor",
        owner="Rahul",
        due_date="2026-11-26",
        goal_name="Diwali Drop",
        depends_on_titles=[],
        confidence=0.95,
        reasoning="Mentioned in standup"
    )
    assert task.owner == "Rahul"
    assert task.due_date == "2026-11-26"
    assert task.confidence == 0.95


def test_extracted_task_invalid_date():
    with pytest.raises(ValidationError):
        ExtractedTask(
            title="Bad Date Task",
            due_date="not-a-valid-date",
            confidence=0.9
        )


def test_extracted_task_confidence_bounds():
    with pytest.raises(ValidationError):
        ExtractedTask(
            title="Out of bounds confidence",
            due_date="2026-11-30",
            confidence=1.5  # Must be <= 1.0
        )


def test_meeting_extraction_result_valid():
    result = MeetingExtractionResult(
        goal_name="Launch Shopify Store",
        goal_due_date="2026-11-30",
        meeting_summary="Team pre-launch sync notes.",
        source_language_detected="Hindi + Gujarati + English",
        tasks=[
            ExtractedTask(
                title="Task 1",
                owner="Priya",
                due_date="2026-11-25",
                depends_on_titles=[]
            )
        ]
    )
    assert len(result.tasks) == 1
    assert result.goal_due_date == "2026-11-30"


def test_run_log_serialization():
    log = RunLog(
        run_id="run_test_123",
        timestamp="2026-11-20T19:00:00Z",
        input_hash="hash_abc_123",
        model="gemini-2.5-flash",
        input_tokens=500,
        output_tokens=250,
        cost_usd=0.000112,
        cost_inr=0.0096,
        human_action="pending",
        output_json='{"tasks": []}'
    )
    dumped = log.model_dump_json()
    assert "run_test_123" in dumped
    assert "pending" in dumped
