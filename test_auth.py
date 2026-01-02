"""Small script to exercise auth_db functionality."""
from auth_db import migrate_from_json, create_user, authenticate_user, list_users


def run():
    print("Migrating from users.json (if present)...")
    migrated = migrate_from_json()
    print(f"Migrated: {migrated}")

    username = "testuser"
    password = "secret123"

    print(f"Creating user {username}...")
    ok, msg = create_user(username, password)
    print(ok, msg)

    print(f"Authenticating {username} with correct password...")
    print(authenticate_user(username, password))

    print(f"Authenticating {username} with wrong password...")
    print(authenticate_user(username, 'wrong'))

    print("Current users:")
    print(list_users())


if __name__ == '__main__':
    run()
