"""
Pydantic models for Email operations.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class ListEmailsInput(BaseModel):
    """Input for listing emails with pagination and filtering."""
    
    # Use extra="ignore" to be tolerant of unexpected fields from LLMs
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    limit: Optional[int] = Field(default=100, ge=1, le=100, description="Results per page (1-100, default: 100)")
    starting_after: Optional[str] = Field(
        default=None, 
        description="Pagination cursor - use value from pagination.next_starting_after to get next page"
    )
    search: Optional[str] = Field(
        default=None,
        description="Search (use 'thread:UUID' for threads)"
    )
    campaign_id: Optional[str] = Field(default=None)
    i_status: Optional[int] = Field(default=None, description="Interest status")
    eaccount: Optional[str] = Field(
        default=None,
        description="Sender accounts (comma-separated)"
    )
    is_unread: Optional[bool] = Field(default=None)
    has_reminder: Optional[bool] = Field(default=None)
    mode: Optional[Literal["emode_focused", "emode_others", "emode_all"]] = Field(default=None)
    preview_only: Optional[bool] = Field(default=None)
    sort_order: Optional[Literal["asc", "desc"]] = Field(default=None)
    scheduled_only: Optional[bool] = Field(default=None)
    assigned_to: Optional[str] = Field(default=None)
    lead: Optional[str] = Field(default=None, description="Lead email")
    company_domain: Optional[str] = Field(default=None)
    marked_as_done: Optional[bool] = Field(default=None)
    email_type: Optional[Literal["received", "sent", "manual"]] = Field(default=None)


class GetEmailInput(BaseModel):
    """Input for getting email details."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    email_id: str = Field(..., description="Email UUID")


class EmailBody(BaseModel):
    """Email body content."""
    
    model_config = ConfigDict(extra="ignore")
    
    html: Optional[str] = Field(default=None, description="HTML content")
    text: Optional[str] = Field(default=None, description="Plain text content")


class ReplyToEmailInput(BaseModel):
    """
    Input for replying to an email.
    
    🚨 SENDS REAL EMAIL! Confirm with user first. Cannot undo!
    """
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    reply_to_uuid: str = Field(..., description="Email UUID to reply to")
    eaccount: str = Field(..., description="Sender account (must be active)")
    subject: str = Field(..., description="Subject line")
    body: EmailBody = Field(..., description="Email body (html or text)")


class VerifyEmailInput(BaseModel):
    """
    Input for verifying email deliverability.

    Takes 5-45 seconds. Returns status, score, flags.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    email: str = Field(..., description="Email to verify")
    max_wait_seconds: Optional[int] = Field(
        default=45,
        ge=0,
        le=120,
        description="Maximum time to wait for verification (0 to return immediately, default: 45)"
    )
    poll_interval_seconds: Optional[float] = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Time between polling attempts (default: 2 seconds)"
    )
    skip_polling: Optional[bool] = Field(
        default=False,
        description="Return immediately even if status is pending (default: false)"
    )


class MarkThreadAsReadInput(BaseModel):
    """
    Input for marking an email thread as read.

    Marks all emails in the thread as read.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    thread_id: str = Field(..., description="Thread UUID to mark as read")

