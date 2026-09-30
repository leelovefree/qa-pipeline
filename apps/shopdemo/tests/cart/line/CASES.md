# CASES — cart / line

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### CART.LINE.DISPLAY_FIELDS
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap product P (first product in the list); note its name, category (as shown on home) and price.
2. Tap "+" once (quantity 2), then tap "Buy Now".

**Expected result:** On "My Cart", the line for P shows: the product name of P, its category, its unit price (same value as on the product detail page, formatted per PDP.PRICE.FORMAT_USD — the unit price, not price × 2), and quantity 2.

### CART.LINE.REMOVE
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Add product A (first product) with quantity 1 via "Buy Now".
2. Navigate back to home, open product B (a different product) and add it with quantity 1 via "Buy Now".
3. On "My Cart" (lines A and B), tap the trash icon on line A.

**Expected result:** Line A is no longer shown; line B is still shown with quantity 1. ("Your cart is empty" is not shown.)
