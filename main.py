"""
main.py — Entry point for the GuildQuest Mini-Adventure Environment (GMAE).

Run from the repository root:
    python main.py

No external dependencies — standard library only.

Architecture overview
---------------------
  GMAE_Engine         : Microkernel core; manages players and the active adventure.
  IMiniAdventure      : Strategy interface all mini-adventures implement.
  RelicHunt           : Mini-adventure 1 — competitive relic collection.
  EscortQuest         : Mini-adventure 2 — co-operative NPC escort.
  PlayerProfileProxy  : Protection Proxy wrapping every User in the engine.
  RBACService         : Role-based permission checks (hero vs guest).
  RealmAdapter        : Adapter over the reused GuildQuest Realm subsystem.
  QuestEventAdapter   : Adapter over the reused GuildQuest QuestEvent subsystem.

Reused GuildQuest subsystems (required by project spec)
--------------------------------------------------------
  1. Realm / WorldClock / TimeRule  — core/realm.py, core/world_clock.py
  2. QuestEvent (Observer Pattern)  — core/quest_event.py

Design patterns in use
----------------------
  Non-security:
    Strategy  — engine.interface.IMiniAdventure / GMAE_Engine
    Observer  — core.quest_event.QuestEvent + adapters.quest_adapter.QuestEventAdapter
    Adapter   — adapters.realm_adapter, adapters.quest_adapter
  Security:
    Protection Proxy  — security.proxy.PlayerProfileProxy
    RBAC              — security.rbac.RBACService
"""

from engine.gmae_engine import GMAE_Engine
from adventures.relic_hunt import RelicHunt
from adventures.escort_quest import EscortQuest


def main() -> None:
    engine = GMAE_Engine()

    # Register mini-adventure plugins
    # To add a new adventure: import it and call engine.register_adventure()
    engine.register_adventure(RelicHunt())
    engine.register_adventure(EscortQuest())

    # Hand control to the menu / game loop
    engine.run()


if __name__ == "__main__":
    main()
