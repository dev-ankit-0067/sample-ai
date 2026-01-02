# Sample Streamlit Login App

Minimal Streamlit app plus a tiny SQLite-backed authentication backend.

Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run

```bash
streamlit run app.py
```

Usage

- Open the app in your browser.
- Use "Sign up" to create a new local user (stored in a local SQLite DB `users.db`).
- Use "Login" to authenticate.

Migration

- If you previously used `users.json`, the app and the helper module will migrate entries into `users.db` automatically on first run.

Tests

- Quick test script: `python test_auth.py` will migrate (if needed), create a test user, and demonstrate authentication.

Notes

# Passwords are hashed with `bcrypt` and stored in `users.db` (SQLite).
# This is a simple demo. For production use, use a proper user management system, secure session handling, and never store secrets in plain files.

OpenAI integration

- You can provide an OpenAI API key via an environment variable or a `.env` file in the project root. Copy `.env.example` to `.env` and set your key:

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
```

- Example usage from Python (uses `langchain_query.ask_gpt`):

```python
from langchain_query import ask_gpt
print(ask_gpt("Write a short haiku about Python and AI."))
```
