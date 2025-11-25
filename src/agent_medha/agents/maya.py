"""
Maya - Intelligent Email Agent

Maya is your AI email assistant who:
- Learns your email patterns and preferences
- Triages emails by importance and urgency
- Drafts responses based on learned patterns
- Summarizes emails intelligently
- Handles email workflows autonomously

Maya uses multiple memory systems:
- Episodic: Past email interactions
- Semantic: Contact profiles, preferences, facts
- Procedural: Response patterns, workflows
"""

import os
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent_medha.memory.store import get_memory_store, SharedMemoryStore
from agent_medha.memory.base import MemoryDomain, MemoryScope
from agent_medha.memory.procedural import Procedure
from agent_medha.memory.semantic import EntityProfile
from agent_medha.workers.email import GmailClient, gmail_client


class EmailPriority(str, Enum):
    """Email priority levels."""
    URGENT = "urgent"           # Needs immediate action
    HIGH = "high"              # Important, respond today
    NORMAL = "normal"          # Standard priority
    LOW = "low"                # Can wait, FYI only
    NEWSLETTER = "newsletter"  # Subscriptions, bulk
    SPAM = "spam"              # Promotional, spam-like


class EmailCategory(str, Enum):
    """Email categories for triage."""
    ACTION_REQUIRED = "action_required"
    NEEDS_REPLY = "needs_reply"
    FYI_ONLY = "fyi_only"
    MEETING = "meeting"
    NEWSLETTER = "newsletter"
    PROMOTION = "promotion"
    PERSONAL = "personal"
    WORK = "work"
    FINANCIAL = "financial"
    AUTOMATED = "automated"


@dataclass
class TriagedEmail:
    """An email with triage information."""
    id: str
    thread_id: str
    subject: str
    sender: str
    sender_email: str
    snippet: str
    date: str
    is_unread: bool
    
    # Triage results
    priority: EmailPriority = EmailPriority.NORMAL
    categories: List[EmailCategory] = field(default_factory=list)
    importance_score: float = 0.5
    
    # Analysis
    summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    suggested_response: Optional[str] = None
    
    # Metadata
    sender_is_vip: bool = False
    has_deadline: bool = False
    deadline: Optional[str] = None
    requires_response: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "subject": self.subject,
            "sender": self.sender,
            "sender_email": self.sender_email,
            "snippet": self.snippet,
            "date": self.date,
            "is_unread": self.is_unread,
            "priority": self.priority.value,
            "categories": [c.value for c in self.categories],
            "importance_score": self.importance_score,
            "summary": self.summary,
            "key_points": self.key_points,
            "suggested_actions": self.suggested_actions,
            "suggested_response": self.suggested_response,
            "sender_is_vip": self.sender_is_vip,
            "has_deadline": self.has_deadline,
            "deadline": self.deadline,
            "requires_response": self.requires_response,
        }


