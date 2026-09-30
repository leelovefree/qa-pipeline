# CASES — auth / login

Source spec: `apps/shopdemo/specs/SCRUM-5/spec.md` (ticket SCRUM-5 — Login screen — authenticate with email and password)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### AUTH.LOGIN.INITIAL_SCREEN_STATE
**Preconditions:** App freshly installed or app state cleared; no user logged in.
**Steps:**
1. Launch the app with cleared state.
2. Wait for the app to finish launching.

**Expected result:** The login screen is the first screen shown. An email field, a password field, and a "Log In" button are all visible.

### AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS
**Preconditions:** App launched with cleared state; login screen is shown.
**Steps:**
1. Tap the email field and enter `demo@shop.com`.
2. Tap the password field and enter `123456`.
3. Tap "Log In".

**Expected result:** The user is taken to the home screen. The login screen is no longer shown.

### AUTH.LOGIN.INVALID_CREDENTIALS_ERROR
**Preconditions:** App launched with cleared state; login screen is shown.
**Steps:**
1. Tap the email field and enter an email that matches no account (e.g. `nobody@shop.com`).
2. Tap the password field and enter any password (e.g. `wrongpass`).
3. Tap "Log In".

**Expected result:** An inline error message reading exactly "Invalid email or password." is shown. The user remains on the login screen (email field, password field and "Log In" button still visible), and the home screen is not shown.

### AUTH.LOGIN.PASSWORD_MASKED
**Preconditions:** App launched with cleared state; login screen is shown.
**Steps:**
1. Tap the password field.
2. Type `123456`.

**Expected result:** The entered characters are masked in the password field (secure text entry), and the plain-text value `123456` is never shown on screen.
