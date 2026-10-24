import json
from backend.app.models.admin import AdminAccount
from backend.app.security.auth import hash_password

def test_sources_endpoints(client):
    res = client.get("/api/sources")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3

    sum_res = client.get("/api/sources/summary")
    assert sum_res.status_code == 200
    s_data = sum_res.json()
    assert "total_sources" in s_data
    assert s_data["verified_count"] >= 3


def test_import_json_schemes(client, db_session):
    admin = db_session.query(AdminAccount).filter(AdminAccount.username == "test_superadmin").first()
    if not admin:
        admin = AdminAccount(
            username="test_superadmin",
            email="superadmin2@test.gov.in",
            hashed_password=hash_password("SuperSecretPass123!"),
            role="superadmin",
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()

    login = client.post("/api/admin/login", json={
        "username_or_email": "test_superadmin",
        "password": "SuperSecretPass123!"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    new_scheme_payload = [
        {
            "slug": "test-new-scheme",
            "official_name": "New Test National Scheme",
            "ministry": "Ministry of Electronics & IT",
            "is_central": True,
            "category": "livelihood",
            "numeric_benefit_value": 25000.0,
            "application_method": "online",
            "external_portal_name": "MeitY Portal",
            "external_portal_url": "https://meity.gov.in",
            "status": "pending_review",
            "rules": [
                {
                    "rule_code": "TEST_R1",
                    "field_name": "age_group",
                    "operator": "eq",
                    "target_value": "18 - 25 years",
                    "description": "Youth category"
                }
            ],
            "documents": [
                {
                    "document_code": "aadhaar",
                    "document_name": "Aadhaar Card",
                    "authority": "UIDAI",
                    "is_mandatory": True,
                    "steps": "Verify via OTP",
                    "turnaround": "Instant",
                    "estimated_cost": "Free"
                }
            ]
        }
    ]

    import_res = client.post("/api/admin/import/json", json=new_scheme_payload, headers=headers)
    assert import_res.status_code == 200
    assert import_res.json()["created_count"] == 1

    # Verify that the scheme was inserted
    scheme_res = client.get("/api/schemes/test-new-scheme")
    assert scheme_res.status_code == 200
    assert scheme_res.json()["slug"] == "test-new-scheme"
