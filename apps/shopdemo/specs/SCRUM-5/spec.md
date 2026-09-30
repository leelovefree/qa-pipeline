# Spec: SCRUM-5 — Login screen — authenticate with email and password

Source ticket: [SCRUM-5](https://linhdngen.atlassian.net/browse/SCRUM-5)

## User story
As a returning shopper, I want to log into Fashion Shop with my email and password, so that I can
access my account and start shopping.

## Notes carried from ticket
- Demo account for QA: `demo@shop.com` / `123456`.
- This ticket formalizes existing login behavior as a QA regression requirement — no product code
  changes are expected as part of this ticket.

---

### AUTH.LOGIN.INITIAL_SCREEN_STATE
- **Given/When/Then:** Given the app has just launched and no user is logged in, when the app
  finishes launching, then the login screen is shown first, with an email field, a password field,
  and a "Log In" button all visible.
- **source_ticket:** SCRUM-5
- **source_span:** "Given the app has just launched and no user is logged in, when the app finishes launching, then the login screen is shown first, with an email field, a password field, and a \"Log In\" button all visible."
- **confidence:** high

### AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS
- **Given/When/Then:** Given a user is on the login screen, when they enter the registered demo
  account's email (`demo@shop.com`) and correct password (`123456`) and tap "Log In", then they are
  taken to the home screen.
- **source_ticket:** SCRUM-5
- **source_span:** "Given a user is on the login screen, when they enter the registered demo account's email and correct password and tap \"Log In\", then they are taken to the home screen." (demo credentials from ticket Notes: "Demo account for QA: `demo@shop.com` / `123456`.")
- **confidence:** high

### AUTH.LOGIN.INVALID_CREDENTIALS_ERROR
- **Given/When/Then:** Given a user is on the login screen, when they enter an email/password
  combination that does not match any account and tap "Log In", then an inline error message reading
  "Invalid email or password." is shown, and the user remains on the login screen (home screen is
  not shown).
- **source_ticket:** SCRUM-5
- **source_span:** "Given a user is on the login screen, when they enter an email/password combination that does not match any account and tap \"Log In\", then an inline error message reading \"Invalid email or password.\" is shown, and the user remains on the login screen (home screen is not shown)."
- **confidence:** high

### AUTH.LOGIN.PASSWORD_MASKED
- **Given/When/Then:** Given a user is on the login screen, when they type into the password field,
  then the entered characters are masked and never shown in plain text.
- **source_ticket:** SCRUM-5
- **source_span:** "Given a user is on the login screen, when they type into the password field, then the entered characters are masked and never shown in plain text."
- **confidence:** high
