import re
from models import EmailClassification

# ── PII Patterns ──────────────────────────────────────────────────────────────

PII_PATTERNS = {
    "ssn": [
        r"\b\d{3}-\d{2}-\d{4}\b",                        # XXX-XX-XXXX
    ],
    "phone": [
        r"\b\d{3}-\d{3}-\d{4}\b",                        # XXX-XXX-XXXX
        r"\(\d{3}\)\s?\d{3}-\d{4}",                      # (XXX) XXX-XXXX
    ],
    "email": [
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    ],
    "credit_card": [
        r"\b(?:\d[ -]?){16}\b",                          # 16 digits (with optional spaces/dashes)
    ],
    "bank_account": [
        r"\b\d{8,17}\b",                                 # account numbers (8–17 digits)
        r"\b\d{9}\b",                                    # routing numbers (exactly 9 digits)
    ],
}

# ── redact_pii ────────────────────────────────────────────────────────────────

def redact_pii(text: str) -> str:
    """
    Replaces all detected PII in text with [REDACTED].
    """
    redacted = text

    for _, patterns in PII_PATTERNS.items():
        for pattern in patterns:
            redacted = re.sub(pattern, "[REDACTED]", redacted)

    return redacted

def sanitize_classification(classification: EmailClassification) -> EmailClassification:
    """
    Sanitizes the classification by redacting any PII in the draft reply.
    """
    if classification.draft_reply:
        classification.draft_reply = redact_pii(classification.draft_reply)
    if classification.reasoning:
        classification.reasoning = redact_pii(classification.reasoning)
    return classification


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    Hi, my name is John.
    SSN: 123-45-6789
    Phone: 987-654-3210 or (415) 555-1234
    Email: john.doe@example.com
    Credit Card: 4111 1111 1111 1111
    Bank Account: 123456789012
    Routing Number: 021000021
    """

    print("\n=== redact_pii ===")
    print(redact_pii(sample))