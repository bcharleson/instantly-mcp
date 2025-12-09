"""
Instantly MCP Server - Pydantic Models

Input validation models for all API operations.
Using Pydantic v2 for automatic validation and OpenAPI schema generation.
"""

from .common import PaginationParams, PaginationResponse
from .accounts import (
    ListAccountsInput,
    GetAccountInput,
    CreateAccountInput,
    UpdateAccountInput,
    ManageAccountStateInput,
    DeleteAccountInput,
)
from .campaigns import (
    CreateCampaignInput,
    ListCampaignsInput,
    GetCampaignInput,
    UpdateCampaignInput,
    ActivateCampaignInput,
    PauseCampaignInput,
)
from .leads import (
    ListLeadsInput,
    GetLeadInput,
    CreateLeadInput,
    UpdateLeadInput,
    ListLeadListsInput,
    CreateLeadListInput,
    UpdateLeadListInput,
    GetVerificationStatsInput,
    BulkAddLeadsInput,
    DeleteLeadInput,
    MoveLeadsInput,
)
from .emails import (
    ListEmailsInput,
    GetEmailInput,
    ReplyToEmailInput,
    VerifyEmailInput,
)
from .analytics import (
    GetCampaignAnalyticsInput,
    GetDailyCampaignAnalyticsInput,
    GetWarmupAnalyticsInput,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginationResponse",
    # Accounts
    "ListAccountsInput",
    "GetAccountInput",
    "CreateAccountInput",
    "UpdateAccountInput",
    "ManageAccountStateInput",
    "DeleteAccountInput",
    # Campaigns
    "CreateCampaignInput",
    "ListCampaignsInput",
    "GetCampaignInput",
    "UpdateCampaignInput",
    "ActivateCampaignInput",
    "PauseCampaignInput",
    # Leads
    "ListLeadsInput",
    "GetLeadInput",
    "CreateLeadInput",
    "UpdateLeadInput",
    "ListLeadListsInput",
    "CreateLeadListInput",
    "UpdateLeadListInput",
    "GetVerificationStatsInput",
    "BulkAddLeadsInput",
    "DeleteLeadInput",
    "MoveLeadsInput",
    # Emails
    "ListEmailsInput",
    "GetEmailInput",
    "ReplyToEmailInput",
    "VerifyEmailInput",
    # Analytics
    "GetCampaignAnalyticsInput",
    "GetDailyCampaignAnalyticsInput",
    "GetWarmupAnalyticsInput",
]