class Maya:
    """
    Maya - Your Intelligent Email Assistant
    
    Maya learns from your email patterns and helps manage your inbox intelligently.
    """
    
    AGENT_ID = "maya"
    DOMAIN = MemoryDomain.EMAIL
    
    # VIP detection keywords
    VIP_KEYWORDS = ["boss", "manager", "ceo", "cto", "director", "vp", "president"]
    
    # Priority keywords
    URGENT_KEYWORDS = ["urgent", "asap", "immediately", "emergency", "critical", "deadline today"]
    HIGH_PRIORITY_KEYWORDS = ["important", "priority", "action required", "please respond", "waiting for"]
    
    # Category detection patterns
    MEETING_KEYWORDS = ["meeting", "calendar", "invite", "schedule", "appointment", "call"]
    FINANCIAL_KEYWORDS = ["invoice", "payment", "receipt", "bill", "transaction", "bank", "credit"]
    NEWSLETTER_PATTERNS = ["unsubscribe", "email preferences", "view in browser", "newsletter"]
    
    def __init__(self):
        self.memory = get_memory_store()
        self.gmail = gmail_client
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # Cache for VIP contacts
        self._vip_cache: Dict[str, bool] = {}
        self._load_vip_cache()
    
    def _load_vip_cache(self):
        """Load VIP contacts from semantic memory."""
        contacts = self.memory.search_entities("VIP important contact", entity_type="contact", limit=50)
        for contact in contacts:
            if contact.attributes.get("is_vip"):
                email = contact.attributes.get("email", "")
                if email:
                    self._vip_cache[email.lower()] = True
    
    # ==================== EMAIL TRIAGE ====================
    
    def triage_email(self, email: Dict[str, Any], full_body: Optional[str] = None) -> TriagedEmail:
        """
        Triage a single email with intelligent analysis.
        
        Args:
            email: Email metadata from Gmail API
            full_body: Optional full email body for deeper analysis
            
        Returns:
            TriagedEmail with priority, categories, and analysis
        """
        triaged = TriagedEmail(
            id=email.get("id", ""),
            thread_id=email.get("thread_id", email.get("id", "")),
            subject=email.get("subject", "(no subject)"),
            sender=email.get("from", "Unknown"),
            sender_email=self._extract_email(email.get("from", "")),
            snippet=email.get("snippet", ""),
            date=email.get("date", ""),
            is_unread=email.get("is_unread", True),
        )
        
        # Check if sender is VIP
        triaged.sender_is_vip = self._is_vip(triaged.sender_email)
        
        # Analyze subject and snippet
        combined_text = f"{triaged.subject} {triaged.snippet}".lower()
        if full_body:
            combined_text += f" {full_body.lower()}"
        
        # Detect categories
        triaged.categories = self._detect_categories(combined_text, triaged.sender_email)
        
        # Calculate priority
        triaged.priority, triaged.importance_score = self._calculate_priority(
            triaged, combined_text
        )
        
        # Check for deadlines
        triaged.has_deadline, triaged.deadline = self._detect_deadline(combined_text)
        
        # Determine if response is needed
        triaged.requires_response = self._requires_response(triaged, combined_text)
        
        # Use LLM for deeper analysis if high priority
        if triaged.importance_score >= 0.7 and full_body:
            self._llm_analyze(triaged, full_body)
        
        return triaged
    
    def triage_inbox(
        self, 
        account_id: str = "primary", 
        query: str = "is:inbox",
        max_results: int = 50,
        deep_analyze_count: int = 10
    ) -> List[TriagedEmail]:
        """
        Triage all emails in inbox.
        
        Args:
            account_id: Gmail account to triage
            query: Gmail query for emails to triage
            max_results: Maximum emails to process
            deep_analyze_count: Number of top emails to analyze deeply
            
        Returns:
            List of triaged emails sorted by importance
        """
        # Fetch emails
        result = self.gmail.list_messages(
            account_id=account_id,
            query=query,
            max_results=max_results
        )
        messages = result.get("messages", [])
        
        # Triage each email
        triaged_emails = []
        for email in messages:
            triaged = self.triage_email(email)
            triaged_emails.append(triaged)
        
        # Sort by importance
        triaged_emails.sort(key=lambda e: e.importance_score, reverse=True)
        
        # Deep analyze top emails
        for triaged in triaged_emails[:deep_analyze_count]:
            if triaged.importance_score >= 0.5:
                try:
                    full_email = self.gmail.get_message(triaged.id, account_id)
                    self._llm_analyze(triaged, full_email.get("body", ""))
                except Exception:
                    pass
        
        # Learn from this triage session
        self._learn_from_triage(triaged_emails)
        
        return triaged_emails
    
    def _detect_categories(self, text: str, sender_email: str) -> List[EmailCategory]:
        """Detect email categories from content."""
        categories = []
        
        # Meeting detection
        if any(kw in text for kw in self.MEETING_KEYWORDS):
            categories.append(EmailCategory.MEETING)
        
        # Financial detection
        if any(kw in text for kw in self.FINANCIAL_KEYWORDS):
            categories.append(EmailCategory.FINANCIAL)
        
        # Newsletter detection
        if any(pattern in text for pattern in self.NEWSLETTER_PATTERNS):
            categories.append(EmailCategory.NEWSLETTER)
        
        # Automated email detection
        if "noreply" in sender_email or "no-reply" in sender_email:
            categories.append(EmailCategory.AUTOMATED)
        
        # Action required detection
        if "action required" in text or "please respond" in text or "waiting for" in text:
            categories.append(EmailCategory.ACTION_REQUIRED)
        
        # Default to FYI if no categories detected
        if not categories:
            categories.append(EmailCategory.FYI_ONLY)
        
        return categories
    
    def _calculate_priority(
        self, 
        triaged: TriagedEmail, 
        text: str
    ) -> Tuple[EmailPriority, float]:
        """Calculate email priority and importance score."""
        score = 0.5  # Base score
        
        # VIP sender boost
        if triaged.sender_is_vip:
            score += 0.3
        
        # Unread boost
        if triaged.is_unread:
            score += 0.1
        
        # Urgent keywords
        if any(kw in text for kw in self.URGENT_KEYWORDS):
            score += 0.4
            return EmailPriority.URGENT, min(score, 1.0)
        
        # High priority keywords
        if any(kw in text for kw in self.HIGH_PRIORITY_KEYWORDS):
            score += 0.2
        
        # Category adjustments
        if EmailCategory.ACTION_REQUIRED in triaged.categories:
            score += 0.2
        if EmailCategory.MEETING in triaged.categories:
            score += 0.1
        if EmailCategory.FINANCIAL in triaged.categories:
            score += 0.1
        if EmailCategory.NEWSLETTER in triaged.categories:
            score -= 0.3
        if EmailCategory.AUTOMATED in triaged.categories:
            score -= 0.2
        
        # Check learned sender importance
        sender_importance = self._get_sender_importance(triaged.sender_email)
        score += sender_importance * 0.2
        
        # Clamp score
        score = max(0.0, min(1.0, score))
        
        # Determine priority level
        if score >= 0.8:
            return EmailPriority.URGENT, score
        elif score >= 0.6:
            return EmailPriority.HIGH, score
        elif score >= 0.4:
            return EmailPriority.NORMAL, score
        elif EmailCategory.NEWSLETTER in triaged.categories:
            return EmailPriority.NEWSLETTER, score
        else:
            return EmailPriority.LOW, score
    
    def _detect_deadline(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect if email mentions a deadline."""
        deadline_patterns = [
            r"by\s+(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"deadline[:\s]+(\w+\s+\d+|\d+/\d+)",
            r"due\s+(by\s+)?(\w+\s+\d+|\d+/\d+)",
            r"before\s+(\w+\s+\d+|\d+/\d+)",
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return True, match.group(1)
        
        return False, None
    
    def _requires_response(self, triaged: TriagedEmail, text: str) -> bool:
        """Determine if email requires a response."""
        # Questions usually need response
        if "?" in triaged.subject or text.count("?") > 0:
            return True
        
        # Action required
        if EmailCategory.ACTION_REQUIRED in triaged.categories:
            return True
        
        # Meeting invites
        if EmailCategory.MEETING in triaged.categories:
            return True
        
        # Direct questions
        response_triggers = ["please let me know", "what do you think", "can you", "could you", 
                           "would you", "let me know", "respond by", "reply to"]
        if any(trigger in text for trigger in response_triggers):
            return True
        
        return False
    
    def _llm_analyze(self, triaged: TriagedEmail, body: str) -> None:
        """Use LLM for deeper email analysis."""
        prompt = f"""Analyze this email and provide:
1. A one-sentence summary
2. Up to 3 key points
3. Suggested actions (if any)
4. A brief suggested response (if response is needed)

Email:
Subject: {triaged.subject}
From: {triaged.sender}
Body:
{body[:2000]}

Respond in JSON format:
{{
    "summary": "...",
    "key_points": ["...", "..."],
    "suggested_actions": ["...", "..."],
    "suggested_response": "..." or null
}}"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                analysis = json.loads(json_match.group())
                triaged.summary = analysis.get("summary")
                triaged.key_points = analysis.get("key_points", [])
                triaged.suggested_actions = analysis.get("suggested_actions", [])
                triaged.suggested_response = analysis.get("suggested_response")
        except Exception:
            pass
    
    # ==================== LEARNING ====================
    
    def _learn_from_triage(self, emails: List[TriagedEmail]) -> None:
        """Learn patterns from triaged emails."""
        # Track sender interactions
        for email in emails:
            # Update or create contact profile
            contact = self.memory.get_contact(email.sender_email)
            if not contact:
                self.memory.add_contact(
                    email=email.sender_email,
                    name=email.sender,
                    attributes={
                        "is_vip": email.sender_is_vip,
                        "interaction_count": 1,
                        "avg_importance": email.importance_score,
                        "first_seen": datetime.now().isoformat(),
                    }
                )
            else:
                # Update existing contact
                count = contact.attributes.get("interaction_count", 0) + 1
                avg_importance = contact.attributes.get("avg_importance", 0.5)
                new_avg = (avg_importance * (count - 1) + email.importance_score) / count
                
                self.memory.semantic.update_contact(email.sender_email, {
                    "interaction_count": count,
                    "avg_importance": new_avg,
                    "last_seen": datetime.now().isoformat(),
                })
    
    def mark_vip(self, email: str, is_vip: bool = True, reason: str = None) -> bool:
        """
        Mark a contact as VIP.
        
        Args:
            email: Contact email
            is_vip: Whether to mark as VIP
            reason: Optional reason for VIP status
        """
        success = self.memory.semantic.update_contact(email, {
            "is_vip": is_vip,
            "vip_reason": reason,
            "vip_marked_at": datetime.now().isoformat(),
        })
        
        if success:
            self._vip_cache[email.lower()] = is_vip
            
            # Store as semantic memory
            self.memory.learn_fact(
                fact=f"{email} is marked as {'VIP' if is_vip else 'not VIP'}. Reason: {reason}",
                category="contact_status",
                agent_id=self.AGENT_ID,
                domain=self.DOMAIN
            )
        
        return success
    
    def learn_response_pattern(
        self,
        pattern_name: str,
        trigger_description: str,
        trigger_keywords: List[str],
        response_template: str,
        conditions: Dict[str, Any] = None
    ) -> str:
        """
        Learn a new email response pattern.
        
        Args:
            pattern_name: Name for this pattern
            trigger_description: When to use this pattern
            trigger_keywords: Keywords that trigger this pattern
            response_template: Template for the response
            conditions: Additional conditions
            
        Returns:
            Pattern ID
        """
        return self.memory.create_email_pattern(
            pattern_name=pattern_name,
            description=trigger_description,
            trigger_pattern=trigger_description,
            trigger_keywords=trigger_keywords,
            response_template=response_template,
            conditions=conditions,
            agent_id=self.AGENT_ID
        )
    
    def record_response_feedback(
        self,
        email_id: str,
        pattern_used: str,
        was_helpful: bool,
        user_edits: Optional[str] = None
    ) -> None:
        """
        Record feedback on a suggested response.
        
        Args:
            email_id: The email that was responded to
            pattern_used: The pattern that was used
            was_helpful: Whether the suggestion was helpful
            user_edits: What the user changed (if any)
        """
        # Update pattern confidence
        self.memory.record_procedure_outcome(pattern_used, success=was_helpful)
        
        # If user made edits, learn from them
        if user_edits and not was_helpful:
            # Store the user's preferred response as episodic memory
            self.memory.remember_interaction(
                content=f"User preferred response for email type '{pattern_used}': {user_edits}",
                agent_id=self.AGENT_ID,
                importance=0.8,
                metadata={
                    "type": "response_feedback",
                    "email_id": email_id,
                    "pattern": pattern_used,
                }
            )
    
    # ==================== DRAFT GENERATION ====================
    
    def draft_response(
        self,
        email: Dict[str, Any],
        tone: str = "professional",
        max_length: str = "medium",
        additional_context: str = None
    ) -> str:
        """
        Draft a response to an email using learned patterns and LLM.
        
        Args:
            email: The email to respond to
            tone: Response tone (professional, friendly, formal, casual)
            max_length: Response length (short, medium, long)
            additional_context: Additional context from user
            
        Returns:
            Drafted response text
        """
        subject = email.get("subject", "")
        sender = email.get("from", "")
        body = email.get("body", email.get("snippet", ""))
        
        # Find matching patterns
        context = f"Reply to: {subject} from {sender}: {body[:500]}"
        patterns = self.memory.find_procedures(context, agent_id=self.AGENT_ID)
        
        # Get relevant preferences
        preferences = self.memory.get_preferences(domain=self.DOMAIN)
        pref_text = "\n".join([f"- {p.content}" for p in preferences[:5]])
        
        # Get contact info
        sender_email = self._extract_email(sender)
        contact = self.memory.get_contact(sender_email)
        contact_info = ""
        if contact:
            contact_info = f"\nContact history: {contact.attributes}"
        
        # Build prompt
        pattern_text = ""
        if patterns:
            pattern_text = f"\nRelevant response patterns:\n"
            for p in patterns[:3]:
                pattern_text += f"- {p.name}: {p.action_template}\n"
        
        length_guide = {
            "short": "2-3 sentences",
            "medium": "1 short paragraph",
            "long": "2-3 paragraphs"
        }
        
        prompt = f"""Draft a {tone} email response. Keep it {length_guide.get(max_length, 'medium')}.

Original Email:
From: {sender}
Subject: {subject}
Body:
{body[:1500]}

User preferences:
{pref_text}
{contact_info}
{pattern_text}

{f'Additional context: {additional_context}' if additional_context else ''}

Write ONLY the response body (no subject line, no greeting analysis).
Start directly with the greeting."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Store this draft for learning
        self.memory.remember_interaction(
            content=f"Drafted response to '{subject}' from {sender}: {response.content[:200]}...",
            agent_id=self.AGENT_ID,
            importance=0.5,
            metadata={"type": "draft_generated", "email_subject": subject}
        )
        
        return response.content
    
    # ==================== SUMMARIZATION ====================
    
    def summarize_emails(
        self,
        emails: List[Dict[str, Any]],
        format: str = "bullet"
    ) -> str:
        """
        Summarize multiple emails.
        
        Args:
            emails: List of emails to summarize
            format: Output format (bullet, paragraph, brief)
            
        Returns:
            Summary text
        """
        if not emails:
            return "No emails to summarize."
        
        email_texts = []
        for email in emails[:10]:  # Limit to 10 emails
            email_texts.append(f"- From: {email.get('from')}\n  Subject: {email.get('subject')}\n  Snippet: {email.get('snippet', '')[:200]}")
        
        format_instructions = {
            "bullet": "Use bullet points, one per email",
            "paragraph": "Write a cohesive paragraph summary",
            "brief": "Give a 2-3 sentence overview"
        }
        
        prompt = f"""Summarize these {len(email_texts)} emails. {format_instructions.get(format, '')}

Emails:
{chr(10).join(email_texts)}

Provide a clear, actionable summary."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
    
    def daily_digest(self, account_id: str = "primary") -> Dict[str, Any]:
        """
        Generate a daily email digest.
        
        Returns:
            Dictionary with digest information
        """
        # Get unread emails
        unread = self.gmail.list_messages(account_id, query="is:unread", max_results=50)
        unread_emails = unread.get("messages", [])
        
        # Triage them
        triaged = self.triage_inbox(account_id, "is:unread", max_results=50, deep_analyze_count=5)
        
        # Categorize
        urgent = [e for e in triaged if e.priority == EmailPriority.URGENT]
        high = [e for e in triaged if e.priority == EmailPriority.HIGH]
        action_needed = [e for e in triaged if e.requires_response]
        newsletters = [e for e in triaged if e.priority == EmailPriority.NEWSLETTER]
        
        digest = {
            "generated_at": datetime.now().isoformat(),
            "total_unread": len(unread_emails),
            "urgent_count": len(urgent),
            "high_priority_count": len(high),
            "needs_response_count": len(action_needed),
            "newsletter_count": len(newsletters),
            "urgent_emails": [e.to_dict() for e in urgent],
            "high_priority_emails": [e.to_dict() for e in high[:5]],
            "needs_response": [e.to_dict() for e in action_needed[:5]],
            "summary": self.summarize_emails(
                [{"from": e.sender, "subject": e.subject, "snippet": e.snippet} for e in triaged[:10]],
                format="paragraph"
            )
        }
        
        # Store digest in episodic memory
        self.memory.remember_interaction(
            content=f"Daily digest: {digest['total_unread']} unread, {digest['urgent_count']} urgent, {digest['needs_response_count']} need response",
            agent_id=self.AGENT_ID,
            importance=0.7,
            metadata={"type": "daily_digest", "date": datetime.now().date().isoformat()}
        )
        
        return digest
    
    # ==================== HELPER METHODS ====================
    
    def _extract_email(self, from_string: str) -> str:
        """Extract email address from 'Name <email>' format."""
        match = re.search(r'<([^>]+)>', from_string)
        if match:
            return match.group(1).lower()
        # If no angle brackets, assume the whole string is an email
        return from_string.strip().lower()
    
    def _is_vip(self, email: str) -> bool:
        """Check if sender is a VIP."""
        email_lower = email.lower()
        
        # Check cache first
        if email_lower in self._vip_cache:
            return self._vip_cache[email_lower]
        
        # Check memory
        contact = self.memory.get_contact(email_lower)
        if contact and contact.attributes.get("is_vip"):
            self._vip_cache[email_lower] = True
            return True
        
        return False
    
    def _get_sender_importance(self, email: str) -> float:
        """Get learned importance score for a sender."""
        contact = self.memory.get_contact(email)
        if contact:
            return contact.attributes.get("avg_importance", 0.5)
        return 0.5


# Global Maya instance
_maya: Optional[Maya] = None


def get_maya() -> Maya:
    """Get the global Maya instance."""
    global _maya
    if _maya is None:
        _maya = Maya()
    return _maya

