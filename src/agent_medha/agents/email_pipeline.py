"""
Email Analysis Pipeline

A background pipeline that:
- Periodically checks for new emails
- Triages and categorizes them
- Creates drafts for high-priority items
- Learns from user interactions
- Maintains inbox health metrics
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

from agent_medha.agents.maya import Maya, get_maya, TriagedEmail, EmailPriority
from agent_medha.memory.store import get_memory_store
from agent_medha.memory.base import MemoryDomain
from agent_medha.workers.email import gmail_client


logger = logging.getLogger(__name__)


class PipelineStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class PipelineConfig:
    """Configuration for the email pipeline."""
    check_interval_minutes: int = 15
    triage_batch_size: int = 50
    deep_analyze_count: int = 10
    auto_draft_urgent: bool = True
    auto_mark_read_newsletters: bool = False
    digest_time: str = "08:00"  # Daily digest time
    enabled_accounts: List[str] = field(default_factory=lambda: ["primary"])
    
    # Learning settings
    learn_from_responses: bool = True
    track_response_times: bool = True
    
    # Notification settings
    notify_urgent: bool = True
    notify_high_priority: bool = False


@dataclass
class PipelineRun:
    """Record of a single pipeline run."""
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    emails_processed: int = 0
    urgent_found: int = 0
    drafts_created: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "emails_processed": self.emails_processed,
            "urgent_found": self.urgent_found,
            "drafts_created": self.drafts_created,
            "errors": self.errors,
        }


class EmailPipeline:
    """
    Background email processing pipeline.
    
    Runs periodically to:
    - Check for new emails
    - Triage and categorize
    - Generate drafts for urgent items
    - Send notifications
    - Learn from patterns
    """
    
    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()
        self.maya = get_maya()
        self.memory = get_memory_store()
        
        self._status = PipelineStatus.IDLE
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_run: Optional[PipelineRun] = None
        self._run_history: List[PipelineRun] = []
        
        # Callbacks for notifications
        self._on_urgent: Optional[Callable[[List[TriagedEmail]], None]] = None
        self._on_digest: Optional[Callable[[Dict[str, Any]], None]] = None
    
    @property
    def status(self) -> PipelineStatus:
        return self._status
    
    @property
    def last_run(self) -> Optional[PipelineRun]:
        return self._last_run
    
    def set_urgent_callback(self, callback: Callable[[List[TriagedEmail]], None]) -> None:
        """Set callback for urgent email notifications."""
        self._on_urgent = callback
    
    def set_digest_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Set callback for daily digest."""
        self._on_digest = callback
    
    def start(self) -> None:
        """Start the background pipeline."""
        if self._status == PipelineStatus.RUNNING:
            logger.warning("Pipeline already running")
            return
        
        self._stop_event.clear()
        self._status = PipelineStatus.RUNNING
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Email pipeline started")
    
    def stop(self) -> None:
        """Stop the background pipeline."""
        self._stop_event.set()
        self._status = PipelineStatus.IDLE
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Email pipeline stopped")
    
    def pause(self) -> None:
        """Pause the pipeline."""
        self._status = PipelineStatus.PAUSED
        logger.info("Email pipeline paused")
    
    def resume(self) -> None:
        """Resume a paused pipeline."""
        if self._status == PipelineStatus.PAUSED:
            self._status = PipelineStatus.RUNNING
            logger.info("Email pipeline resumed")
    
    def run_once(self) -> PipelineRun:
        """Run the pipeline once (manually triggered)."""
        return self._process_emails()
    
    def _run_loop(self) -> None:
        """Main pipeline loop."""
        last_digest_date = None
        
        while not self._stop_event.is_set():
            try:
                if self._status == PipelineStatus.RUNNING:
                    # Process emails
                    self._process_emails()
                    
                    # Check for daily digest time
                    now = datetime.now()
                    if self._should_send_digest(now, last_digest_date):
                        self._send_daily_digest()
                        last_digest_date = now.date()
                
                # Wait for next interval
                self._stop_event.wait(self.config.check_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                self._status = PipelineStatus.ERROR
                self._stop_event.wait(60)  # Wait before retrying
    
    def _process_emails(self) -> PipelineRun:
        """Process emails for all configured accounts."""
        run = PipelineRun(started_at=datetime.now())
        
        try:
            for account_id in self.config.enabled_accounts:
                self._process_account(account_id, run)
            
            run.status = "completed"
        except Exception as e:
            run.status = "error"
            run.errors.append(str(e))
            logger.error(f"Pipeline processing error: {e}")
        
        run.completed_at = datetime.now()
        self._last_run = run
        self._run_history.append(run)
        
        # Keep only last 100 runs
        if len(self._run_history) > 100:
            self._run_history = self._run_history[-100:]
        
        # Store run in memory
        self.memory.remember_interaction(
            content=f"Pipeline run: {run.emails_processed} processed, {run.urgent_found} urgent",
            agent_id="maya",
            importance=0.3,
            metadata={"type": "pipeline_run", "run": run.to_dict()}
        )
        
        return run
    
    def _process_account(self, account_id: str, run: PipelineRun) -> None:
        """Process emails for a single account."""
        # Get new/unread emails
        triaged_emails = self.maya.triage_inbox(
            account_id=account_id,
            query="is:unread",
            max_results=self.config.triage_batch_size,
            deep_analyze_count=self.config.deep_analyze_count
        )
        
        run.emails_processed += len(triaged_emails)
        
        # Find urgent emails
        urgent_emails = [e for e in triaged_emails if e.priority == EmailPriority.URGENT]
        run.urgent_found += len(urgent_emails)
        
        # Notify about urgent emails
        if urgent_emails and self.config.notify_urgent and self._on_urgent:
            self._on_urgent(urgent_emails)
        
        # Auto-draft for urgent emails
        if self.config.auto_draft_urgent:
            for email in urgent_emails:
                if email.requires_response:
                    try:
                        draft = self._create_draft_for_email(account_id, email)
                        if draft:
                            run.drafts_created += 1
                    except Exception as e:
                        run.errors.append(f"Draft error for {email.id}: {e}")
        
        # Auto-mark newsletters as read
        if self.config.auto_mark_read_newsletters:
            newsletters = [e for e in triaged_emails if e.priority == EmailPriority.NEWSLETTER]
            for newsletter in newsletters:
                try:
                    # Mark as read (would need to implement this in Gmail client)
                    pass
                except Exception:
                    pass
    
    def _create_draft_for_email(self, account_id: str, email: TriagedEmail) -> Optional[str]:
        """Create a draft response for an email."""
        try:
            # Get full email content
            full_email = gmail_client.get_message(email.id, account_id)
            
            # Draft response
            response = self.maya.draft_response(
                full_email,
                tone="professional",
                max_length="medium"
            )
            
            # Create draft in Gmail
            result = gmail_client.create_draft(
                to=[email.sender_email],
                subject=f"Re: {email.subject}",
                body=response,
                account_id=account_id
            )
            
            # Store draft creation in memory
            self.memory.remember_interaction(
                content=f"Auto-drafted response to urgent email: {email.subject}",
                agent_id="maya",
                importance=0.6,
                metadata={
                    "type": "auto_draft",
                    "email_id": email.id,
                    "draft_id": result.get("draft_id"),
                }
            )
            
            return result.get("draft_id")
        except Exception as e:
            logger.error(f"Error creating draft: {e}")
            return None
    
    def _should_send_digest(self, now: datetime, last_digest_date) -> bool:
        """Check if it's time to send daily digest."""
        if last_digest_date and last_digest_date == now.date():
            return False
        
        try:
            digest_hour, digest_minute = map(int, self.config.digest_time.split(":"))
            return now.hour == digest_hour and now.minute < digest_hour + 5
        except ValueError:
            return False
    
    def _send_daily_digest(self) -> None:
        """Generate and send daily digest."""
        try:
            digest = self.maya.daily_digest()
            
            if self._on_digest:
                self._on_digest(digest)
            
            logger.info(f"Daily digest sent: {digest['total_unread']} unread emails")
        except Exception as e:
            logger.error(f"Error sending digest: {e}")
    
    # ==================== STATS & REPORTING ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        recent_runs = self._run_history[-10:]
        
        total_processed = sum(r.emails_processed for r in recent_runs)
        total_urgent = sum(r.urgent_found for r in recent_runs)
        total_drafts = sum(r.drafts_created for r in recent_runs)
        total_errors = sum(len(r.errors) for r in recent_runs)
        
        return {
            "status": self._status.value,
            "last_run": self._last_run.to_dict() if self._last_run else None,
            "recent_runs": len(recent_runs),
            "total_processed_recent": total_processed,
            "total_urgent_recent": total_urgent,
            "total_drafts_recent": total_drafts,
            "total_errors_recent": total_errors,
            "config": {
                "check_interval_minutes": self.config.check_interval_minutes,
                "enabled_accounts": self.config.enabled_accounts,
                "auto_draft_urgent": self.config.auto_draft_urgent,
            }
        }
    
    def get_inbox_health(self) -> Dict[str, Any]:
        """Get inbox health metrics."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "accounts": {}
        }
        
        for account_id in self.config.enabled_accounts:
            try:
                # Get inbox stats
                inbox = gmail_client.list_messages(account_id, "is:inbox", max_results=1)
                unread = gmail_client.list_messages(account_id, "is:unread", max_results=1)
                
                # Triage to get priority breakdown
                triaged = self.maya.triage_inbox(
                    account_id, "is:unread", max_results=100, deep_analyze_count=0
                )
                
                urgent_count = len([e for e in triaged if e.priority == EmailPriority.URGENT])
                high_count = len([e for e in triaged if e.priority == EmailPriority.HIGH])
                normal_count = len([e for e in triaged if e.priority == EmailPriority.NORMAL])
                low_count = len([e for e in triaged if e.priority == EmailPriority.LOW])
                newsletter_count = len([e for e in triaged if e.priority == EmailPriority.NEWSLETTER])
                
                health["accounts"][account_id] = {
                    "unread_count": len(triaged),
                    "urgent": urgent_count,
                    "high_priority": high_count,
                    "normal": normal_count,
                    "low_priority": low_count,
                    "newsletters": newsletter_count,
                    "needs_response": len([e for e in triaged if e.requires_response]),
                    "health_score": self._calculate_health_score(triaged),
                }
            except Exception as e:
                health["accounts"][account_id] = {"error": str(e)}
        
        return health
    
    def _calculate_health_score(self, emails: List[TriagedEmail]) -> float:
        """
        Calculate inbox health score (0-100).
        
        High score = healthy inbox (low urgent, manageable queue)
        Low score = inbox needs attention
        """
        if not emails:
            return 100.0
        
        score = 100.0
        
        # Penalize urgent emails
        urgent = len([e for e in emails if e.priority == EmailPriority.URGENT])
        score -= urgent * 10
        
        # Penalize high priority emails
        high = len([e for e in emails if e.priority == EmailPriority.HIGH])
        score -= high * 3
        
        # Penalize large unread count
        if len(emails) > 50:
            score -= (len(emails) - 50) * 0.5
        
        # Penalize emails needing response
        needs_response = len([e for e in emails if e.requires_response])
        score -= needs_response * 2
        
        return max(0.0, min(100.0, score))


# Global pipeline instance
_pipeline: Optional[EmailPipeline] = None


def get_email_pipeline(config: PipelineConfig = None) -> EmailPipeline:
    """Get the global email pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = EmailPipeline(config)
    return _pipeline


def start_email_pipeline(config: PipelineConfig = None) -> EmailPipeline:
    """Start the email pipeline."""
    pipeline = get_email_pipeline(config)
    pipeline.start()
    return pipeline


def stop_email_pipeline() -> None:
    """Stop the email pipeline."""
    global _pipeline
    if _pipeline:
        _pipeline.stop()

