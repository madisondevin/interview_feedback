"""
UI logic for feedback forms, feedback tabs, and feedback table rendering.
"""

import streamlit as st
from datetime import datetime
import pandas as pd

from feedback_storage import save_feedback, get_feedback_status
from configuration import RATING_OPTIONS


def format_timestamp(ts):
    """
    Format an ISO timestamp string as mm/dd/yy hh:mm for display in the UI.
    Returns the original string if parsing fails.
    """
    if not ts:
        return ""
    try:
        return datetime.fromisoformat(ts).strftime("%m/%d/%y %H:%M")
    except ValueError:
        return ts


def render_feedback_table(feedback, criteria_dict, panelist=None):
    """
    Render a feedback summary table for a given feedback dict and criteria.
    Shows panelist, criteria, rating, and notes in a dataframe.
    """
    rows = []
    for crit in criteria_dict.keys():
        rows.append(
            {
                "Panelist": panelist if panelist else "",
                "Criteria": crit,
                "Rating": feedback.get("criteria_ratings", {}).get(crit, ""),
                "Notes": feedback.get("criteria_notes", {}).get(crit, ""),
            }
        )
    st.caption("Double-click a Notes cell to view all the text if it is truncated.")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def show_feedback_form(candidate_id, candidate_choice, criteria, username):
    """
    Display the feedback form for a candidate, allowing the user to enter ratings and notes.
    Handles auto-saving and submission logic.
    """
    candidate_id_str = str(candidate_id)
    # Show candidate name at the top of the panel without link symbol using st.header
    st.header(f"Feedback for {candidate_choice}")
    user_feedback = (
        st.session_state["feedback"].get(username, {}).get(candidate_id_str, {})
    )

    already_submitted = get_feedback_status(user_feedback) == "submitted"
    if already_submitted:
        st.info(
            "You have submitted feedback for this candidate. You cannot edit your responses."
        )
        st.write("**Overall Rating:**", user_feedback.get("overall_rating", ""))
        st.write("**Overall Notes:**", user_feedback.get("overall_notes", ""))
        st.write(
            "**Last Modified At:**",
            format_timestamp(user_feedback.get("timestamp", "")),
        )
        render_feedback_table(user_feedback, criteria)
        return
    rating_options = RATING_OPTIONS
    overall_rating_key = f"overall_rating_{candidate_id_str}_{username}"
    overall_notes_key = f"overall_notes_{candidate_id_str}_{username}"
    prev_overall_rating = user_feedback.get("overall_rating", "I can't tell")
    prev_overall_notes = user_feedback.get("overall_notes", "")
    # Make Overall Rating header same size as criteria
    st.markdown("### Overall Rating")
    st.selectbox(
        "",
        rating_options,
        index=(
            rating_options.index(prev_overall_rating)
            if prev_overall_rating in rating_options
            else 0
        ),
        key=overall_rating_key,
    )
    st.text_area(
        "Overall Notes",
        value=prev_overall_notes,
        key=overall_notes_key,
    )
    ratings = {}
    notes = {}
    for crit, desc in criteria.items():
        st.markdown(f"### {crit}")
        if isinstance(desc, list):
            st.markdown(
                "<ul style='margin-bottom:0;'>"
                + "".join([f"<li>{item}</li>" for item in desc])
                + "</ul>",
                unsafe_allow_html=True,
            )
        else:
            st.caption(desc)
        crit_rating_key = f"r_{crit}_{candidate_id_str}_{username}"
        crit_notes_key = f"n_{crit}_{candidate_id_str}_{username}"
        prev_crit_rating = user_feedback.get("criteria_ratings", {}).get(
            crit, "I can't tell"
        )
        prev_crit_notes = user_feedback.get("criteria_notes", {}).get(crit, "")
        col1, col2 = st.columns([1, 2])
        with col1:
            ratings[crit] = st.selectbox(
                "Rating",  # Shorter label for compactness
                rating_options,
                index=(
                    rating_options.index(prev_crit_rating)
                    if prev_crit_rating in rating_options
                    else 0
                ),
                key=crit_rating_key,
            )
        with col2:
            notes[crit] = st.text_area(
                f"Notes for {crit}",
                value=prev_crit_notes,
                key=crit_notes_key,
            )
    if username not in st.session_state["feedback"]:
        st.session_state["feedback"][username] = {}
    prev_submitted = (
        get_feedback_status(
            st.session_state["feedback"][username].get(candidate_id_str, {})
        )
        == "submitted"
    )
    st.session_state["feedback"][username][candidate_id_str] = {
        "overall_rating": st.session_state[overall_rating_key],
        "overall_notes": st.session_state[overall_notes_key],
        "criteria_ratings": {
            crit: st.session_state[f"r_{crit}_{candidate_id_str}_{username}"]
            for crit in criteria
        },
        "criteria_notes": {
            crit: st.session_state[f"n_{crit}_{candidate_id_str}_{username}"]
            for crit in criteria
        },
        "timestamp": datetime.now().isoformat(),
        "submitted": prev_submitted,
    }
    save_feedback(
        st.session_state["feedback"], username, candidate_id_str, list(criteria.keys())
    )
    st.markdown(
        """
        <style>
        div.stButton > button:first-child {
            background-color: #21ba45 !important;
            color: white !important;
            font-size: 1.3em !important;
            padding: 0.75em 2.5em !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: bold;
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Submit Feedback", key=f"submit_{candidate_id_str}"):
        st.session_state["feedback"][username][candidate_id_str]["submitted"] = True
        save_feedback(
            st.session_state["feedback"],
            username,
            candidate_id_str,
            list(criteria.keys()),
        )
        st.success(
            "Feedback submitted! You can now view others' feedback for this candidate."
        )
        st.rerun()


def show_feedback_tabs(candidates, criteria, username):
    """
    Display feedback tabs for all candidates that have been submitted by the user.
    Shows both the user's and other panelists' feedback for each candidate.
    """
    st.header("View Candidate Feedback")

    for cid_str, cname in candidates.items():
        user_feedback = st.session_state["feedback"].get(username, {}).get(cid_str, {})
        if get_feedback_status(user_feedback) == "submitted":
            with st.expander(f"Feedback for {cname}"):
                st.subheader(f"Your Feedback for {cname}")
                if user_feedback:
                    st.write(
                        "**Overall Rating:**", user_feedback.get("overall_rating", "")
                    )
                    st.write(
                        "**Overall Notes:**", user_feedback.get("overall_notes", "")
                    )
                    st.write(
                        "**Last Modified At:**",
                        format_timestamp(user_feedback.get("timestamp", "")),
                    )
                    render_feedback_table(user_feedback, criteria, username)
                st.subheader("Other Panelists' Feedback")
                other_feedback_found = False
                for uname, fb in st.session_state["feedback"].items():
                    if (
                        uname != username
                        and cid_str in fb
                        and get_feedback_status(fb[cid_str]) == "submitted"
                    ):
                        other_feedback_found = True
                        st.write(f"**{uname}:**")
                        st.write(
                            "Overall Rating:", fb[cid_str].get("overall_rating", "")
                        )
                        st.write("Overall Notes:", fb[cid_str].get("overall_notes", ""))
                        st.write(
                            "Last Modified At:",
                            format_timestamp(fb[cid_str].get("timestamp", "")),
                        )
                        render_feedback_table(fb[cid_str], criteria, uname)
                        st.write("---")
                if not other_feedback_found:
                    st.write("No other feedback available yet.")
        else:
            st.info(f"Submit your feedback for {cname} to unlock this tab.")
