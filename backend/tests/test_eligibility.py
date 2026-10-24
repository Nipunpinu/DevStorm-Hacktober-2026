import pytest
from backend.app.schemas.eligibility import UserProfileInput

def test_eligibility_potential_match(client):
    """Citizen satisfying all rules for Post-Matric scholarship."""
    payload = {
        "profile": {
            "gender": "Female",
            "age_group": "18 - 25 years",
            "marital_status": "Single / Unmarried",
            "state": "Uttar Pradesh",
            "region_type": "Rural",
            "social_category": "OBC",
            "minority": "No",
            "disability_status": "None",
            "student_status": "Yes",
            "education_level": "Undergraduate (BA/BSc/BCom/BTech)",
            "bpl_status": "Yes",
            "family_income": "Below ₹1,00,000"
        },
        "language": "en"
    }
    response = client.post("/api/eligibility/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "schemes" in data
    assert data["total_active"] >= 4

    # Post-matric must be a potential_match
    pms = next((s for s in data["schemes"] if s["slug"] == "post-matric"), None)
    assert pms is not None
    assert pms["evaluation"]["status"] == "potential_match"
    assert pms["evaluation"]["is_match"] is True
    assert len(pms["evaluation"]["satisfied_conditions"]) >= 2
    assert len(pms["evaluation"]["violated_conditions"]) == 0


def test_eligibility_does_not_match(client):
    """Citizen not a student should NOT match Post-Matric scholarship."""
    payload = {
        "profile": {
            "student_status": "No",
            "social_category": "General",
            "family_income": "Above ₹8,00,000"
        },
        "language": "en"
    }
    response = client.post("/api/eligibility/check", json=payload)
    assert response.status_code == 200
    data = response.json()

    pms = next((s for s in data["schemes"] if s["slug"] == "post-matric"), None)
    assert pms is not None
    assert pms["evaluation"]["status"] == "does_not_match"
    assert pms["evaluation"]["is_match"] is False
    assert len(pms["evaluation"]["violated_conditions"]) > 0


def test_eligibility_needs_verification(client):
    """Missing key information must yield needs_verification, NOT an automatic failure."""
    payload = {
        "profile": {
            # Omit student_status, income, category
            "state": "Uttar Pradesh",
            "region_type": "Rural"
        },
        "language": "en"
    }
    response = client.post("/api/eligibility/check", json=payload)
    assert response.status_code == 200
    data = response.json()

    pms = next((s for s in data["schemes"] if s["slug"] == "post-matric"), None)
    assert pms is not None
    # Because user didn't violate any mandatory condition, but facts are missing
    assert pms["evaluation"]["status"] == "needs_verification"
    assert pms["evaluation"]["is_match"] is True
    assert len(pms["evaluation"]["missing_facts"]) > 0
    assert len(pms["evaluation"]["violated_conditions"]) == 0


def test_assessment_options(client):
    response = client.get("/api/eligibility/options")
    assert response.status_code == 200
    data = response.json()
    assert "genders" in data
    assert "age_groups" in data
    assert "social_categories" in data
    assert len(data["states"]) >= 10
