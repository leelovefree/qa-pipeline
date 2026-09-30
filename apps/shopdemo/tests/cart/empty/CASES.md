# CASES — cart / empty

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### CART.EMPTY.MESSAGE
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open the first product and tap "Buy Now". "My Cart" shows exactly one line.
2. Tap the trash icon on that line.

**Expected result:** The line is removed and the screen shows the text "Your cart is empty". No cart line is shown.
