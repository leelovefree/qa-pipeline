# CASES — cart / persist

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### CART.PERSIST.ACROSS_NAVIGATION
**Preconditions:** App launched with cleared state (cart empty); logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. Open product A, tap "+" once (quantity 2), tap "Buy Now".
2. Navigate back to home, open product B, tap "Buy Now" (quantity 1). "My Cart" shows A ×2 and B ×1; note Total Cost.
3. Navigate back to the home screen.
4. Open product C (a third product) and tap "Buy Now" (quantity 1). "My Cart" opens with C added.

**Expected result:** "My Cart" shows line A with quantity 2 and line B with quantity 1 unchanged from step 2, plus a new line C with quantity 1; Total Cost = step-2 total + price of C.
**Reviewer note:** home has a cart icon (`home_cart_button`, top right), so persistence is verified by re-entering the cart through it and checking A and B are intact.
