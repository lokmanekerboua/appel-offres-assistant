import json
from pathlib import Path

COMPANY_PROFILE_PATH = Path(__file__).parent.parent / "data" / "company_profile.json"


def check_eligibility(requirements: dict) -> dict:
    """
    Pure Python business logic — deterministic, no LLM call needed.
    Deliberately kept out of the LLM loop: cheaper, faster, and testable
    without mocking the API.
    """
    with open(COMPANY_PROFILE_PATH, encoding="utf-8") as f:
        profile = json.load(f)

    required_certs = requirements.get("required_certifications", []) or []
    company_certs = set(profile["certifications"])

    missing = [cert for cert in required_certs if cert not in company_certs]
    risk_notes = []

    if missing:
        risk_notes.append(f"Certifications manquantes : {', '.join(missing)}")

    budget_str = requirements.get("budget")
    if budget_str:
        digits = "".join(c for c in budget_str if c.isdigit())
        if digits and int(digits) > profile["max_project_budget_eur"]:
            risk_notes.append("Le budget du projet dépasse la capacité financière habituelle de l'entreprise")

    is_eligible = len(missing) == 0

    return {
        "is_eligible": is_eligible,
        "missing_certifications": missing,
        "risk_notes": risk_notes,
    }