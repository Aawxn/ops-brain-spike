"""
tests/test_extractor_mock.py - Tests for model-agnostic extraction and cost calculations.
"""

from pathlib import Path
from extractor import ModelAgnosticExtractor


def test_cost_calculation():
    extractor = ModelAgnosticExtractor()
    usd, inr = extractor.calculate_cost("gemini-2.5-flash", 1000, 500)
    assert usd > 0.0
    assert inr > 0.0
    # Gemini pricing: 1000 * 0.075 / 1M + 500 * 0.30 / 1M = 0.000075 + 0.000150 = 0.000225 USD
    assert round(usd, 6) == 0.000225


def test_mock_extraction_schema_compliance():
    extractor = ModelAgnosticExtractor()
    sample_path = Path(__file__).resolve().parent.parent / "sample_data" / "meeting_note_hinglish.txt"
    with open(sample_path, "r", encoding="utf-8") as f:
        text = f.read()

    result, run_log = extractor.extract(text, force_offline=True)

    assert result.goal_name is not None
    assert len(result.tasks) == 4
    assert result.tasks[0].owner == "Rahul"
    assert result.tasks[1].owner == "Priya"
    assert result.tasks[2].owner == "Karan"
    assert run_log.human_action == "pending"
    assert run_log.cost_usd > 0
