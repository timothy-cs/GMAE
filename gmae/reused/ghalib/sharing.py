"""Campaign sharing model — reused from Ghalib's individual GuildQuest assignment.

Manages permission levels for shared campaigns/sessions.
Adapted for GMAE: used for access control in game sessions.
"""

from __future__ import annotations
from dataclasses import dataclass
from gmae.enums import PermissionLevel


@dataclass
class CampaignSharing:
    campaign_id: str
    owner_id: str
    shared_with_id: str
    permission: PermissionLevel

    def can_modify(self) -> bool:
        return self.permission == PermissionLevel.COLLABORATIVE

    def can_view(self) -> bool:
        return True  # Both levels can view

    def __str__(self) -> str:
        return f"Campaign {self.campaign_id}: {self.shared_with_id} has {self.permission.value}"
