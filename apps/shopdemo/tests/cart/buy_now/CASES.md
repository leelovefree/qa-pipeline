# CASES — cart / buy_now

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### CART.BUY_NOW.ADD_AND_OPEN_CART
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap product P (first product in the list); note its name.
2. On the product detail page, tap "+" twice (quantity 3).
3. Tap "Buy Now".

**Expected result:** The cart screen titled "My Cart" opens. It contains exactly one line, for product P, with quantity 3.

### CART.BUY_NOW.NO_CONFIRMATION_MESSAGE
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap the first product in the list.
2. Tap "Buy Now".

**Expected result:** The app goes directly to the "My Cart" screen. No alert, dialog, toast or banner confirming the add is shown on the "My Cart" screen (e.g. no text such as "Added to cart", "Added", "Success").
Note: absence of "any" message can only be checked against known patterns — the flow asserts no system alert and none of the listed texts. This is a bounded negative check, not a proof.

### CART.BUY_NOW.MERGE_SAME_PRODUCT
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap product P (first product in the list).
2. Tap "+" once (quantity 2), then tap "Buy Now". Cart shows one line for P with quantity 2.
3. Navigate back to the home screen and open product P's detail page again.
4. Set quantity to 3 (tap "+" until the quantity shows 3), then tap "Buy Now".

**Expected result:** The "My Cart" screen shows exactly one line for product P (no duplicate line), with quantity 5 (2 + 3).
