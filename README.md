# GuildQuest Mini-Adventure Environment (GMAE)

INF 122 — Final Project
Team: Timothy Le, Ethan Votran, Jordan Moreno, Ellis Liang, Ghalib

---

## How to Run

**Requirements:** Python 3.10 or later (standard library only — no pip installs needed).

```bash
# From the repo root:
python3 main.py
```

The game will walk you through profile setup for both players, then present the mini-adventure menu.

---

## Project Structure

```
GMAE/
├── main.py                     # Entry point — registers adventures, starts engine
├── engine/
│   ├── interface.py            # IMiniAdventure — the extensibility interface
│   └── gmae_engine.py          # GMAE_Engine — microkernel core
├── core/                       # Reused GuildQuest subsystems (Part 1)
│   ├── world_clock.py          # WorldClock — universal game time
│   ├── realm.py                # Realm + TimeRule — physical locations
│   ├── quest_event.py          # QuestEvent — Observer Pattern subject
│   ├── inventory.py            # Inventory + Item
│   ├── character.py            # Character (name, class, level)
│   └── user.py                 # User (player profile)
├── adapters/                   # Adapter Pattern — fit subsystems into GMAE
│   ├── realm_adapter.py        # RealmAdapter — adds grid layer to Realm
│   └── quest_adapter.py        # QuestEventAdapter — cleaner event API
├── security/
│   ├── proxy.py                # PlayerProfileProxy — Protection Proxy
│   └── rbac.py                 # RBACService — Role-Based Access Control
├── adventures/
│   ├── relic_hunt.py           # Mini-Adventure 1: Relic Hunt (competitive)
│   └── escort_quest.py         # Mini-Adventure 2: Escort Across the Realm (co-op)
├── profiles/
│   ├── profile_manager.py      # Profile creation, save, and load
│   └── saves/                  # JSON profile files (auto-created)
└── ui/
    └── menu.py                 # Main menu and in-game loop
```

---

## Mini-Adventures

### 1. Relic Hunt (Competitive)
Two players race across an 8×8 grid to collect relics (`*`). First to collect **3 relics** wins.

| Player | Move     | Collect |
|--------|----------|---------|
| P1     | W A S D  | E       |
| P2     | I J K L  | U       |

### 2. Escort Across the Realm (Co-operative)
Both players work together to push an NPC (`N`) to the target (`X`) within **40 turns** while avoiding roaming hazards (`@`). At the halfway point, hazards move faster.

| Player | Move     | Push NPC                     |
|--------|----------|------------------------------|
| P1     | W A S D  | E (when adjacent to NPC)     |
| P2     | I J K L  | U (when adjacent to NPC)     |

---

## How to Add a New Mini-Adventure

1. Create a new file in `adventures/` (e.g., `adventures/dungeon_run.py`).
2. Define a class that extends `IMiniAdventure` from `engine/interface.py`.
3. Implement all six abstract methods:
   - `initialize(players, realm)` — set up the adventure state
   - `handle_input(player_id, action, **kwargs) → str` — process one player action
   - `update(delta_time)` — advance autonomous logic (no-op for turn-based)
   - `check_completion() → bool` — return True when the adventure ends
   - `get_status() → dict` — return a state snapshot (must include `"adventure"`, `"done"`, `"last_message"`)
   - `reset()` — restore to initial state
4. Add the `name` and `description` properties.
5. In `main.py`, add one line:
   ```python
   from adventures.dungeon_run import DungeonRun
   engine.register_adventure(DungeonRun())
   ```
   The menu will automatically list it — no other changes needed.

---

## Design Patterns

| Pattern             | Type         | Location                                                    |
|---------------------|--------------|-------------------------------------------------------------|
| Strategy            | Non-security | `engine/interface.py` + `engine/gmae_engine.py`             |
| Observer            | Non-security | `core/quest_event.py` + `adapters/quest_adapter.py`         |
| Adapter             | Non-security | `adapters/realm_adapter.py`, `adapters/quest_adapter.py`    |
| Protection Proxy    | Security     | `security/proxy.py`                                         |
| Role-Based Access Control | Security | `security/rbac.py`                                        |

---

## Reused GuildQuest Subsystems

| Subsystem                  | Source                          | Files                                       | Used In                                                  |
|----------------------------|---------------------------------|---------------------------------------------|----------------------------------------------------------|
| WorldClock                 | Ethan Votran — GuildQuest Part 1 | `core/world_clock.py`                      | Realm local time, QuestEvent windows, EscortQuest turns  |
| Realm + TimeRule           | Ethan Votran — GuildQuest Part 1 | `core/realm.py`                            | RealmAdapter grid layer, all mini-adventures             |
| QuestEvent (Observer)      | Ethan Votran — GuildQuest Part 1 | `core/quest_event.py`                      | QuestEventAdapter, EscortQuest midpoint warning          |
| Character + Inventory      | Ethan Votran — GuildQuest Part 1 | `core/character.py`, `core/inventory.py`   | User/PlayerProfile, loot grants via proxy                |

---

## Player Profiles

Profiles are saved to `profiles/saves/<username>.json` automatically after each game.
On next launch, entering the same username will offer to load the existing profile
(quest history, achievements, character).
