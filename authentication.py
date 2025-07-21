from datetime import datetime, timedelta


# --- Authentication/Rate Limiting Utilities ---
def check_app_expiration(APP_EXPIRATION_DATE):
    """Disable app after expiration date"""
    if datetime.now() > APP_EXPIRATION_DATE:
        st.error("This application has expired and is no longer accessible.")
        st.stop()


def init_rate_limiting():
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = {}
    if "last_attempt_time" not in st.session_state:
        st.session_state.last_attempt_time = {}


def check_rate_limit(username, max_attempts=5, lockout_minutes=15):
    """Basic rate limiting for login attempts"""
    now = datetime.now()
    if username in st.session_state.login_attempts:
        attempts = st.session_state.login_attempts[username]
        last_attempt = st.session_state.last_attempt_time.get(username)
        if last_attempt and now - last_attempt < timedelta(minutes=lockout_minutes):
            if attempts >= max_attempts:
                st.error(
                    f"Too many login attempts. Please try again in {lockout_minutes} minutes."
                )
                return False
    return True


def record_login_attempt(username, success=False):
    """Record login attempt for rate limiting"""
    now = datetime.now()
    if username not in st.session_state.login_attempts:
        st.session_state.login_attempts[username] = 0
    if not success:
        st.session_state.login_attempts[username] += 1
        st.session_state.last_attempt_time[username] = now
    else:
        # Reset on successful login
        st.session_state.login_attempts[username] = 0


import streamlit as st
import streamlit_authenticator as stauth
from configuration import (
    credentials,
    COOKIE_EXPIRY_DAYS,
    COOKIE_KEY,
)


def get_authenticator():
    """Create and return a configured authenticator object."""
    # NOTE: This constructor signature is correct for streamlit-authenticator v0.1.5
    # pylint: disable=no-value-for-parameter
    return stauth.Authenticate(
        credentials, "interview_panel_cookie", COOKIE_KEY, COOKIE_EXPIRY_DAYS
    )


def authenticate_user():
    """
    Handle login, rate limiting, and return (name, authentication_status, username, authenticator).
    This function manages login attempts, error/warning messages, and returns authentication info.
    """
    authenticator = get_authenticator()

    # FIXED: streamlit-authenticator 0.1.5 syntax
    name, authentication_status, username = authenticator.login("Login", "main")

    # Handle authentication with rate limiting
    if authentication_status is False:
        st.error("Username/password is incorrect")
        if username:
            record_login_attempt(username, success=False)
            # Check rate limiting after failed login
            if not check_rate_limit(username):
                st.stop()
    # Do not show warning here; let main app handle it to avoid duplicate messages

    if authentication_status:
        # Record successful login
        record_login_attempt(username, success=True)
        # Check rate limiting before proceeding
        if not check_rate_limit(username):
            st.stop()
        return name, authentication_status, username, authenticator
    else:
        # Return authentication info even if not authenticated
        return name, authentication_status, username, authenticator


def logout(authenticator):
    """Logout function to be called in the sidebar."""
    # FIXED: streamlit-authenticator 0.1.5 syntax
    authenticator.logout("Logout", "sidebar")
