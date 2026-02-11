#!/usr/bin/env python3
"""
Create the initial admin user (e.g. for fresh Docker DB).
Run inside the app container:
  docker compose exec app python -m app.scripts.create_initial_admin
  docker compose exec app python -m app.scripts.create_initial_admin --password "YourSecurePassword"
Or set INITIAL_ADMIN_PASSWORD in the environment.
"""
import argparse
import getpass
import sys


def main():
    parser = argparse.ArgumentParser(description="Create initial admin user in DB and users.json")
    parser.add_argument("--username", default="admin", help="Admin username (default: admin)")
    parser.add_argument("--password", help="Admin password (or set INITIAL_ADMIN_PASSWORD, or you will be prompted)")
    args = parser.parse_args()

    password = args.password or sys.environ.get("INITIAL_ADMIN_PASSWORD")
    if not password:
        if sys.stdin.isatty():
            password = getpass.getpass("Enter admin password: ")
        else:
            print("No TTY. Use --password or set INITIAL_ADMIN_PASSWORD.", file=sys.stderr)
            sys.exit(1)
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Load DB so add_user and get_users use both DB and JSON
    from app.database import _load_database
    _load_database()

    from app.config import PRACTICE_DATA_DIR
    PRACTICE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    from app.auth import add_user
    from app.services.data_reader import get_users

    if args.username in get_users():
        print(f"User '{args.username}' already exists. Use the app to change the password if needed.")
        sys.exit(0)

    add_user(args.username, password, "admin", force_change=False)
    print(f"Admin user '{args.username}' created. You can log in at /login.")


if __name__ == "__main__":
    main()
