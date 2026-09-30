# CASES — pdp / detail

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### PDP.DETAIL.DISPLAY_ELEMENTS
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap the first product in the list.
2. Wait for the product detail page to load.

**Expected result:** The product detail page shows all of the following:
- the product name;
- the product price;
- a size selector with exactly the options S, M, L and XL;
- a quantity selector with a "−" button and a "+" button (and the current quantity value);
- a "Buy Now" button.
