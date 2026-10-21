#!/usr/bin/env python3
"""Create a demo ticket in the personal Jira project (tracker_project_key of apps/shopdemo).

  python3 docs/demo/new_ticket.py clean            # well-specified ticket: runs the full happy path
  python3 docs/demo/new_ticket.py vague            # deliberately vague ticket: triggers the ambiguity gate
  python3 docs/demo/new_ticket.py clean --dry-run  # print the payload, create nothing

The ticket is created WITHOUT labels. Adding the `qa-auto` label is the live trigger of the demo.
Credentials come from ~/.config/qa-auto/env (never printed). Every successful run creates ONE real issue.
A ticket that already has a PR cannot be reused, so create a fresh one for every rehearsal and for the live run.

Behaviours in the "clean" ticket were checked against the app source (leelovefree/ios-shop-demo):
  - CheckoutView.placeOrder() calls cartStore.clear() before showing the confirmation screen
  - OrderConfirmedView "Back to Home" calls path.removeLast(path.count) -> home screen
  - empty cart text "Your cart is empty" is already asserted by CART.EMPTY.MESSAGE
"""
import base64
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

VARIANTS = {
    "clean": {
        "summary": '[shopdemo] Order Confirmed: "Back to Home" returns to the home screen and the cart is empty',
        "paragraphs": [
            'Context: after a shopper places an order, the "Order Confirmed!" screen shows a "Back to Home" button.',
            'AC1: Given I am logged in with the standard test account, started from a fresh app state, and placed an order for '
            '"Defile Lux Blazer" (Buy Now, Proceed to Checkout, Place Order), When I tap "Back to Home" on the '
            '"Order Confirmed!" screen, Then the home screen is shown.',
            'AC2: Given the same order has been placed and I tapped "Back to Home", When I open the cart from the home screen, '
            'Then the cart shows "Your cart is empty".',
            "Test data: the standard test account. Start from a fresh app state.",
            "Out of scope: the Order ID value (it is random), the contents of the checkout screen, the wording of the order confirmation message.",
        ],
    },
    "vague": {
        "summary": "[shopdemo] Checkout should feel faster and clearer",
        "paragraphs": [
            "Users say the checkout is confusing and slow. Make it better and show the right information.",
        ],
    },
}


def load_env():
    for line in (Path.home() / ".config/qa-auto/env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()


def project_key():
    cfg = (ROOT / "apps/shopdemo/app.config.yml").read_text()
    return re.search(r"^tracker_project_key:\s*(\S+)", cfg, re.M).group(1)


def adf(paragraphs):
    return {"type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": p}]} for p in paragraphs]}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1 or args[0] not in VARIANTS:
        sys.exit(__doc__)
    v = VARIANTS[args[0]]
    body = {"fields": {"project": {"key": project_key()}, "issuetype": {"name": "Story"},
                       "summary": v["summary"], "description": adf(v["paragraphs"])}}
    if "--dry-run" in sys.argv:
        print(json.dumps(body, indent=2, ensure_ascii=False))
        return
    load_env()
    base = os.environ["JIRA_BASE_URL"].rstrip("/")
    auth = base64.b64encode(f"{os.environ['JIRA_EMAIL']}:{os.environ['JIRA_API_TOKEN']}".encode()).decode()
    req = urllib.request.Request(base + "/rest/api/3/issue", method="POST", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        key = json.load(r)["key"]
    print(f"created {key}: {base}/browse/{key}")
    print(f"live trigger: add the label  qa-auto  to {key}")


main()
