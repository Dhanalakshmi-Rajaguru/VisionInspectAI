from backend.ml.severity import assess_quality


def test_manual_review_when_confidence_below_70():
    result = assess_quality(
        defect_type="bent_lead",
        classification_confidence=65,
        severity_score=45.63,
        severity_level="Medium",
        recommended_action="Review",
    )

    assert result["quality_status"] == "MANUAL_REVIEW"
    assert result["recommended_action"] == "MANUAL_REVIEW"
    assert result["manual_review"] is True


def test_no_manual_review_at_70_percent():
    result = assess_quality(
        defect_type="bent_lead",
        classification_confidence=70,
        severity_score=45.63,
        severity_level="Medium",
        recommended_action="Review",
    )

    assert result["quality_status"] == "REVIEW"
    assert result["recommended_action"] == "Review"
    assert result["manual_review"] is False