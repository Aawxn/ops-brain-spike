"""
schemas.py - Strict Pydantic v2 data models for Ops Brain Spike.

Strict Build Principles satisfied:
- Validated structured extraction (ExtractedTask, MeetingExtractionResult)
- Run Logging model capturing tokens, cost, latency, input hash, and human actions
- Slip cascade & priority ranking reporting contracts
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class ExtractedTask(BaseModel):
    """
    Individual structured task extracted from multilingual meeting notes.
    """
    title: str = Field(
        ...,
        description="Clean, action-oriented English verb phrase describing the task"
    )
    owner: str = Field(
        default="Unassigned",
        description="Name of the person accountable for execution (e.g. Rahul, Priya)"
    )
    due_date: str = Field(
        ...,
        description="Target completion date in ISO format YYYY-MM-DD"
    )
    goal_name: str = Field(
        default="General Operations",
        description="Business goal this task directly contributes to"
    )
    depends_on_titles: list[str] = Field(
        default_factory=list,
        description="Exact titles of prerequisite tasks that must complete before this can start"
    )
    confidence: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Model confidence score for this extraction (0.0 to 1.0)"
    )
    reasoning: str = Field(
        default="",
        description="Contextual quote and reasoning from the meeting note justifying owner/date/deps"
    )

    @field_validator("due_date")
    @classmethod
    def validate_due_date_format(cls, v: str) -> str:
        """Ensure date can be parsed as a valid ISO calendar date."""
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid date format '{v}'. Expected YYYY-MM-DD.")


class MeetingExtractionResult(BaseModel):
    """
    Full extraction payload returned by the LLM from a meeting note.
    """
    goal_name: str = Field(
        ...,
        description="Primary overarching strategic goal identified in the meeting"
    )
    goal_due_date: str = Field(
        ...,
        description="Deadline for the overarching goal in YYYY-MM-DD format"
    )
    meeting_summary: str = Field(
        ...,
        description="Crisp 2-sentence English summary of key decisions and bottlenecks"
    )
    source_language_detected: str = Field(
        default="English + Hindi + Gujarati",
        description="Linguistic composition detected in the source notes"
    )
    tasks: list[ExtractedTask] = Field(
        ...,
        min_length=1,
        description="List of extracted structured tasks"
    )


class PriorityScoreDetail(BaseModel):
    """
    Explainable breakdown of the deterministic priority score for a task.
    """
    task_title: str
    owner: str
    due_date: str
    rank: int
    total_score: float
    goal_component: float
    urgency_component: float
    blocker_component: float
    explanation: str


class TaskSlipStatus(BaseModel):
    """
    Status of an individual task in a slip cascade.
    """
    task_title: str
    owner: str
    original_due_date: str
    projected_due_date: str
    slip_days: int
    is_root_cause: bool = False
    is_impacted: bool = False
    blocked_by: list[str] = Field(default_factory=list)


class SlipCascadeReport(BaseModel):
    """
    Output of the DAG/BFS slip-cascade detector.
    """
    root_slipped_task: str
    slip_days: int
    goal_name: str
    goal_deadline: str
    projected_goal_completion: str
    goal_status: Literal["On Track", "At Risk", "Off Track"]
    threshold_triggered: bool
    total_impacted_tasks: int
    impacted_chain: list[TaskSlipStatus]
    summary_message: str
    slack_blocks: list[dict[str, Any]] = Field(default_factory=list)


class RunLog(BaseModel):
    """
    Audit record for every AI invocation.
    Captures input hash, token counts, exact financial cost in USD/INR, and human decision.
    """
    run_id: str = Field(..., description="Unique UUID for this execution run")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    input_hash: str = Field(..., description="SHA-256 hash of raw input text")
    model: str = Field(..., description="Model identifier used (e.g. gemini-2.5-flash)")
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    cost_inr: float = Field(default=0.0, ge=0.0)
    human_action: Literal["pending", "approved", "edited", "rejected"] = Field(
        default="pending",
        description="Human in the loop approval state"
    )
    output_json: str = Field(..., description="Raw or parsed JSON string of the model output")
    error: str | None = Field(default=None, description="Error message if run failed")
