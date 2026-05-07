from models import EmailInput

mock_emails = [
    # ── URGENT ────────────────────────────────────────────────────────────────
    EmailInput(
        sender="devops-alerts@company.com",
        subject="CRITICAL: Production server down",
        body="The main production server (us-east-1) is unresponsive since 14:22 UTC. All customer-facing APIs are returning 503. Immediate action required.",
        timestamp="2026-05-06T14:25:00"
    ),
    EmailInput(
        sender="security@company.com",
        subject="Unauthorized access detected on admin panel",
        body="We detected 47 failed login attempts followed by a successful login from IP 203.0.113.42 (Ukraine) on the admin panel at 03:15 UTC. Please verify if this was authorized.",
        timestamp="2026-05-06T03:20:00"
    ),
    EmailInput(
        sender="cto@company.com",
        subject="Board presentation due in 1 hour — need your section",
        body="Hey, the board meeting is at 4 PM. I still don't have your engineering metrics slide. Can you send it ASAP? We cannot delay this.",
        timestamp="2026-05-06T14:58:00"
    ),
    EmailInput(
        sender="hr@company.com",
        subject="URGENT: Compliance training deadline TODAY",
        body="This is a final reminder. Your mandatory compliance training must be completed by end of day today or you will be locked out of company systems.",
        timestamp="2026-05-06T09:00:00"
    ),

    # ── NEEDS REPLY ───────────────────────────────────────────────────────────
    EmailInput(
        sender="john.client@bigcorp.com",
        subject="Re: Proposal timeline",
        body="Hi, thanks for the proposal. We reviewed it internally and have a few questions: 1) Can the delivery be moved up by 2 weeks? 2) Is the pricing flexible for a 3-year contract? Looking forward to your thoughts.",
        timestamp="2026-05-06T10:30:00"
    ),
    EmailInput(
        sender="sarah@team.com",
        subject="Can we reschedule Thursday's standup?",
        body="Hey, I have a dentist appointment Thursday at 10. Can we move standup to 11 or do it async that day? Let me know what works.",
        timestamp="2026-05-05T16:45:00"
    ),
    EmailInput(
        sender="finance@company.com",
        subject="Invoice #4821 — clarification needed",
        body="Hi, we received invoice #4821 from your vendor but the line items don't match our PO. Could you confirm whether the additional $2,400 charge for 'consulting hours' was pre-approved?",
        timestamp="2026-05-06T11:15:00"
    ),
    EmailInput(
        sender="recruiter@techstartup.io",
        subject="Interested in a Senior Engineer role?",
        body="Hi, I came across your profile and think you'd be a great fit for a Senior Backend Engineer role at our Series B startup. Comp is $180-220k + equity. Would you be open to a 15-min chat this week?",
        timestamp="2026-05-05T09:00:00"
    ),
    EmailInput(
        sender="manager@company.com",
        subject="Feedback on your Q1 review draft",
        body="Hey, I read through your self-assessment. Overall great, but can you add more detail to the 'impact' section? Specifically quantify the latency improvements you made. Send me a revised version by Friday?",
        timestamp="2026-05-04T17:30:00"
    ),

    # ── FYI ───────────────────────────────────────────────────────────────────
    EmailInput(
        sender="newsletter@techweekly.com",
        subject="This week in AI: GPT-5 benchmarks, new robotics paper",
        body="Your weekly roundup: 1) GPT-5 scores 94% on MMLU. 2) Google DeepMind's new robotics paper shows 3x improvement in manipulation tasks. 3) Anthropic releases Claude 4. Read more at techweekly.com/ai",
        timestamp="2026-05-06T07:00:00"
    ),
    EmailInput(
        sender="all-hands@company.com",
        subject="Team offsite confirmed — June 15-17",
        body="Hi everyone, just confirming the team offsite will be June 15-17 in Austin, TX. Travel and hotel will be booked by admin. More details to follow next week.",
        timestamp="2026-05-05T14:00:00"
    ),
    EmailInput(
        sender="github@notifications.github.com",
        subject="[langgraph] New release: v1.2.0",
        body="langgraph v1.2.0 has been released. Changes: improved checkpointing, new ToolNode retry logic, bug fixes for conditional edges. Full changelog at github.com/langchain-ai/langgraph/releases",
        timestamp="2026-05-06T05:30:00"
    ),
    EmailInput(
        sender="docs-team@company.com",
        subject="New API docs published",
        body="FYI — we published updated API documentation for the v3 endpoints. No action needed on your part, just awareness. Link: docs.internal.company.com/v3",
        timestamp="2026-05-05T11:00:00"
    ),
    EmailInput(
        sender="noreply@slack.com",
        subject="Your weekly Slack digest",
        body="You were mentioned in 3 channels this week. #engineering: 12 new messages. #random: 45 new messages. #project-alpha: 8 new messages.",
        timestamp="2026-05-06T08:00:00"
    ),

    # ── SPAM ──────────────────────────────────────────────────────────────────
    EmailInput(
        sender="winner@lottery-intl.com",
        subject="Congratulations! You've won $5,000,000",
        body="Dear winner, your email was selected in our international lottery draw. To claim your $5,000,000 prize, reply with your full name, bank account number, and phone number.",
        timestamp="2026-05-06T02:00:00"
    ),
    EmailInput(
        sender="security-alert@amaz0n-support.com",
        subject="YOUR ACCOUNT WILL BE LOCKED IN 24 HOURS",
        body="We detected suspicious activity on your Amazon account. Click here immediately to verify your identity or your account will be permanently suspended: http://amaz0n-verify.sketchy.ru/login",
        timestamp="2026-05-06T04:00:00"
    ),
    EmailInput(
        sender="deals@cheap-watches-luxury.com",
        subject="Rolex watches 95% off — today only!!!",
        body="EXCLUSIVE DEAL: Genuine Rolex, Omega, and Patek Philippe watches at 95% discount. Limited stock! Order now at www.totally-legit-watches.biz. Free shipping worldwide!!!",
        timestamp="2026-05-05T23:00:00"
    ),
    EmailInput(
        sender="prince.nigerian@gmail.com",
        subject="Business proposal — $12M transfer",
        body="Dear friend, I am a prince from Nigeria seeking a trustworthy partner to help transfer $12,000,000 out of the country. You will receive 30% commission. Please reply with your details.",
        timestamp="2026-05-04T18:00:00"
    ),

    # ── EDGE CASES ────────────────────────────────────────────────────────────

    # PII in body — should trigger guardrails
    EmailInput(
        sender="vendor@supplierco.com",
        subject="Wire transfer details for payment",
        body="Hi, please send payment to: Account holder: John Smith, SSN: 123-45-6789, Bank: Chase, Routing: 021000021, Account: 483927156. My phone is 555-867-5309. Amount due: $14,500.",
        timestamp="2026-05-06T13:00:00"
    ),

    # Spam disguised as urgent
    EmailInput(
        sender="support@micros0ft-security.com",
        subject="URGENT: Your Microsoft 365 subscription expires today",
        body="Your Microsoft 365 subscription will expire in 2 hours. To avoid losing all your files and emails, renew immediately at http://ms365-renew.phishing.com/pay",
        timestamp="2026-05-06T12:00:00"
    ),

    # Ambiguous — could be FYI or needs_reply
    EmailInput(
        sender="colleague@company.com",
        subject="Thoughts on this architecture?",
        body="Hey, I put together a rough architecture diagram for the new microservice. No rush, but if you have opinions, feel free to comment on the doc: docs.google.com/d/abc123",
        timestamp="2026-05-05T15:30:00"
    ),

    # Very short email
    EmailInput(
        sender="boss@company.com",
        subject="Call me",
        body="ASAP.",
        timestamp="2026-05-06T15:01:00"
    ),

    # Long rambling email
    EmailInput(
        sender="overexplainer@partner.com",
        subject="Re: Re: Re: Integration timeline",
        body="Hi, so following up on our call last Tuesday where we discussed the integration timeline and you mentioned that Q3 might work but then Sarah said Q2 was preferred by the client and I think what we landed on was somewhere in between but I wanted to circle back because my team needs to plan their sprint capacity and if we're looking at a May 20 start date that only gives us 2 weeks of buffer before the client demo on June 3 which as you know is already tight given the dependencies on the auth team who are still working on the OAuth migration so could you confirm whether May 20 is still the target or if we should push to June 1?",
        timestamp="2026-05-06T10:00:00"
    ),
]
