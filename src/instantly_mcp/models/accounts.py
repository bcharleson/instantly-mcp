"""
Pydantic models for Account operations.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class WarmupAdvancedSettings(BaseModel):
    """Advanced warmup configuration."""
    
    model_config = ConfigDict(extra="ignore")
    
    warm_ctd: Optional[bool] = Field(default=None, description="Warm CTD enabled")
    open_rate: Optional[int] = Field(default=None, ge=0, le=100, description="Target open rate %")
    important_rate: Optional[int] = Field(default=None, ge=0, le=100, description="Important rate %")
    read_emulation: Optional[bool] = Field(default=None, description="Read emulation enabled")
    spam_save_rate: Optional[int] = Field(default=None, ge=0, le=100, description="Spam save rate %")
    weekday_only: Optional[bool] = Field(default=None, description="Weekday only warmup")


class WarmupSettings(BaseModel):
    """Warmup configuration settings."""
    
    model_config = ConfigDict(extra="ignore")
    
    limit: Optional[int] = Field(default=None, ge=1, description="Daily warmup email limit")
    advanced: Optional[WarmupAdvancedSettings] = Field(default=None, description="Advanced settings")
    warmup_custom_ftag: Optional[str] = Field(default=None, description="Custom from tag")
    increment: Optional[str] = Field(default=None, description="Daily increment value")
    reply_rate: Optional[int] = Field(default=None, ge=0, le=100, description="Reply rate %")


class ListAccountsInput(BaseModel):
    """Input for listing email accounts."""
    
    # Use extra="ignore" to be tolerant of unexpected fields from LLMs
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    limit: Optional[int] = Field(
        default=100, ge=1, le=100,
        description="Results per page (1-100, default: 100)"
    )
    starting_after: Optional[str] = Field(
        default=None,
        description="Pagination cursor - use value from pagination.next_starting_after to get next page"
    )
    search: Optional[str] = Field(
        default=None,
        description="Search by email domain"
    )
    status: Optional[Literal[1, 2, -1, -2, -3]] = Field(
        default=None,
        description="1=Active, 2=Paused, -1/-2/-3=Errors"
    )
    provider_code: Optional[Literal[1, 2, 3, 4]] = Field(
        default=None,
        description="1=IMAP, 2=Google, 3=Microsoft, 4=AWS"
    )
    tag_ids: Optional[str] = Field(
        default=None,
        description="Comma-separated tag IDs"
    )


class GetAccountInput(BaseModel):
    """Input for getting account details."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    email: str = Field(..., description="Account email address")


class CreateAccountInput(BaseModel):
    """Input for creating an email account with IMAP/SMTP credentials."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    email: str = Field(..., description="Email address")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    provider_code: Literal[1, 2, 3, 4] = Field(
        ..., description="1=IMAP, 2=Google, 3=Microsoft, 4=AWS"
    )
    imap_username: str = Field(..., description="IMAP username")
    imap_password: str = Field(..., description="IMAP password")
    imap_host: str = Field(..., description="IMAP host (e.g., imap.gmail.com)")
    imap_port: int = Field(..., description="IMAP port (e.g., 993)")
    smtp_username: str = Field(..., description="SMTP username")
    smtp_password: str = Field(..., description="SMTP password")
    smtp_host: str = Field(..., description="SMTP host (e.g., smtp.gmail.com)")
    smtp_port: int = Field(..., description="SMTP port (e.g., 587)")


class UpdateAccountInput(BaseModel):
    """Input for updating account settings (partial update)."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    email: str = Field(..., description="Account to update")
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    warmup: Optional[WarmupSettings] = Field(default=None, description="Warmup configuration")
    daily_limit: Optional[int] = Field(default=None, ge=1, le=100, description="Daily send limit")
    sending_gap: Optional[int] = Field(
        default=None, ge=0, le=1440,
        description="Minutes between emails (0-1440)"
    )
    enable_slow_ramp: Optional[bool] = Field(default=None)
    tracking_domain_name: Optional[str] = Field(default=None)
    tracking_domain_status: Optional[str] = Field(default=None)
    skip_cname_check: Optional[bool] = Field(default=None)
    remove_tracking_domain: Optional[bool] = Field(default=None)
    inbox_placement_test_limit: Optional[int] = Field(default=None)


class ManageAccountStateInput(BaseModel):
    """Input for managing account state (pause, resume, warmup control, vitals test)."""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    email: str = Field(..., description="Account email")
    action: Literal["pause", "resume", "enable_warmup", "disable_warmup", "test_vitals"] = Field(
        ..., description="Action to perform"
    )


class DeleteAccountInput(BaseModel):
    """Input for deleting an account. ⚠️ PERMANENT - CANNOT UNDO!"""
    
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")
    
    email: str = Field(..., description="Email to DELETE PERMANENTLY")

