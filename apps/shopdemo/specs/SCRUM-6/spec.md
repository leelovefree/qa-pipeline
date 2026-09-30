# Spec — SCRUM-6 "Add to cart from product detail page"

App: shopdemo. Extracted from the rewritten ticket description and comment 10001 (answers to Q1-Q7).
Not asserted (per ticket): Subtotal, Delivery Fee display, color, wishlist, promo codes, payment, stock handling, cart icon/badge, size in cart, cart persistence across app restart, checkout/order details.

### PDP.DETAIL.DISPLAY_ELEMENTS
- **Given/When/Then:** Given a product detail page is open, When it is displayed, Then it shows the product name, price, a size selector with options S, M, L, XL, a quantity selector with "−" and "+" buttons, and a "Buy Now" button.
- **source_ticket:** SCRUM-6
- **source_span:** "The page shows the product name, price, a size selector (S, M, L, XL), a quantity selector with \"−\" and \"+\" (minimum 1, no upper limit, default 1) and a \"Buy Now\" button."
- **confidence:** high

### PDP.QUANTITY.DEFAULT_AND_MIN
- **Given/When/Then:** Given a product detail page is freshly opened, When it is displayed, Then the quantity is 1, and the quantity can never be set below 1.
- **source_ticket:** SCRUM-6
- **source_span:** "a quantity selector with \"−\" and \"+\" (minimum 1, no upper limit, default 1)"
- **confidence:** high

### PDP.QUANTITY.NO_UPPER_LIMIT
- **Given/When/Then:** Given a product detail page, When the customer taps "+" repeatedly, Then the quantity keeps increasing with no maximum enforced.
- **source_ticket:** SCRUM-6
- **source_span:** "minimum 1, no upper limit, default 1"
- **confidence:** high

### PDP.SIZE.DEFAULT_S_BUY_NOW_ENABLED
- **Given/When/Then:** Given a product detail page is freshly opened, When it is displayed, Then size S is selected and "Buy Now" is enabled.
- **source_ticket:** SCRUM-6
- **source_span:** "Size S is selected by default, so \"Buy Now\" is always enabled."
- **confidence:** high

### PDP.PRICE.FORMAT_USD
- **Given/When/Then:** Given any product price is displayed, When the price is rendered, Then it is in USD with a "$" prefix, no decimals and "." as thousands separator (e.g. "$300", "$1.800").
- **source_ticket:** SCRUM-6
- **source_span:** "Prices are shown in USD without decimals, with \".\" as thousands separator (e.g. \"$300\", \"$1.800\")."
- **confidence:** high

### CART.BUY_NOW.ADD_AND_OPEN_CART
- **Given/When/Then:** Given a product detail page with a selected quantity N and the product not yet in the cart, When the customer taps "Buy Now", Then a cart line for that product with quantity N is added and the cart screen ("My Cart") opens.
- **source_ticket:** SCRUM-6
- **source_span:** "\"Buy Now\" adds the selected quantity of the product to the cart and opens the cart screen (\"My Cart\")."
- **confidence:** high

### CART.BUY_NOW.NO_CONFIRMATION_MESSAGE
- **Given/When/Then:** Given a product detail page, When the customer taps "Buy Now", Then no confirmation message is shown.
- **source_ticket:** SCRUM-6
- **source_span:** "No confirmation message is shown."
- **confidence:** high

### CART.BUY_NOW.MERGE_SAME_PRODUCT
- **Given/When/Then:** Given the cart already contains a line for product P with quantity A, When the customer adds product P again with selected quantity N via "Buy Now", Then the cart still has exactly one line for P and its quantity is A + N.
- **source_ticket:** SCRUM-6
- **source_span:** "The cart has one line per product; adding the same product again increases the existing line's quantity by the selected quantity."
- **confidence:** high

### CART.LINE.DISPLAY_FIELDS
- **Given/When/Then:** Given the cart contains a line, When the cart screen is displayed, Then the line shows the product name, category, unit price (format per PDP.PRICE.FORMAT_USD) and quantity.
- **source_ticket:** SCRUM-6
- **source_span:** "The cart screen shows each line with the product name, category, unit price and quantity."
- **confidence:** high

### CART.QUANTITY.INCREASE
- **Given/When/Then:** Given a cart line with quantity Q, When the customer taps "+" on that line, Then its quantity becomes Q + 1 (no upper limit).
- **source_ticket:** SCRUM-6
- **source_span:** "The customer can change the quantity of each line with \"+\" and \"−\" (\"−\" is disabled at quantity 1, no upper limit)"
- **confidence:** high

### CART.QUANTITY.DECREASE
- **Given/When/Then:** Given a cart line with quantity Q greater than 1, When the customer taps "−" on that line, Then its quantity becomes Q − 1.
- **source_ticket:** SCRUM-6
- **source_span:** "The customer can change the quantity of each line with \"+\" and \"−\" (\"−\" is disabled at quantity 1, no upper limit)"
- **confidence:** high

### CART.QUANTITY.MINUS_DISABLED_AT_MIN
- **Given/When/Then:** Given a cart line with quantity 1, When the cart screen is displayed, Then the "−" button on that line is disabled.
- **source_ticket:** SCRUM-6
- **source_span:** "\"−\" is disabled at quantity 1"
- **confidence:** high

### CART.LINE.REMOVE
- **Given/When/Then:** Given the cart contains a line, When the customer taps the trash icon on that line, Then that line is removed from the cart.
- **source_ticket:** SCRUM-6
- **source_span:** "remove a line with the trash icon"
- **confidence:** high

### CART.EMPTY.MESSAGE
- **Given/When/Then:** Given the cart contains exactly one line, When the customer removes that last line, Then the screen shows "Your cart is empty".
- **source_ticket:** SCRUM-6
- **source_span:** "When the last line is removed, the screen shows \"Your cart is empty\"."
- **confidence:** high

### CART.TOTAL.FORMULA
- **Given/When/Then:** Given the cart contains one or more lines, When the cart screen is displayed, Then Total Cost equals the sum of (unit price x quantity) over all lines plus the Delivery Fee of $5.
- **source_ticket:** SCRUM-6
- **source_span:** "The screen shows Total Cost = sum of (unit price x quantity) over all lines + Delivery Fee ($5)."
- **confidence:** high

### CART.TOTAL.UPDATES_IMMEDIATELY
- **Given/When/Then:** Given the cart screen shows a Total Cost, When the customer changes a line's quantity or removes a line, Then Total Cost updates immediately to the new value per CART.TOTAL.FORMULA.
- **source_ticket:** SCRUM-6
- **source_span:** "Total Cost updates immediately when a quantity changes or a line is removed."
- **confidence:** high

### CART.PERSIST.ACROSS_NAVIGATION
- **Given/When/Then:** Given the cart contains lines, When the customer navigates to other screens and returns to the cart, Then the cart contents are unchanged.
- **source_ticket:** SCRUM-6
- **source_span:** "The cart contents are kept when the customer navigates between screens."
- **confidence:** high

### CHECKOUT.ORDER.PROCEED_TO_CONFIRMATION
- **Given/When/Then:** Given the cart screen contains at least one line, When the customer taps "Proceed to Checkout" and places the order, Then the "Order Confirmed!" screen is shown (contents of checkout and order steps are not asserted).
- **source_ticket:** SCRUM-6
- **source_span:** "From the cart screen, \"Proceed to Checkout\" leads to placing the order and then to the \"Order Confirmed!\" screen (order ID, \"Back to Home\")."
- **confidence:** high
