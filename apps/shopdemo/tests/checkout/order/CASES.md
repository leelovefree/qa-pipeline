# CASES — checkout / order

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### CHECKOUT.ORDER.PROCEED_TO_CONFIRMATION
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product and tap "Buy Now". "My Cart" shows one line.
2. Tap "Proceed to Checkout".
3. On the checkout step, perform the place-order action (its exact label is read from the real app at Stage 4; no checkout field values are asserted). Use only fake/test data if the step requires input.

**Expected result:** The "Order Confirmed!" screen is shown. (Order ID value, "Back to Home" behaviour and checkout/order contents are not asserted.)
