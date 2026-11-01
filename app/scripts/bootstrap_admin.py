"""One-off command that grants the ADMIN role to an existing account.

    python -m app.scripts.bootstrap_admin user@example.com

There is deliberately no HTTP endpoint for this: it needs access to the
server's environment and database.
"""
import sys

from app.database.connection import SessionLocal
from app.models.user import User


def promote(db, email: str) -> bool:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return False
    user.role = "ADMIN"
    db.commit()
    return True


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m app.scripts.bootstrap_admin <email>", file=sys.stderr)
        return 2
    db = SessionLocal()
    try:
        if not promote(db, args[0]):
            print("No user with that email exists; register first.", file=sys.stderr)
            return 1
    finally:
        db.close()
    print("Role set to ADMIN.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
