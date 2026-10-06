# Spec — SCRUM-12 "[shopdemo] Home: "Men Fashion" category chip filters the product list"

App: shopdemo. Extracted from the ticket description (AC1, AC2). The ticket has no comments.
Not asserted: product order, other category chips, product details beyond name/price, behaviour of any category other than "All" and "Men Fashion".

### HOME.CATEGORY_FILTER.MEN_FASHION_SHOWS_MEN_PRODUCTS
- **Given/When/Then:** Given a user is logged in with the standard test account and the home screen shows the "All" category (default), When the user taps the "Men Fashion" chip, Then the product list shows exactly two products: "Classic Denim Jacket" ($180) and "Leather Sneakers" ($220).
- **source_ticket:** SCRUM-12
- **source_span:** "**Given** I am logged in with the standard test account and the home screen shows the \"All\" category (default), **When** I tap the \"Men Fashion\" chip, **Then** the list shows exactly two products: \"Classic Denim Jacket\" ($180) and \"Leather Sneakers\" ($220)"
- **confidence:** high

### HOME.CATEGORY_FILTER.MEN_FASHION_EXCLUDES_OTHER_CATEGORIES
- **Given/When/Then:** Given a user is logged in with the standard test account and the home screen shows the "All" category (default), When the user taps the "Men Fashion" chip, Then no product from another category is shown (e.g. "Defile Lux Blazer", "Knit Bow Back Top" are not shown).
- **source_ticket:** SCRUM-12
- **source_span:** "and no product from another category (e.g. \"Defile Lux Blazer\", \"Knit Bow Back Top\") is shown."
- **confidence:** high

### HOME.CATEGORY_FILTER.ALL_RESTORES_FULL_LIST
- **Given/When/Then:** Given the "Men Fashion" chip is selected, When the user taps the "All" chip, Then the full product list is shown again, including "Defile Lux Blazer" and "Classic Denim Jacket".
- **source_ticket:** SCRUM-12
- **source_span:** "**Given** the \"Men Fashion\" chip is selected, **When** I tap the \"All\" chip, **Then** the full list is shown again, including \"Defile Lux Blazer\" and \"Classic Denim Jacket\"."
- **confidence:** high
