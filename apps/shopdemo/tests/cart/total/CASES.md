# CASES — cart / total

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

Pricing note: the concrete products (and therefore the concrete expected totals) are pinned at Stage 4
from the real catalog. Expected values below are written as formulas over the prices read from screen.

---

### CART.TOTAL.FORMULA
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open product A; note its unit price pA. Tap "+" once (quantity 2) and tap "Buy Now".
2. Navigate back to home, open a different product B; note its unit price pB. Tap "Buy Now" (quantity 1).
3. On "My Cart", read Total Cost.

**Expected result:** Total Cost = 2 × pA + 1 × pB + $5 (Delivery Fee), formatted per PDP.PRICE.FORMAT_USD. (Subtotal and the Delivery Fee row itself are not asserted.)

### CART.TOTAL.UPDATES_IMMEDIATELY
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Add product A (unit price pA) with quantity 1 via "Buy Now"; navigate back, add product B (unit price pB) with quantity 1 via "Buy Now".
2. On "My Cart", read Total Cost.
3. Tap "+" on line A; read Total Cost without leaving the screen.
4. Tap "−" on line A; read Total Cost.
5. Tap the trash icon on line B; read Total Cost.

**Expected result:** Without navigating away or refreshing, Total Cost reads:
- step 2: pA + pB + $5
- step 3: 2 × pA + pB + $5
- step 4: pA + pB + $5
- step 5: pA + $5
