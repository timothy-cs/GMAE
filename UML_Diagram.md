---
title: GuildQuest Mini-Adventure Environment (GMAE) — UML Class Diagram
---
classDiagram
    %% ─────────────────────────────────────────
    %% ENUMS
    %% ─────────────────────────────────────────
    class VisibilityType {
        <<enumeration>>
        PUBLIC
        PRIVATE
    }

    class PermissionLevel {
        <<enumeration>>
        VIEW_ONLY
        COLLABORATIVE
    }

    class ThemeType {
        <<enumeration>>
        CLASSIC
        MODERN
    }

    class RarityType {
        <<enumeration>>
        COMMON
        RARE
        ULTRA_RARE
        LEGENDARY
    }

    class AdventureStatus {
        <<enumeration>>
        NOT_STARTED
        IN_PROGRESS
        WIN
        LOSE
        DRAW
    }

    %% ─────────────────────────────────────────
    %% GMAE CORE — NEW
    %% ─────────────────────────────────────────
    class GMEngine {
        <<GMAE Core>>
        -sessions : List~GameSession~
        -adventures : List~IMiniAdventure~
        +launchMenu() void
        +startSession(p1, p2, adv) GameSession
        +registerAdventure(adv) void
    }

    class MiniAdventureMenu {
        <<GMAE Core>>
        -adventures : List~IMiniAdventure~
        +display() void
        +select(index) IMiniAdventure
    }

    class IMiniAdventure {
        <<interface>>
        +initialize(session) void
        +acceptInput(player, input) void
        +advanceTurn() void
        +getState() AdventureState
        +checkCompletion() AdventureStatus
        +reset() void
    }

    class GameSession {
        <<GMAE Core>>
        +sessionId : UUID
        +player1 : PlayerProfile
        +player2 : PlayerProfile
        +adventure : IMiniAdventure
        +status : AdventureStatus
        +startTime : WorldTime
        +start() void
        +end() void
        +getResult() AdventureResult
    }

    class AdventureResult {
        <<GMAE Core>>
        +winner : PlayerProfile
        +duration : int
        +completedAt : WorldTime
        +summary : String
    }

    class AdventureState {
        <<GMAE Core>>
        +turnCount : int
        +entities : List~Entity~
        +objectives : List~String~
        +timeRemaining : int
    }

    class PlayerProfile {
        <<GMAE Core>>
        +profileId : UUID
        +displayName : String
        +preferredRealm : Realm
        +questHistory : List~String~
        +achievements : List~String~
        +updateHistory(quest) void
        +addAchievement(a) void
    }

    %% ─────────────────────────────────────────
    %% MINI-ADVENTURES — NEW
    %% ─────────────────────────────────────────
    class EscortAdventure {
        <<Mini-Adventure>>
        +npcTarget : Character
        +targetCoord : String
        +hazards : List~Entity~
        +initialize(session) void
        +acceptInput(player, input) void
        +advanceTurn() void
        +getState() AdventureState
        +checkCompletion() AdventureStatus
        +reset() void
    }

    class RelicHuntAdventure {
        <<Mini-Adventure>>
        +relics : List~InventoryItem~
        +scores : Map~PlayerProfile_int~
        +targetCount : int
        +initialize(session) void
        +acceptInput(player, input) void
        +advanceTurn() void
        +getState() AdventureState
        +checkCompletion() AdventureStatus
        +reset() void
    }

    %% ─────────────────────────────────────────
    %% REUSED — GHALIB'S REALM/INVENTORY SYSTEM
    %% ─────────────────────────────────────────
    class Realm {
        <<Reused: Ghalib>>
        +realmId : String
        +name : String
        +description : String
    }

    class Character {
        <<Reused: Ghalib>>
        +characterId : String
        +name : String
        +characterClass : String
        +level : int
    }

    class InventoryEntry {
        <<Reused: Ghalib>>
        +quantity : int
    }

    class InventoryItem {
        <<Reused: Ghalib>>
        +itemId : String
        +name : String
        +rarity : String
        +type : String
        +description : String
    }

    class CampaignSharing {
        <<Reused: Ghalib>>
        +permission : String
    }

    %% ─────────────────────────────────────────
    %% REUSED — ELLIS'S QUEST/TIME SYSTEM
    %% ─────────────────────────────────────────
    class Settings {
        <<Reused: Ellis>>
        +theme : ThemeType
        +timeDisplay : String
        +currentRealm : Realm
    }

    class QuestEvent {
        <<Reused: Ellis>>
        +eventId : UUID
        +title : String
        +startTime : WorldTime
        +endTime : WorldTime
        +assignRealm(r) void
        +addParticipant(c) void
    }

    class WorldClock {
        <<Reused: Ellis>>
        +currentTime : WorldTime
        +compare(t1, t2) int
        +addMinutes(t, m) WorldTime
    }

    class WorldTime {
        <<Reused: Ellis>>
        +days : int
        +hours : int
        +minutes : int
    }

    class LocalTimeRule {
        <<Reused: Ellis>>
        +offsetMinutes : int
        +dayLengthMultiplier : double
        +toLocal(t) LocalTime
    }

    class LocalTime {
        <<Reused: Ellis>>
        +days : int
        +hours : int
        +minutes : int
    }

    %% ─────────────────────────────────────────
    %% RELATIONSHIPS — GMAE CORE
    %% ─────────────────────────────────────────
    GMEngine "1" --> "1" MiniAdventureMenu : uses
    GMEngine "1" --> "*" IMiniAdventure : registers
    GMEngine "1" --> "*" GameSession : creates

    GameSession "1" --> "2" PlayerProfile : player1 / player2
    GameSession "1" --> "1" IMiniAdventure : runs
    GameSession "1" --> "1" AdventureResult : produces
    GameSession "1" --> "1" AdventureState : tracks state via
    GameSession "1" --> "1" WorldTime : startTime

    PlayerProfile "1" --> "1" Character : has
    PlayerProfile "1" --> "1" Realm : preferredRealm
    PlayerProfile "1" --> "1" Settings : uses

    %% ─────────────────────────────────────────
    %% RELATIONSHIPS — MINI-ADVENTURES
    %% ─────────────────────────────────────────
    EscortAdventure ..|> IMiniAdventure : implements
    RelicHuntAdventure ..|> IMiniAdventure : implements

    EscortAdventure "1" --> "1" Character : npcTarget
    EscortAdventure "1" --> "1" Realm : set in
    EscortAdventure "1" --> "1" QuestEvent : tracks via

    RelicHuntAdventure "1" --> "*" InventoryItem : relics
    RelicHuntAdventure "1" --> "1" Realm : set in
    RelicHuntAdventure "1" --> "1" QuestEvent : tracks via

    %% ─────────────────────────────────────────
    %% RELATIONSHIPS — GHALIB SUBSYSTEM
    %% ─────────────────────────────────────────
    Character "1" --> "0..*" InventoryEntry : inventory
    InventoryEntry "1" --> "1" InventoryItem : item
    InventoryItem --> RarityType : rarity
    CampaignSharing --> PermissionLevel : uses

    %% ─────────────────────────────────────────
    %% RELATIONSHIPS — ELLIS SUBSYSTEM
    %% ─────────────────────────────────────────
    QuestEvent "1" --> "1" Realm : occursIn
    QuestEvent "1" --> "1" WorldTime : startTime
    WorldClock "1" --> "1" WorldTime : tracks
    Realm "1" --> "1" LocalTimeRule : uses
    LocalTimeRule ..> LocalTime : produces
    Settings --> ThemeType : uses
    Settings --> VisibilityType : uses