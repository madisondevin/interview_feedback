import streamlit as st
from configuration import (
    criteria,
    ADMIN_USERS,
    APP_EXPIRATION_DATE,
    candidates,
)
from authentication import authenticate_user, check_app_expiration, init_rate_limiting
from feedback_storage import load_feedback
from user_panel import show_user_panel
from admin_panel import show_admin_dashboard


def initialize_app():
    st.set_page_config(layout="wide")
    check_app_expiration(APP_EXPIRATION_DATE)
    init_rate_limiting()


def initialize_session_state():
    if "feedback" not in st.session_state:
        st.session_state["feedback"] = load_feedback()


def calculate_criteria_avg_rating(
    criteria_ratings: dict, criteria_list, rating_map, FIRST_OPTION
) -> float:
    vals = []
    for crit in criteria_list:
        val = criteria_ratings.get(crit, "")
        if val != FIRST_OPTION and val in rating_map:
            vals.append(rating_map[val])
    return round(sum(vals) / len(vals), 2) if vals else ""


def main():
    initialize_app()
    initialize_session_state()
    _, authentication_status, username, authenticator = authenticate_user()
    if authentication_status:
        authenticator.logout("Logout", "sidebar")
        if username in ADMIN_USERS:
            show_admin_dashboard()
        else:
            show_user_panel(username, candidates, criteria)
    elif authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")


if __name__ == "__main__":
    main()
