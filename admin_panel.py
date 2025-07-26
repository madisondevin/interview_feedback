"""
Admin dashboard UI and logic for feedback completion matrix, feedback table, and Excel export.
"""

import streamlit as st
import pandas as pd
from io import BytesIO

from configuration import criteria, ADMIN_USERS, credentials, RATING_OPTIONS, candidates
from ui_feedback import format_timestamp
from feedback_storage import get_feedback_status


def calculate_criteria_avg_rating(
    criteria_ratings: dict, criteria_list, rating_map, FIRST_OPTION
) -> float:
    vals = []
    for crit in criteria_list:
        val = criteria_ratings.get(crit, "")
        if val != FIRST_OPTION and val in rating_map:
            vals.append(rating_map[val])
    return round(sum(vals) / len(vals), 2) if vals else ""


def export_feedback_to_excel(feedback_df, criteria_list, rating_options):
    """
    Export the feedback DataFrame to Excel with candidate and interviewer summaries.
    Returns the Excel file as bytes.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        feedback_df_sorted = feedback_df.sort_values(
            ["Candidate_Name", "Interviewer"], ascending=[True, True]
        )
        # Only write the DataFrame, which will write a single header row
        feedback_df_sorted.to_excel(writer, sheet_name="All_Feedback", index=False)
        # Candidate summary
        if not feedback_df.empty:
            candidate_summary = []
            for cname in feedback_df["Candidate_Name"].unique():
                cdf = feedback_df[feedback_df["Candidate_Name"] == cname]
                row = {
                    "Candidate_Name": cname,
                    "Count_Submitted_Reviews": len(cdf),
                }
                for r in rating_options[1:]:
                    row[f"Overall_Count_{r}"] = (cdf["Overall_Rating"] == r).sum()
                row["Overall_Notes"] = "; ".join(
                    [str(x) for x in cdf["Overall_Notes"] if x]
                )
                # Ensure numeric for mean calculation
                avg_col = pd.to_numeric(cdf["Criteria_Avg_Rating"], errors="coerce")
                row["Avg_Of_Interviewer_Avg"] = (
                    round(avg_col.mean(), 2) if not cdf.empty else ""
                )
                for crit in criteria_list:
                    for r in rating_options[1:]:
                        row[f"{crit}_Count_{r}"] = (cdf[f"{crit}_Rating"] == r).sum()
                candidate_summary.append(row)
            candidate_summary_df = pd.DataFrame(candidate_summary)
            candidate_summary_df.to_excel(
                writer, sheet_name="Candidate_Summary", index=False
            )
            interviewer_summary = []
            for interviewer in feedback_df["Interviewer"].unique():
                idf = feedback_df[feedback_df["Interviewer"] == interviewer]
                submitted_count = len(idf)

                def is_in_progress(row):
                    feedback_entry = (
                        st.session_state["feedback"]
                        .get(row["Interviewer"], {})
                        .get(str(row["Candidate_ID"]), {})
                    )
                    return get_feedback_status(feedback_entry) == "in_progress"

                started_count = idf.apply(is_in_progress, axis=1).sum()
                row = {
                    "Interviewer": interviewer,
                    "Count_Submitted_Reviews": submitted_count,
                    "Count_Started_Reviews": started_count,
                }
                for r in rating_options[1:]:
                    row[f"Count_Overall_Rating_{r}"] = (
                        idf["Overall_Rating"] == r
                    ).sum()
                interviewer_summary.append(row)
            interviewer_summary_df = pd.DataFrame(interviewer_summary)
            interviewer_summary_df.to_excel(
                writer, sheet_name="Interviewer_Summary", index=False
            )
    return output.getvalue()


def show_admin_dashboard():
    """
    Display the admin dashboard, including the feedback completion matrix and all feedback details.
    Shows summary tables and allows export to Excel.
    """
    st.header("Admin Dashboard", anchor=None)
    st.header("Feedback Completion Matrix", anchor=None)
    completion_data = []
    all_panelists = [u for u in credentials["usernames"] if u not in ADMIN_USERS]
    for panelist in all_panelists:
        row = {"Interviewer": panelist}
        user_feedback = st.session_state["feedback"].get(panelist, {})
        for cid_str, cname in candidates.items():
            feedback_entry = user_feedback.get(cid_str, {})
            status_code = get_feedback_status(feedback_entry)
            if status_code == "submitted":
                status = "✅ Submitted"
            elif status_code == "in_progress":
                status = "📝 In Progress"
            else:
                status = "❌ Not Started"
            last_modified = feedback_entry.get("timestamp", "")
            row[cname] = status
            row[f"{cname} Last Modified At"] = (
                format_timestamp(last_modified) if last_modified else ""
            )
        completion_data.append(row)
    if completion_data:
        completion_df = pd.DataFrame(completion_data)
        st.caption(
            "'In Progress' means feedback has been started but not submitted. 'Last Modified' shows the most recent save time."
        )
        st.dataframe(completion_df, use_container_width=True)

    st.header("All Feedback Details", anchor=None)
    feedback_data = []
    criteria_list = list(criteria.keys())
    FIRST_OPTION = RATING_OPTIONS[0] if RATING_OPTIONS else None
    rating_map = {r: i for i, r in enumerate(RATING_OPTIONS[1:])}
    for panelist, user_feedback in st.session_state["feedback"].items():
        for candidate_id_str, feedback in user_feedback.items():
            if not feedback.get("submitted", False):
                continue  # Only include submitted feedback
            candidate_name = candidates.get(
                candidate_id_str, f"Unknown_{candidate_id_str}"
            )
            row_data = {
                "Interviewer": panelist,
                "Candidate_ID": candidate_id_str,
                "Candidate_Name": candidate_name,
                "Overall_Rating": feedback.get("overall_rating", ""),
                "Overall_Notes": feedback.get("overall_notes", ""),
                "Last_Modified_At": feedback.get("timestamp", ""),
            }
            criteria_ratings = feedback.get("criteria_ratings", {})
            criteria_notes = feedback.get("criteria_notes", {})
            for criterion in criteria_list:
                val = criteria_ratings.get(criterion, "")
                row_data[f"{criterion}_Rating"] = val
                row_data[f"{criterion}_Notes"] = criteria_notes.get(criterion, "")
            row_data["Criteria_Avg_Rating"] = calculate_criteria_avg_rating(
                criteria_ratings, criteria_list, rating_map, FIRST_OPTION
            )
            feedback_data.append(row_data)
    feedback_df = pd.DataFrame(feedback_data)
    if not feedback_df.empty:
        if "Last_Modified_At" in feedback_df.columns:
            feedback_df["Last_Modified_At"] = feedback_df["Last_Modified_At"].apply(
                format_timestamp
            )
        st.caption("Double-click a Notes cell to view all the text if it is truncated.")
        cols = feedback_df.columns.tolist()
        if "Candidate_Name" in cols and "Interviewer" in cols:
            crit_cols = [
                c for c in cols if c.endswith("_Rating") and c != "Criteria_Avg_Rating"
            ]
            new_order = ["Candidate_Name", "Interviewer"]
            if "Criteria_Avg_Rating" in cols and crit_cols:
                first_crit = crit_cols[0]
                idx = cols.index(first_crit)
                for c in cols:
                    if c not in new_order and c != "Criteria_Avg_Rating":
                        new_order.append(c)
                new_order.insert(idx, "Criteria_Avg_Rating")
                feedback_df = feedback_df[
                    [col for col in new_order if col in feedback_df.columns]
                ]
            else:
                new_order += [c for c in cols if c not in new_order]
                feedback_df = feedback_df[new_order]
        st.dataframe(feedback_df, use_container_width=True)
        st.subheader("📤 Export to Excel", anchor=None)
        st.caption(
            "The Excel file will contain three sheets: (1) All submitted feedback, (2) summary by candidate with numeric averages, and (3) summary by interviewer."
        )
        try:
            excel_data = export_feedback_to_excel(
                feedback_df, criteria_list, RATING_OPTIONS
            )
            st.download_button(
                label="📋 Download as Excel",
                data=excel_data,
                file_name=f"interview_feedback_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except ImportError:
            st.error(
                "Excel export requires openpyxl. Install with: pip install openpyxl"
            )
