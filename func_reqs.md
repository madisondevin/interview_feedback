The goal is an interviewing feedback app.

Provided with 
* interview criteria
*  a description of each criteria, 
* interviewee names
* panelist names

the app should
* allow users to login with a password
* Note that the app will be hosted on public streamlist, so security functionality should be in place to protect feedback.
* only allow the user to view their own feedback on each candidate until they have completed and submitted their feedback for that candidate
* they can't edit their responses once submitted
* after submitting feedback for a candidate, they can click that candidates' tab and see both theirs and all other panelists' feedback on the candidate

The UI for a paneist should
* one row at the top that has the candidates' anmes and an indiator of their submitted status. Clicking on one should bring you to that one. This row should not change after you click a candidate, and you should be able to move back and forth
* be optimized for desktop/laptop, not mobile. rating should be a left column and feedback notes on the right, for example

An administrative user
* should have a dashboard with each panelist x interviewee status (submitted/not) and the date of last updated or entered any feedback
* able to view all panelists' responses on the dashboard
* able to download the feedback as a CSV
* not able to submit feedback for a candidate
* admin dashboard should have an Criteria Avg Rating column that works as follows: values of the first rating option, "I can't tell" are ignored. For all other ratings values, the first is a 0, the second is a 1, the third is a 2, and so on. This should be done ensuring flexibility for different numbers and names for ratings. The Criteria Avg Rating column should come before the first criteria column in both the admin dashboard and the Excel export.
* The excel export should have columns in the order of candidate then interviewer.

Feedback should: 
*  persist between sessions/logins/closing of the app. Submitted or not should be a property of the interviewer x candidate feedback
*  auto-save so a panelist can't lose what they're typing even if they haven't submitted yet.

Code structure
* All configurations such as panelist usernames, starter passwords, ratings choices, criteria should be in a configurations.py module
* Code should be as modular as possible, with short, single-purpose functions and modules by groups of functionality.
