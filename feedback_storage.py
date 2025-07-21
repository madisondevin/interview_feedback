def get_feedback_status(feedback_entry):
    """
    Returns one of: 'submitted', 'in_progress', 'not_started' for a feedback entry dict.
    """
    if feedback_entry.get("submitted", False):
        return "submitted"
    if (
        feedback_entry.get("overall_rating")
        or feedback_entry.get("overall_notes")
        or (
            feedback_entry.get("criteria_ratings")
            and any(feedback_entry.get("criteria_ratings", {}).values())
        )
        or (
            feedback_entry.get("criteria_notes")
            and any(feedback_entry.get("criteria_notes", {}).values())
        )
    ):
        return "in_progress"
    return "not_started"


# Google Sheets integration
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SHEET_NAME = "streamlit_interview_feedback"
WORKSHEET_NAME = "Feedback"


import time
from gspread.exceptions import APIError


def get_gsheet(max_retries=5, delay=2):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    gc = gspread.authorize(creds)
    for attempt in range(max_retries):
        try:
            sh = gc.open(SHEET_NAME)
            worksheet = sh.worksheet(WORKSHEET_NAME)
            return worksheet
        except APIError as e:
            if (
                hasattr(e, "response")
                and getattr(e.response, "status_code", None) == 503
            ):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
            raise


def load_feedback():
    worksheet = get_gsheet()
    # Define the expected headers for the worksheet
    expected_headers = [
        "Interviewer",
        "Candidate_ID",
        "Candidate_Name",
        "Submitted",
        "Overall_Rating",
        "Overall_Notes",
        "Timestamp",
    ]
    # Add all possible criteria headers (for compatibility, but will be handled dynamically below)
    records = worksheet.get_all_records(expected_headers=expected_headers)
    feedback = {}
    for row in records:
        user = row.get("Interviewer", "")
        candidate_id = str(row.get("Candidate_ID", ""))
        if not user or not candidate_id:
            continue
        if user not in feedback:
            feedback[user] = {}
        # Extract criteria ratings and notes dynamically
        criteria_ratings = {}
        criteria_notes = {}
        for key, value in row.items():
            if key.startswith("CriteriaRating_"):
                crit = key.replace("CriteriaRating_", "")
                criteria_ratings[crit] = value
            elif key.startswith("CriteriaNotes_"):
                crit = key.replace("CriteriaNotes_", "")
                criteria_notes[crit] = value
        # Ensure 'submitted' is a real boolean (not string)
        submitted_val = row.get("Submitted", False)
        if isinstance(submitted_val, str):
            submitted = submitted_val.lower() == "true"
        else:
            submitted = bool(submitted_val)
        feedback[user][candidate_id] = {
            "candidate_name": row.get("Candidate_Name", ""),
            "overall_rating": row.get("Overall_Rating", ""),
            "overall_notes": row.get("Overall_Notes", ""),
            "submitted": submitted,
            "timestamp": row.get("Timestamp", ""),
            "criteria_ratings": criteria_ratings,
            "criteria_notes": criteria_notes,
        }
    return feedback


def save_feedback(feedback, user=None, candidate_id=None, criteria_list=None):
    """
    Save or update feedback for a single user/candidate pair, including all criteria ratings/notes.
    criteria_list: list of criteria names (strings) to save ratings/notes for.
    """
    worksheet = get_gsheet()
    if user is None or candidate_id is None or criteria_list is None:
        return

    fb = feedback.get(user, {}).get(candidate_id, {})
    # Prepare row and headers
    headers = [
        "Interviewer",
        "Candidate_ID",
        "Candidate_Name",
        "Submitted",
        "Overall_Rating",
        "Overall_Notes",
        "Timestamp",
    ]
    row = [
        user,
        candidate_id,
        fb.get("candidate_name", ""),
        bool(fb.get("submitted", False)),
        fb.get("overall_rating", ""),
        fb.get("overall_notes", ""),
        fb.get("timestamp", ""),
    ]
    # Add criteria ratings and notes
    for crit in criteria_list:
        headers.append(f"CriteriaRating_{crit}")
        row.append(fb.get("criteria_ratings", {}).get(crit, ""))
    for crit in criteria_list:
        headers.append(f"CriteriaNotes_{crit}")
        row.append(fb.get("criteria_notes", {}).get(crit, ""))

    # Ensure header row is present and correct at the top (row 1)
    sheet_values = worksheet.get_all_values()
    if not sheet_values:
        worksheet.insert_row(headers, 1)
    elif sheet_values[0] != headers:
        worksheet.update(f"A1:{chr(65+len(headers)-1)}1", [headers])

    # Find if this user/candidate_id already exists in the sheet
    records = worksheet.get_all_records(expected_headers=headers)
    found = False
    for idx, record in enumerate(records, start=2):
        if record.get("Interviewer") == user and str(record.get("Candidate_ID")) == str(
            candidate_id
        ):
            worksheet.update(f"A{idx}:{chr(65+len(headers)-1)}{idx}", [row])
            found = True
            break
    if not found:
        worksheet.append_row(row)
