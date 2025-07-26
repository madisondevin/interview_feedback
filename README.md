# Interview Panel Feedback App

This app allows interview panelists to submit feedback on candidates in a structured, unbiased way. Panelists must submit their ratings before viewing others' feedback.

## Features
- Secure login for each interviewer
- Candidate and criteria selection (passed as arguments)
- Feedback forms for each candidate (overall + per-criteria)
- Ratings: None, Weak, Strong, Exceptional
- View others' feedback only after submitting your own

## Setup Instructions


### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```


## Configuration

- **Candidates, criteria, ratings, and admin users**: Edit `configuration.py`.
- **Google Sheets and authentication secrets**: Set in `.streamlit/secrets.toml` (never commit real secrets to GitHub).
- **App expiration**: Set `APP_EXPIRATION_DATE` in `configuration.py` to auto-disable after a certain date.


## Notes

- The app uses `streamlit-authenticator` for secure authentication.
- Feedback is stored in Google Sheets, not locally.
- All authentication and secrets are managed via Streamlit Authenticator and `.streamlit/secrets.toml`.
- For best performance, consider installing the optional `watchdog` package (Streamlit will prompt you if needed).


## How to Invite Users

When you are ready for panelists to use the app, share the following message with them (customize as needed):

---

**Subject:** Interview Panel Feedback App Access Instructions

Dear Panelist,

You have been invited to participate in the interview feedback process. Please follow the instructions below to access the feedback app:

1. Open your web browser and go to https://interviewfeedback-iveggdcdruheskfdyzdtg9.streamlit.app/
2. Log in using your assigned username and password.
3. Select each candidate and submit your feedback. After you submit your response for a candidate, you can view others' responses.

Please note that it may take a moment for the submit button to load, and it may take a moment for the data to process. If someone is running or biking in the top right icon and the page is loading, hang tight.

If you have any issues with the app, please contact your administrator.

Thank you for your participation!
