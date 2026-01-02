import streamlit as st
import auth_db as auth
import backend_prompt as backend


def _set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            background-attachment: fixed;
        }
        .block-container {
            background: rgba(255,255,255,0.75);
            border-radius: 12px;
            padding: 1rem 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    _set_background()
    st.title("Chatbot")
    # Ensure DB initialized and migrate any existing JSON users
    try:
        migrated = auth.migrate_from_json()
        if migrated:
            st.info(f"Migrated {migrated} users from users.json")
    except Exception:
        pass

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # If not logged in, show only the auth screen
    if not st.session_state.logged_in:
        action = st.selectbox("Choose action", ["Login", "Sign up"])

        if action == "Sign up":
            st.subheader("Create Account")
            with st.form(key="signup_form"):
                username = st.text_input("Username", key="signup_user")
                password = st.text_input("Password", type="password", key="signup_pass")
                password2 = st.text_input("Confirm Password", type="password", key="signup_pass2")
                submit = st.form_submit_button("Create")

                if submit:
                    if not username or not password:
                        st.error("Please provide a username and password.")
                    elif password != password2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = auth.create_user(username, password)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

        else:
            st.subheader("Login")
            with st.form(key="login_form"):
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                submit = st.form_submit_button("Login")

                if submit:
                    if auth.authenticate_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.user = username
                        # refresh UI to show the prompt screen only
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        return

    # Logged-in screen: clear previous inputs and show prompt UI
    st.header(f"Welcome, {st.session_state.user}!")
    st.subheader("Model Prompt")
    prompt = st.text_area("Enter a prompt for the model", height=160)
    model = st.text_input("Model (optional)", value="")

    if st.button("Send Prompt"):
        if not prompt.strip():
            st.error("Please enter a prompt.")
        else:
            with st.spinner("Processing prompt..."):
                try:
                    resp = backend.process_prompt(prompt, model=model or None)
                    st.success("Response received")
                    st.text_area("Model response", value=resp, height=240)
                except Exception as e:
                    st.error(f"Error processing prompt: {e}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


if __name__ == "__main__":
    main()
