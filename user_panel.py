from feedback_storage import get_feedback_status
import streamlit as st
from ui_feedback import show_feedback_form, show_feedback_tabs


def select_candidate_main(candidates_dict):
    st.header("Select candidate", anchor=None)
    username = st.session_state.get("username")
    candidate_ids = list(candidates_dict.keys())
    options = []
    option_map = {}
    for cid_str in candidate_ids:
        cname = candidates_dict[cid_str]
        status = ""
        if username and "feedback" in st.session_state:
            feedback_entry = (
                st.session_state["feedback"].get(username, {}).get(cid_str, {})
            )
            status_code = get_feedback_status(feedback_entry)
            if status_code == "submitted":
                status = "✅ Submitted"
            elif status_code == "in_progress":
                status = "📝 In Progress"
            else:
                status = "❌ Not Started"
        label = f"{cname} {status}"
        options.append(label)
        option_map[label] = (cid_str, cname)
    selected_id = st.session_state.get("selected_candidate_id", candidate_ids[0])
    selected_label = None
    for label, (cid, _) in option_map.items():
        if cid == selected_id:
            selected_label = label
            break
    chosen_label = st.radio(
        "",
        options,
        index=options.index(selected_label) if selected_label else 0,
        horizontal=True,
        key="candidate_radio",
        label_visibility="collapsed",
    )
    cid_str, cname = option_map[chosen_label]
    st.session_state["selected_candidate_id"] = cid_str
    st.session_state["selected_candidate_name"] = cname
    return cid_str, cname


def show_user_panel(username, candidates, criteria):
    st.sidebar.title(f"Welcome {username}")
    candidate_id_str, candidate_choice = select_candidate_main(candidates)

    user_feedback = (
        st.session_state["feedback"].get(username, {}).get(candidate_id_str, {})
    )
    if get_feedback_status(user_feedback) != "submitted":
        show_feedback_form(candidate_id_str, candidate_choice, criteria, username)
    else:
        st.success("You have submitted feedback for this candidate.")
    show_feedback_tabs({candidate_id_str: candidate_choice}, criteria, username)
