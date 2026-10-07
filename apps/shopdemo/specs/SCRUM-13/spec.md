# Spec — SCRUM-13 "[shopdemo] Home: "Women Fashion" category chip filters the product list"

App: shopdemo. Extracted from the ticket description (AC1, AC2). The ticket has no comments.
Not asserted: product order, product details beyond name/price, the "Men Fashion" and "Kids Fashion" chips, returning to "All".

### HOME.CATEGORY_FILTER.WOMEN_FASHION_SHOWS_WOMEN_PRODUCTS
- **Given/When/Then:** Given a user is logged in with the standard test account and the home screen shows the "All" category (default), When the user taps the "Women Fashion" chip, Then the product list shows exactly three products: "Defile Lux Blazer" ($300), "Neck Short Sleeves" ($120) and "Magnolia Pink Dress" ($150).
- **source_ticket:** SCRUM-13
- **source_span:** "**Given** I am logged in with the standard test account and the home screen shows the \"All\" category (default), **When** I tap the \"Women Fashion\" chip, **Then** the list shows exactly three products: \"Defile Lux Blazer\" ($300), \"Neck Short Sleeves\" ($120) and \"Magnolia Pink Dress\" ($150)."
- **confidence:** high

### HOME.CATEGORY_FILTER.WOMEN_FASHION_EXCLUDES_OTHER_CATEGORIES
- **Given/When/Then:** Given a user is logged in with the standard test account and the home screen shows the "All" category (default), When the user taps the "Women Fashion" chip, Then no product from another category is shown (e.g. "Classic Denim Jacket", "Knit Bow Back Top" and "Training Shoes" are not shown).
- **source_ticket:** SCRUM-13
- **source_span:** "**Given** I am logged in with the standard test account and the home screen shows the \"All\" category (default), **When** I tap the \"Women Fashion\" chip, **Then** no product from another category is shown (e.g. \"Classic Denim Jacket\", \"Knit Bow Back Top\" and \"Training Shoes\" are not shown)."
- **confidence:** high
