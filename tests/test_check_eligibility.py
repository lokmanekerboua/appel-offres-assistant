import json
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tools.check_eligibility import check_eligibility


FAKE_COMPANY_PROFILE = {
    "company_name": "Demo Corp",
    "certifications": ["ISO 9001", "MASE"],
    "sectors": ["énergie", "environnement"],
    "max_project_budget_eur": 5000000,
    "employee_count": 85,
}


def _mock_profile():
    return patch(
        "builtins.open",
        mock_open(read_data=json.dumps(FAKE_COMPANY_PROFILE)),
    )


def test_eligible_when_all_certifications_match():
    requirements = {
        "required_certifications": ["ISO 9001"],
        "budget": "450000 EUR",
    }
    with _mock_profile():
        result = check_eligibility(requirements)

    assert result["is_eligible"] is True
    assert result["missing_certifications"] == []
    assert result["risk_notes"] == []


def test_not_eligible_when_certification_missing():
    requirements = {
        "required_certifications": ["ISO 9001", "ISO 14001"],
        "budget": "450000 EUR",
    }
    with _mock_profile():
        result = check_eligibility(requirements)

    assert result["is_eligible"] is False
    assert "ISO 14001" in result["missing_certifications"]


def test_risk_note_when_budget_exceeds_capacity():
    requirements = {
        "required_certifications": ["ISO 9001"],
        "budget": "8500000 EUR",
    }
    with _mock_profile():
        result = check_eligibility(requirements)

    assert any("budget" in note.lower() for note in result["risk_notes"])


def test_eligible_with_no_certification_requirements():
    requirements = {
        "required_certifications": [],
        "budget": None,
    }
    with _mock_profile():
        result = check_eligibility(requirements)

    assert result["is_eligible"] is True