# Spec — SCRUM-11 "[shopdemo] PDP: quantity decreases from 3 to 2 after one tap on "−""

App: shopdemo. Extracted from the ticket description (AC1). The ticket has no comments.
Test data (from ticket): the standard test account; any product (the first product in the list is fine); fresh app state.
Out of scope (per ticket): price, size, Buy Now, cart, and the minimum quantity behaviour.

### PDP.QUANTITY.DECREMENT_FROM_THREE
- **Given/When/Then:** Given a logged-in user is on the product detail page of any product and has raised the quantity to 3 by tapping "+" twice, When the user taps "−" once, Then the quantity shows 2.
- **source_ticket:** SCRUM-11
- **source_span:** "AC1: Given a logged-in user is on the product detail page of any product and has raised the quantity to 3 by tapping \"+\" twice, when the user taps \"−\" once, then the quantity shows 2."
- **confidence:** high
