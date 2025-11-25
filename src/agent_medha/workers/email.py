import os
from langchain_core.tools import tool
from typing import List, Dict

# Mock Data
MOCK_EMAILS = [
    {"id": 1, "sender": "boss@work.com", "subject": "Urgent: Project Deadline", "body": "We need to finish this by EOD.", "priority": "high", "category": "work"},
    {"id": 2, "sender": "bank@alert.com", "subject": "Low Balance Alert", "body": "Your balance is below $100.", "priority": "high", "category": "finance"},
    {"id": 3, "sender": "newsletter@tech.com", "subject": "Weekly Tech News", "body": "Here are the top stories...", "priority": "low", "category": "newsletter"},
    {"id": 4, "sender": "team@work.com", "subject": "Meeting Notes", "body": "Notes from today's sync.", "priority": "medium", "category": "work"},
]

@tool
def read_emails(limit: int = 5) -> str:
    """
    Reads the latest emails from the inbox.
    """
    emails = MOCK_EMAILS[:limit]
    result = "Here are your latest emails:\n\n"
    for email in emails:
        result += f"- [{email['priority'].upper()}] From: {email['sender']}, Subject: {email['subject']}\n"
    return result

@tool
def draft_reply(email_id: int, content: str) -> str:
    """
    Drafts a reply to a specific email.
    """
    # Find email
    email = next((e for e in MOCK_EMAILS if e["id"] == email_id), None)
    if not email:
        return f"Error: Email with ID {email_id} not found."
    
    return f"Drafted reply to '{email['subject']}':\n\n{content}\n\n(Draft saved to Outbox)"

class EmailWorker:
    def get_tools(self):
        return [read_emails, draft_reply]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Returns statistics for the dashboard widget.
        """
        urgent_work = len([e for e in MOCK_EMAILS if e["priority"] == "high" and e["category"] == "work"])
        financial_alerts = len([e for e in MOCK_EMAILS if e["category"] == "finance"])
        
        return {
            "urgent_work": urgent_work,
            "financial_alerts": financial_alerts
        }
