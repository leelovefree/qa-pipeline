# CASES — pdp / quantity

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### PDP.QUANTITY.DEFAULT_AND_MIN
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap the first product in the list.
2. Read the quantity value on the product detail page.
3. Tap "−" once.
4. Tap "+" once, then tap "−" twice.

**Expected result:**
- After step 2: quantity is 1 (default).
- After step 3: quantity is still 1 — it does not drop to 0 or below. (Whether "−" is rendered disabled or is a no-op at 1 is not specified by the ticket, so only the value is asserted.)
- After step 4: quantity went 1 → 2 → 1 → 1; it never shows a value below 1.

### PDP.QUANTITY.NO_UPPER_LIMIT
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap the first product in the list.
2. Tap "+" 20 times.

**Expected result:** Quantity shows 21, and "+" is still enabled (no maximum enforced, no warning or cap message shown).
Note: "no upper limit" cannot be proven exhaustively; 21 is a sample well above any plausible small cap (e.g. 5, 10, 20). Increase the tap count in review if a specific cap is suspected.

---

Source spec: `apps/shopdemo/specs/SCRUM-9/spec.md` (ticket SCRUM-9 — PDP: quantity increases to 3 after two taps on "+")
Status: awaiting QA approval (Stage 3, ticket SCRUM-9)

### PDP.QUANTITY.INCREMENT_TWO_TAPS
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap the first product in the list.
2. Read the quantity value on the product detail page.
3. Tap "+" once.
4. Tap "+" once more.

**Expected result:**
- After step 2: quantity is 1 (default — this is the rule's precondition; if it is not 1, the case is blocked, not passed).
- After step 4: quantity shows 3.
- Not asserted (out of scope per spec): price, size, cart contents, Buy Now.

Note: the spec says "any product"; the first product in the list is used as the representative sample.
