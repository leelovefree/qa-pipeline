# Open questions — SCRUM-6 "Add to cart from product detail page"

Stage 2 halted (hard gate): the ticket contains undefined terms and missing expected values. No spec.md was
written. Please answer on the ticket, then re-run spec-extractor.

## Q1. "Short time" for the confirmation message has no value
- **Ticket text:** "A confirmation message \"Added to cart\" appears for a short time"
- **Question:** How long is the message visible (e.g. 2 s)? Should tests assert that it disappears, and within what tolerance?

## Q2. What is "line price"?
- **Ticket text:** "Each cart line shows the product name, selected size, quantity and line price." / "the cart subtotal, which is the sum of all line prices"
- **Question:** Is line price = unit price x quantity? Or the unit price? The expected format (currency symbol, decimals, thousands separator) is also not stated; which format should tests assert?

## Q3. Behaviour of "+" at quantity 5 on the cart screen
- **Ticket text:** "increase or decrease the quantity of each line with \"+\" and \"−\" buttons, within the limit of 1 to 5. Decreasing a line below 1 is not possible, so \"−\" is disabled at quantity 1."
- **Question:** At quantity 5, is "+" disabled, or enabled and shows "Maximum 5 items per product", or silently ignored? Only "−" at 1 is specified.

## Q4. Size selection state after tapping "Add to cart"
- **Ticket text:** "No size is selected by default" / "If the customer adds the same product in the same size again"
- **Question:** After a successful add, does the size selection stay selected (button remains enabled) or reset to none (button disabled again)? This decides the steps for the merge and 5-unit-limit cases.

## Q5. Header badge on screens other than the product detail page, and after restart
- **Ticket text:** "the cart icon in the header shows a badge with the total number of units in the cart. The badge is hidden when the cart is empty." / "The cart contents are kept ... after the app is closed and reopened."
- **Question:** Is the badge shown on every screen with the header (including the cart screen), and does it show the restored count after restart? Is there a display cap for large counts (e.g. "99+")?

## Q6. Test data for stock state
- **Ticket text:** "Sizes that are out of stock are shown as disabled ... If all sizes are out of stock, ... the page shows the label \"Out of stock\"."
- **Question:** Which product(s) in the demo build have partially out-of-stock sizes, and which are fully out of stock? Tests must not guess.

## Q7. Error message: is the "Added to cart" confirmation shown as well?
- **Ticket text:** "the cart is not changed and an error message \"Maximum 5 items per product\" is shown."
- **Question:** Confirm that "Added to cart" is NOT shown in this case, and how long / where the error message is displayed (same "short time" as Q1?).
