# CASES — cart / quantity

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### CART.QUANTITY.INCREASE
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product and tap "Buy Now" (quantity 1). "My Cart" opens with one line at quantity 1.
2. Tap "+" on that line.
3. Tap "+" on that line 10 more times.

**Expected result:** After step 2 the line quantity is 2. After step 3 it is 12, and "+" is still enabled (no maximum enforced).

### CART.QUANTITY.DECREASE
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product, tap "+" twice (quantity 3) and tap "Buy Now". "My Cart" shows the line at quantity 3.
2. Tap "−" on that line.
3. Tap "−" on that line again.

**Expected result:** After step 2 the line quantity is 2; after step 3 it is 1. The line is still present (decreasing never removes the line).

### CART.QUANTITY.MINUS_DISABLED_AT_MIN
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product and tap "Buy Now" (quantity 1).
2. On "My Cart", inspect the "−" button of the line.
3. Tap "+" once, then tap "−" once (back to 1) and inspect "−" again.

**Expected result:** At quantity 1 (after step 2 and again after step 3) the "−" button on the line is disabled; tapping it does not change the quantity or remove the line. At quantity 2 (mid step 3) "−" is enabled.

---

Source spec: `apps/shopdemo/specs/SCRUM-8/spec.md` (ticket SCRUM-8 — Cart: quantity increases on "+")
Status: approved (spec labelled `qa-approved`); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

### CART.QUANTITY.INCREASE_ONE_TO_TWO
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product and tap "Buy Now" (quantity 1). "My Cart" opens with exactly one line at quantity 1.
2. Tap "+" on that line once.

**Expected result:** The line quantity shows 2.

### CART.QUANTITY.DECREASE_TWO_TO_ONE
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product, tap the PDP "+" once (quantity 2) and tap "Buy Now". "My Cart" shows the line at quantity 2 (set up without using the cart "+", so this case does not depend on INCREASE_ONE_TO_TWO).
2. Tap "−" on that line once.

**Expected result:** The line quantity shows 1.

---

Source spec: `apps/shopdemo/specs/SCRUM-10/spec.md` (ticket SCRUM-10 — Cart: quantity increases to 3 after two taps on "+")
Status: approved by QA (manual review, no Jira label); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

### CART.QUANTITY.INCREASE_ONE_TO_THREE
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product and tap "Buy Now" (quantity 1). "My Cart" opens with exactly one line at quantity 1.
2. Tap "+" on that line once.
3. Tap "+" on that line a second time.

**Expected result:** After step 2 the line quantity shows 2. After step 3 the line quantity shows 3.
