from openai import OpenAI
from models import EmailClassification, EmailInput, TriageReport
from guardrails import sanitize_classification
from mock_emails import mock_emails
from dotenv import load_dotenv
from typing import List
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an intelligent email classification assistant.

You will receive an email with the following fields:
- sender
- subject
- body
- timestamp

Your job is to analyze the email and return a structured classification with:

## Categories
Classify the email into exactly one of these:
- "urgent"      — Requires immediate attention (deadlines, critical issues, emergencies, time-sensitive requests)
- "needs_reply" — Requires a response but not immediately (questions, requests, follow-ups)
- "fyi"         — Informational only, no action needed (newsletters, updates, announcements, receipts)
- "spam"        — Unwanted, promotional, or suspicious email

## Confidence
A float between 0.0 and 1.0 indicating how confident you are in the classification.
- 0.9–1.0 → very clear cut
- 0.7–0.9 → mostly clear with minor ambiguity
- 0.5–0.7 → ambiguous, could fit multiple categories
- below 0.5 → very uncertain

## Reasoning
A brief 1–2 sentence explanation of why you chose that category.

## Draft Reply
- If category is "needs_reply" → always provide a professional, concise draft reply
- If category is "urgent" or "fyi" or "spam" → set draft_reply to null

## Rules
- Be concise in reasoning (1-2 sentences max)
- Draft replies should be polite, professional, and to the point
- Consider the timestamp when assessing urgency (e.g. if deadline is very close)
- Never hallucinate information not present in the email
"""

def triage_email(email_input: EmailInput) -> EmailClassification:
    """
    Triages an email using the OpenAI API and returns an EmailClassification.
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": email_input.model_dump_json()}
            ],
            response_format=EmailClassification
        )
        
        sanitised_response = sanitize_classification(response.choices[0].message.parsed)
        return sanitised_response
    except Exception as e:
        print(f"Error triaging email: {e}")
        return EmailClassification(category="fyi", confidence=0.0, reasoning="Error triaging email", draft_reply=None)

def triage_batch(emails: List[EmailInput]) -> TriageReport:
    """
    Triages a batch of emails using the OpenAI API and returns a list of EmailClassifications.
    """
    results = []
    for i, email in enumerate(emails, 1):
        print(f"Processing {i}/{len(emails)}...")
        results.append(triage_email(email))

    return TriageReport(results=results)

if __name__ == "__main__":
    results = triage_batch(mock_emails)
    print(results)