# Minecraft-Planner

TLDR:
- Built Python planner for a Minecraft item crafting problem which is able to craft a set of items described by a given goal through taking actions which obtain items, or      combine items into more complex ones
- Assists speed runners and novice players with more efficient crafting techniques

PROJECT DESCRIPTION AND GOALS: 
The planner is based on the A* algorithm and a heuristic has been designed for this problem. The purpose this planner is to “craft” a set of items described by a given goal. This is achieved by taking actions which can obtain items, or which can combine items into more complex ones. In this process, some items are consumed, and others may be required but not consumed (e.g. tools). A result of an action is the generation of a new item, according to the given recipes. The goal was to define a planning problem (initial state and goal state) using lists of objects and items and to implement the A* algorithm with a heuristic.

HEURISTIC GOALS: 
The heuristic was designed with pruning in mind to guide the search process in order to make it explore fewer states, and in turn make the algorithm run faster. The heuristic was created by analyzing the characteristics of the problem in order to find subproblems that are not worth exploring during the search. For example, in the Minecraft crafting problem there’s no reason to ever craft a tool (pickaxe, furnace, etc. -- things appearing in 'Requires' conditions) if you already have one of them. State-space planners often waste their time considering every possible ordering of order-insensitive actions.
