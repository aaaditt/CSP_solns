"""
Gemini-based email classifier.

The prompt lives here, in one obvious place, so it's easy to iterate on
without touching the sync pipeline or the API layer.
"""

import json
import re

from google import genai
from google.genai import types

import config

VALID_CATEGORIES = {
    "streaming",
    "saas",
    "hosting",
    "domain",
    "telecom",
    "gym",
    "newsletter",
    "finance",
    "other",
    "not_subscription",
}

CLASSIFICATION_PROMPT = """You are an email classifier for a personal subscription-tracking tool.
Given the sender name, sender email, subject, and (optionally) a body snippet of ONE email,
decide whether it relates to a paid, recurring subscription or service.

Subscription-related includes: streaming, SaaS, hosting, domains, telecom, gym memberships,
newsletters that have a paid tier, and recurring payments -- including the FULL lifecycle of
such services: welcome/onboarding emails, invoices/receipts, renewal notices, price-change
notices, payment-failure alerts, and cancellation confirmations.

NOT subscription-related: one-off purchase marketing, promotional blasts, unrelated personal
or work email, one-time purchase receipts (not recurring), and generic finance/banking emails
that are not about a subscribed service (e.g. a loan payment reminder is not_subscription).

Free newsletters with no evidence of a paid plan should be category "newsletter" but with
LOWER confidence (below 0.5) unless the email itself shows evidence of payment.

Respond with STRICT JSON ONLY -- no prose, no markdown code fences, no explanation. Exactly
this shape:
{{"is_subscription": true, "category": "saas", "confidence": 0.92, "summary": "one-line summary"}}

category must be exactly one of: streaming, saas, hosting, domain, telecom, gym, newsletter,
finance, other, not_subscription.

If not a subscription, respond with is_subscription=false and category="not_subscription".

Email to classify:
Sender name: {sender}
Sender email: {sender_email}
Subject: {subject}
Body snippet: {body_snippet}
"""

FALLBACK_RESULT = {
    "is_subscription": False,
    "category": "not_subscription",
    "confidence": 0.0,
    "summary": "classification failed",
}

_client = genai.Client(api_key=config.GOOGLE_API_KEY)


def _call_gemini(prompt: str) -> str:
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0),
    )
    return response.text or ""


def _parse_json_defensive(raw: str) -> dict:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in response: {raw!r}")

    data = json.loads(match.group(0))

    required_keys = {"is_subscription", "category", "confidence", "summary"}
    if not required_keys.issubset(data.keys()):
        raise ValueError(f"Missing required keys in response: {data!r}")

    if data["category"] not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category in response: {data['category']!r}")

    return {
        "is_subscription": bool(data["is_subscription"]),
        "category": data["category"],
        "confidence": float(data["confidence"]),
        "summary": str(data["summary"]),
    }


def classify_email(sender: str, sender_email: str, subject: str, body_snippet: str = "") -> dict:
    """
    Classifies one email via Gemini. Never raises -- any network/API/parse
    failure is caught and converted to FALLBACK_RESULT, so one bad email can
    never abort a sync.
    """
    snippet = body_snippet[:200] if config.INCLUDE_BODY_SNIPPET else ""
    prompt = CLASSIFICATION_PROMPT.format(
        sender=sender,
        sender_email=sender_email,
        subject=subject,
        body_snippet=snippet,
    )

    for attempt in range(2):
        try:
            raw = _call_gemini(prompt)
            return _parse_json_defensive(raw)
        except Exception:
            if attempt == 0:
                continue
            return dict(FALLBACK_RESULT)

    return dict(FALLBACK_RESULT)


if __name__ == "__main__":
    result = classify_email(
        sender="Netflix",
        sender_email="info@account.netflix.com",
        subject="Your Netflix payment confirmation",
        body_snippet="Your monthly payment of $15.49 was processed. Your next billing date is...",
    )
    print(json.dumps(result, indent=2))
