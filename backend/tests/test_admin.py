from backend.app.models.admin import AdminAccount
from backend.app.security.auth import hash_password

def test_admin_auth_and_protected_routes(client, db_session):
    # Ensure test admin exists
    admin = db_session.query(AdminAccount).filter(AdminAccount.username == "test_superadmin").first()
    if not admin:
        admin = AdminAccount(
            username="test_superadmin",
            email="superadmin@test.gov.in",
            hashed_password=hash_password("SuperSecretPass123!"),
            role="superadmin",
            is_active=True
        )
        db_session.add(admin)
        db_session.commit()

    # 1. Invalid login
    bad_login = client.post("/api/admin/login", json={
        "username_or_email": "test_superadmin",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 2. Valid login
    login_res = client.post("/api/admin/login", json={
        "username_or_email": "test_superadmin",
        "password": "SuperSecretPass123!"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Access without token should fail
    unauth = client.get("/api/admin/verification-queue")
    assert unauth.status_code == 401

    # 4. Access with token should succeed
    auth_res = client.get("/api/admin/verification-queue", headers=headers)
    assert auth_res.status_code == 200
    assert "pending_schemes" in auth_res.json()

    # 5. Access audit logs
    logs_res = client.get("/api/admin/audit-logs", headers=headers)
    assert logs_res.status_code == 200
