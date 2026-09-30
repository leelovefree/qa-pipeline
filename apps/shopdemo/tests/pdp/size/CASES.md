# CASES — pdp / size

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### PDP.SIZE.DEFAULT_S_BUY_NOW_ENABLED
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap the first product in the list.
2. Without touching the size selector, inspect the size options and the "Buy Now" button.

**Expected result:** Size S is shown as selected (and M, L, XL are not selected), and the "Buy Now" button is enabled. Selected state is not exposed via accessibility, so it is verified with `assertScreenshot` (reviewer-approved); Buy Now enabled is asserted by selector.
