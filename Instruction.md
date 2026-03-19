FINAL PROJECT — GuildQuest Mini-Adventure Environment (GMAE)
Due Mar 19 by 11:59pm Points 100 Submitting a file upload Available after Feb 19 at 6:30pm
Changelog
Tue, Mar 3, 2026
Minimum team size reduced to 3
Thu, Feb 19 2026
Initial release version
Tue, Feb 17, 2026
Pre-release version created
Description
Design and implement an extensible GuildQuest Mini-Adventure Environment (GMAE).

For years, this course’s final project has focused on a Tile-Matching Game Environment. This quarter, you will build a GuildQuest environment framework that supports multiple mini-adventures set in the GuildQuest world and builds on two of your teammates' GuildQuest implementations from earlier assignments. 

A mini-adventure is a small, self-contained playable experience (co-op or competitive) that:

occurs in one or more realms/locations in the GuildQuest world,

involves entities (players, NPCs, items, hazards, etc.),

has rules, objectives, and a clear win/lose/complete condition.

You will work in teams of 4–5 students.

We will spend time in class to help everyone find a team in a timely manner. If you have excessive difficulty finding a team, we will assign you to one.

Requirements
Mini-adventure coverage.
The GMAE should accommodate mini-adventures that take place in the GuildQuest domain, typically involving a realm/map (often grid-like or coordinate-based) and entities placed in that space (e.g., characters, NPCs, items, hazards, obstacles, quest objectives).

Extensibility.
The GMAE should make it as easy as possible to create new mini-adventures.

Defined interface.
The GMAE must define a clear, documented interface that all mini-adventures implement.
Example interface capabilities (you decide specifics): initialize/start, accept player input, advance time/turns, report current state, detect completion/win/lose, and reset/restart.

Two players on one local machine.
The GMAE must support exactly two players on the same machine. The mini-adventure may be co-op or competitive, but it must be playable by two local players.

Player profiles.
The GMAE must support player profiles. Profiles should be meaningfully connected to the GuildQuest domain (e.g., character name, preferred realm, inventory snapshot, quest history, achievements, etc.).

Menu of mini-adventures.
The GMAE must present players with a list/menu of available mini-adventures and allow players to choose which one to play.

Build on your individual GuildQuest assignments (required reuse).
This final project must reuse (not rewrite from scratch) substantial portions of your team members’ individual GuildQuest assignments from this quarter.
Concretely, your team must integrate at least TWO previously-built GuildQuest subsystems into the GMAE + mini-adventures.
Examples of valid subsystems (choose any 2+ that match what you built this quarter):

realm/map model (realms, coordinates, travel, layout)

quest/event model (objectives, triggers, progress, completion)

item/inventory model (items, effects, loot, crafting, trading)

time / realm-local-time rules (timers, scheduled events, time windows)

permissions/sharing model (who can host/join/modify, roles, access control)

You must clearly document what you reused, where it lives in your repo, and how it is used in your final system.

Deliverables
You must submit:

The GMAE implementation

Runnable code via a CM repository like GitHub (e.g., include a runnable artifact and clear run instructions in your repo).

Two or more mini-adventures built on top of the GMAE

Each mini-adventure must be implemented as a module/plugin/implementation that uses the GMAE’s defined interface.

Documentation
Include the following in a “Final (updated) design document” (PDF recommended):

Your final design, including UML (as appropriate) with description/explanation.

Step-by-step instructions for how to create and add a new mini-adventure using your GMAE.

A retrospective on your design: how and why your updated design evolved from your original design, including high points, low points, and major challenges across the project.

Gen-AI deliverables in a clearly labeled section:

All prompts you used, especially key prompts and responses, as they are essentially like natural language-like programming code

The full AI responses,

What you changed in those responses, and

Why did you change them (reasoning/engineering judgment)

Your reasoning behind your modifications and your avoidance of simply copying and pasting too much of the generated designs are critical to receiving full extra credit or avoiding losing many points for academic dishonesty. If we suspect and can come up with enough evidence that you generated your assignment using AI but did not report it through extra credit, you can lose many points or be reported for academic misconduct. We will use multiple state-of-the-art techniques to identify improper use of generative AI in your assignments. 

 

Peer evaluations

They will be made available to you and your team, likely by the middle or end of the time period allocated between the time of release and the time the project is due.

Suggested mini-adventure ideas (pick any 2+)
You may implement any GuildQuest mini-adventures that fit the requirements. Here are examples that tend to reuse common GuildQuest subsystems:

Escort Across the Realm (co-op): escort an NPC to a target coordinate while hazards/events occur; items can help.

Relic Hunt (competitive or co-op): collect artifacts placed in a realm; first to N wins (or team completion).

