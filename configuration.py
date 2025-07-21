import streamlit_authenticator as stauth
import streamlit as st
from datetime import datetime

# --- ENHANCED SECURITY CONFIGURATION ---

# Set app expiration (optional - auto-disable after interviews)
APP_EXPIRATION_DATE = datetime(2025, 8, 1)  # Adjust as needed
ADMIN_USERS = ["admin"]
COOKIE_EXPIRY_DAYS = 1  # Shorter expiry for security

# Load secrets from Streamlit secrets
COOKIE_KEY = st.secrets["COOKIE_KEY"]


RATING_OPTIONS = [
    "I can't tell",
    "Low",
    "Moderate",
    "Strong",
    "Exceptional",
]

# --- CONFIGURATION ---
candidates = {"1": "Anne", "2": "Maria Paula", "3": "Anastasia"}
criteria = {
    "User research": [
        "Design and conduct mixed method studies, analyze complex data, synthesize findings, and translate insights into actionable recommendations/products for your role.",
        "Expertise should include multiple methods for both quantitative and qualitative research approaches.",
        "Data analytics should be strong for both qualitative and quantitative methods (not manual processes like spreadsheets and all manual coding; inter-rater reliability, etc.)",
        "Working with product/UX designers to create actionable research plans.",
    ],
    "Research ops": [
        "Tracking and managing recruitment and participant pools (e.g., who has been invited via what channel for which studies, who participated, at what level of engagement), ideally with research-specific tools other than spreadsheets.",
        "Managing research logistics (e.g., scheduling interviews, sending reminders, and ensuring participants have the necessary information).",
        "Creating meaningful research inventory (e.g., tagging assets and presentations).",
    ],
    "Communication and collaboration": [
        "Collaborating with cross-functional teams to ensure research design, analysis, and presentations meets business goals.",
        "For example, how well can you understand their answer (if presented as non-technical)?",
    ],
    "ECE knowledge & empathy": [
        "Ability to empathize and build rapport with early childhood educators and administrators.",
        "This position includes lots of engagement and interaction with Frog Street customers.",
        "Baseline ECE knowledge (such as awareness of trends, key issues, challenges, opportunities).",
    ],
    "Leadership & professional maturity": [
        "Level of professional independence, judgment, and maturity in handling complex projects and stakeholders.",
    ],
}

# Use strong, unique passwords (generate these once and store securely)
usernames = st.secrets["credentials"]["usernames"]
names = st.secrets["credentials"]["names"]
secure_passwords = st.secrets["credentials"]["passwords"]

# Hash the passwords - streamlit-authenticator 0.1.5 syntax
hashed_passwords = stauth.Hasher(secure_passwords).generate()

credentials = {
    "usernames": {
        usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
        usernames[1]: {"name": names[1], "password": hashed_passwords[1]},
        usernames[2]: {"name": names[2], "password": hashed_passwords[2]},
    }
}
