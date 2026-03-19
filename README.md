# GMAE
INF 122 - GuildQuest Mini-Adventure Environment (GMAE)

## Requirements

Python 3.10+

## How to Run:
To run main.py:

Run directly from project directory

> python3 main.py

## Basic Usage

The application is fully menu-driven. All interaction happens through numbered CLI menus. The application will first ask for each player's display name, character class, and perferred realm. The application will then create profiles for each player. 

Then, it will display the main menu, where you can choose a mini-adventure to play by entering a number into the CLI that corresponds with its number on the menu. For now, the selectable mini-adventures are Escort Across the Realm (co-op) and Relic Hunt (competitive). 

## Escort Across the Realm
This co-op mini-adventure takes place in the realm Verdant Grove. The objective of this mini-adventure is to escort the NPC, Elara, safely to the target, all while avoiding hazards and using items to protect Elara. 
Each player takes turns moving on a grid. Each turn, the player can move in a cardinal direction by entering either north, east, south, or west. They can also choose to guard the NPC or wait. If Elara reaches the target, the players win. Otherwise, if 30 turns are completed without winning, or the players or Elara goes to 0 hp, the players lose.
### Hazards
A player can guard against a hazard, blocking it and removing it from the grid. However, hazards will continue to appear.
### Items
When a player encounters an item, they will automatically pick it up. Once picked up, the player who picked it up will now be able to use that item as one of their actions. 

## Relic Hunt
This competitive co-op adventure takes place in the realm Crystal Caverns. The objective is to collect relics in a grid, and the first player to reach 30 points wins. Each turn, the player can move in a cardinal direction by entering either north, east, south, or west, or they may wait. The player must collect relics (R) while avoiding hazards (H). If either player's HP reaches 0, the game will end. Regardless of score, the player who died loses. In the case that both players die, the game ends in a draw.
### Relics
The players' objectives are to collect relics until someone reaches 30 points, or someone dies by depleting their HP. Certain relics may be worth more points. 
### Hazards
Hazards will stun the player for one turn and deplete a certain amount of HP. Hazards will re-spawn in new positions after a player encounters a hazard.