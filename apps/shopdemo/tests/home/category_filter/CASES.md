# CASES — home / category_filter

Source spec: `apps/shopdemo/specs/SCRUM-12/spec.md` (ticket SCRUM-12 — Home: "Men Fashion" category chip filters the product list)
Status: approved by QA (Jira label `qa-approved` on SCRUM-12); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

Not covered (out of spec scope): product order, other category chips, product details beyond name/price.

---

### HOME.CATEGORY_FILTER.MEN_FASHION_SHOWS_MEN_PRODUCTS
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown with the "All" category selected (default).
**Steps:**
1. Tap the "Men Fashion" category chip.

**Expected result:** The product list shows exactly two products: "Classic Denim Jacket" priced $180 and "Leather Sneakers" priced $220. No other product is listed.

### HOME.CATEGORY_FILTER.MEN_FASHION_EXCLUDES_OTHER_CATEGORIES
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown with the "All" category selected (default).
**Steps:**
1. Confirm "Defile Lux Blazer" and "Knit Bow Back Top" are listed under "All" (sanity check that the products exist before filtering).
2. Tap the "Men Fashion" category chip.

**Expected result:** No product from another category is shown — in particular "Defile Lux Blazer" and "Knit Bow Back Top" are not visible in the product list.

### HOME.CATEGORY_FILTER.ALL_RESTORES_FULL_LIST
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown; "Men Fashion" category chip tapped and selected (list filtered to men's products).
**Steps:**
1. Tap the "All" category chip.

**Expected result:** The full product list is shown again, including both "Defile Lux Blazer" and "Classic Denim Jacket".

---

Source spec: `apps/shopdemo/specs/SCRUM-13/spec.md` (ticket SCRUM-13 — Home: "Women Fashion" category chip filters the product list)
Status: approved by QA (Jira label `qa-approved` on SCRUM-13); automated by the co-located `<REQUIREMENT_ID>.yaml` flows (Stage 4).

Not covered (out of spec scope): product order, product details beyond name/price, the "Men Fashion" and "Kids Fashion" chips, returning to "All".

### HOME.CATEGORY_FILTER.WOMEN_FASHION_SHOWS_WOMEN_PRODUCTS
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown with the "All" category selected (default).
**Steps:**
1. Tap the "Women Fashion" category chip.

**Expected result:** The product list shows exactly three products: "Defile Lux Blazer" priced $300, "Neck Short Sleeves" priced $120 and "Magnolia Pink Dress" priced $150. No other product is listed.

### HOME.CATEGORY_FILTER.WOMEN_FASHION_EXCLUDES_OTHER_CATEGORIES
**Preconditions:** App launched with cleared state; logged in with the standard test account (see AUTH.LOGIN.SUCCESS_VALID_CREDENTIALS); home screen shown with the "All" category selected (default).
**Steps:**
1. Confirm "Classic Denim Jacket", "Knit Bow Back Top" and "Training Shoes" are listed under "All" (sanity check that the products exist before filtering).
2. Tap the "Women Fashion" category chip.

**Expected result:** No product from another category is shown — in particular "Classic Denim Jacket", "Knit Bow Back Top" and "Training Shoes" are not visible in the product list.
