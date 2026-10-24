import sys
import os
import argparse
import secrets

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database import SessionLocal, Base, engine
from backend.app.models.admin import AdminAccount
from backend.app.security.auth import hash_password

def init_admin():
    parser = argparse.ArgumentParser(description="Create initial YojanaSetu administrator account securely.")
    parser.add_argument("--username", default=None, help="Administrator username")
    parser.add_argument("--email", default=None, help="Administrator email")
    parser.add_argument("--password", default=None, help="Administrator password (generated randomly if omitted)")
    parser.add_argument("--role", default="superadmin", help="Admin role: superadmin, reviewer, auditor")

    args = parser.parse_args()

    username = args.username or "admin_yojanasetu"
    email = args.email or "admin@yojanasetu.gov.in"
    password = args.password
    auto_generated = False

    if not password:
        password = secrets.token_urlsafe(16)
        auto_generated = True

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(AdminAccount).filter(
            (AdminAccount.username == username) | (AdminAccount.email == email)
        ).first()

        if existing:
            print(f"⚠️ Administrator '{username}' already exists (ID: {existing.id}, Role: {existing.role}).")
            return

        admin = AdminAccount(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            full_name="System Administrator",
            role=args.role,
            is_active=True
        )
        db.add(admin)
        db.commit()

        print("==================================================================")
        print("✅ YojanaSetu Administrator Account Initialized Successfully")
        print(f"Username: {username}")
        print(f"Email:    {email}")
        print(f"Role:     {args.role}")
        if auto_generated:
            print(f"Generated Password: {password}")
            print("👉 Store this password securely. It will not be shown again.")
        else:
            print("Password: [Provided by command argument]")
        print("==================================================================")

    finally:
        db.close()

if __name__ == "__main__":
    init_admin()