Timed Raid Window: complete objectives before a realm-local time window ends.

Caravan Trade Run: fulfill trade orders across locations; win by completing orders or profit threshold.

Reuse rules
You cannot pick up an existing “GuildQuest environment / mini-adventure framework” implementation from the internet.

You may reuse libraries/components, but double-check with the professor if you are unsure.

You should reuse your own earlier GuildQuest code. That reuse is required (see Requirement #7).

“Valid reuse” checklist (include in your design doc)
For each reused subsystem:

Source: which assignment(s)/team member(s) it came from

Where in repo: folder/module names

What changed: refactors/adapters/wrappers you added

Where it’s used: which parts of GMAE and which mini-adventures depend on it

Evidence: screenshots, demo notes, unit tests, or short walkthrough

Grading Criteria (100 points)
Stakeholder: the player
How is the experience of playing a mini-adventure?

To what extent do your mini-adventures have reproducible bugs?

Are the rules/objectives clear, and is gameplay reasonably balanced for two local players?

Stakeholder: future developers of the GMAE

How is the understandability and overall quality of the code and design?

Is the architecture maintainable and appropriately modular (separation of concerns, cohesion/coupling, testability)?

Design patterns quality: Are the required design patterns applied appropriately (not just “for show”)? Do they improve modularity, extensibility, and maintainability of the GMAE and/or mini-adventures? Are pattern roles clear in code and documentation?

If your team intentionally retained code smells (per the requirements), are they responsibly contained, clearly documented, and supported by a convincing tradeoff rationale?

Stakeholder: mini-adventure developers

How extensible is the GMAE in supporting new mini-adventures?

How well do you hide parts of the GMAE that should not be exposed to mini-adventure developers?

How is the experience of building a new mini-adventure using your GMAE?

API + patterns support extensibility: Do the design patterns and overall architecture make it easier to add new mini-adventures cleanly through the defined interface? Is the extension workflow well-supported and clearly documented?

Stakeholder: requirements satisfaction

Does your system satisfy the functional requirements (menu of mini-adventures, two local players, player profiles, defined mini-adventure interface, 2+ mini-adventures built on top, required reuse of prior GuildQuest subsystems)?

Patterns requirement satisfied: Does the project meet the minimum of 2 non-security-focused design patterns and 2 security-focused design patterns?

Stakeholder: deliverables provided

Are all deliverables present and complete (runnable repo, 2 or more mini-adventures, final design document, UML as appropriate, instructions for running)?

Are the “how to add a new mini-adventure” instructions clear and accurate?

Justification quality in documentation: Does the design document clearly identify each design pattern and each intentional smell (with file/class references) and provide convincing engineering tradeoff justification for intentional smells retained?

Did you include your design retrospective (Deliverable 3.3)?
Stakeholder: you (individual contribution)

What are your contributions to the project? (inferred from repo evidence + peer evaluations)

Did you contribute meaningfully to both implementation and team process (as appropriate for your role)?

Extra Credit (optional)
A GUI for your GMAE + mini-adventures [3%]

At least one mini-adventure supports real-time play (not turn-based) [3%]

Submitting
Submit the final (updated) design document + retrospective to this Canvas assignment.
Your repo should remain accessible and runnable.
Suggestions
Split your team into sub-teams. Because teams are large, it will be most efficient to divide your team by problem areas. Also consider appointing a team lead.
Use of gen-AI can include the following, but please adhere to the gen-AI policy we've been using so far, which is mentioned earlier in this description:
Help you build game assets, especially if you decide to create a GUI (e.g., sprites of your characters, non-player characters, character or game-system dialog, grid or board elements of different types (e.g., water, grass, fire))
Help you design your mini-games (e.g., game rules)
In other words, make this project fun for yourself and your team
Rubric
Final Project
Final Project
Criteria	Ratings	Pts
This criterion is linked to a Learning OutcomePlayer Experience
See the grading criteria section in the project description
20 pts
This criterion is linked to a Learning OutcomeFuture GMAE Developer Experience
See the grading criteria section in the project description
20 pts
This criterion is linked to a Learning OutcomeMini-Adventure Developer Experience
See grading criteria section in the project description
20 pts
This criterion is linked to a Learning OutcomeRequirements Satisfaction
See grading criteria section in the project description
20 pts
This criterion is linked to a Learning OutcomeDeliverables Provided
See grading criteria section in the project description
20 pts
This criterion is linked to a Learning OutcomeIndividual Contributions
See grading criteria section in the project description
0 pts
This criterion is linked to a Learning OutcomeExtra Credit
See the associated section in the assignment description.
5 pts
Total Points: 105

