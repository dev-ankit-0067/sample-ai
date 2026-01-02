import json
from pathlib import Path
import bcrypt

USERS_FILE = Path(__file__).parent / "users.json"


def load_users():
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=2))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def create_user(username: str, password: str):
    users = load_users()
    if username in users:
        return False, "User already exists"
    users[username] = hash_password(password)
    save_users(users)
    return True, "User created successfully"


def authenticate_user(username: str, password: str) -> bool:
    users = load_users()
    hashed = users.get(username)
    if not hashed:
        return False
    return check_password(password, hashed)
