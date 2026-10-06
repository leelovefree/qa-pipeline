# Spec — SCRUM-8 "[shopdemo] Cart: quantity increases on "+""

App: shopdemo. Extracted from the ticket description (AC1, AC2). No comments on the ticket at extraction time.

Note: these two rules are concrete instances of the general quantity rules `CART.QUANTITY.INCREASE` and `CART.QUANTITY.DECREASE` (SCRUM-6). Distinct IDs are used so the specific scenarios stay separately traceable; the "+" / "−" buttons are the ones on the cart line (ticket summary: "Cart: quantity increases on \"+\"").

### CART.QUANTITY.INCREASE_ONE_TO_TWO
- **Given/When/Then:** Given the cart has 1 item whose quantity is 1, When the user taps "+", Then the quantity shows 2.
- **source_ticket:** SCRUM-8
- **source_span:** "AC1: Given cart has 1 item with quantity 1, when user taps \"+\", quantity shows 2."
- **confidence:** high

### CART.QUANTITY.DECREASE_TWO_TO_ONE
- **Given/When/Then:** Given the cart item's quantity is 2, When the user taps "−", Then the quantity shows 1.
- **source_ticket:** SCRUM-8
- **source_span:** "AC2: Given quantity is 2, when user taps \"−\", quantity shows 1."
- **confidence:** high
