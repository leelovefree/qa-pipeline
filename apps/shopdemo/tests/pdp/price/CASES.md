# CASES — pdp / price

Source spec: `apps/shopdemo/specs/SCRUM-6/spec.md` (ticket SCRUM-6 — Add to cart from product detail page)
Status: approved (Stage 3); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

---

### PDP.PRICE.FORMAT_USD
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown.
**Steps:**
1. On the home screen, tap a product priced below $1.000 and read its price on the product detail page.
2. Go back to home, tap a product priced at $1.000 or more and read its price on the product detail page.
3. Tap "Buy Now" and read the unit price shown on the cart line.

**Expected result:** Every price read matches the format `$` + digits with "." as thousands separator and no decimals — regex `^\$\d{1,3}(\.\d{3})*$` — e.g. "$300", "$1.800". No price contains "," or a decimal part (e.g. "$1,800" or "$300.00" is a failure).
Note: the catalog has no product priced ≥ $1.000 (max $300), so step 2 (thousands separator) is not exercised — accepted by reviewer; the flow covers steps 1 and 3 only.
