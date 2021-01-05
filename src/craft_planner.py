
import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict. Functionality for hashing has been created.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        if 'Consumes' in rule:
            for item in rule['Consumes']:
                cost = rule['Consumes'][item]
                if not state[item] >= cost:
                    return False
        
        if 'Requires' in rule:
            for item in rule['Requires']:
                if not state[item] > 0:
                    return False
        return True

    return check


def make_effector(rule):
    #Returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        next_state = state.copy()

        if 'Produces' in rule:
            for item in rule['Produces']:
                next_state[item] = rule['Produces'][item] + next_state[item]

        if 'Consumes' in rule:
            for item in rule['Consumes']:
                next_state[item] = next_state[item] - rule['Consumes'][item]
                
        return next_state

    return effect


def make_goal_checker(goal):
    # Returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process 
        for item in goal:
            if not state[item] >= goal[item]:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)



def heuristic(state,action):
    # Heuristic is implemented here
    
    item_limit = {
        'coal': 1, 
        'cobble' : 8,
        'ingot' : 6,
        'ore' : 1,
        'plank' : 6,
        'stick' : 6,
        'wood' : 1
    }

    if state['bench'] > 1 :
        return inf

    if state['furnace'] > 1:
        return inf

    if state['wooden_axe'] > 0 or state['stone_axe'] > 0 or state['iron_axe'] > 0:
        return inf
    
    if state['wooden_pickaxe'] > 1 or state['stone_pickaxe'] > 1 or state['iron_pickaxe'] > 1:
        return inf

    if next(iter(Crafting['Recipes'][action]['Produces'])) in item_limit:
        if state[next(iter(Crafting['Recipes'][action]['Produces']))] > item_limit[next(iter(Crafting['Recipes'][action]['Produces']))]:
            return inf
    return 0


def search(graph, state, is_goal, limit, heuristic):

    start_time = time()
    
    # Seach is implemented here with the use of the heuristic.
    # Returns a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    begin = state.copy()
    visitedState = 0
    path = [()]

    while time() - start_time < limit:

        queue = [(0, begin)]
        distance = {begin: 0}
        curBackState = {begin: (None, None)}

        while queue is not None:
            current_cost, currentState = heappop(queue)
            visitedState += 1

            if is_goal(currentState):
                # List containing all cells from initial_position to destination
                path = [(currentState, 'Done')]
                previousState = curBackState[currentState][0] 
                previous_action = curBackState[currentState][1] 
                time1 = 0
                while previous_action is not None:

                    previousState = curBackState[previousState][0]   
                    previous_action = curBackState[previousState][1]
                    path.append((previousState, previous_action))
                    time1 += 1
                    # print(path)
                    # print("--------------------------------")
                    # print(curBackState)
                print('STATES VISITED: ' + str(visitedState))
                print ("len = " + str(time1))
                print('COST: ', distance[currentState])
                print(time() - start_time, 'seconds')
                return path[::-1]

            else:
                for graph_action, graph_state, graph_cost in graph(currentState.copy()):
                    total_cost = distance[currentState] + graph_cost 

                    if graph_state not in distance or total_cost < distance[graph_state]:
                        distance[graph_state] = total_cost
                        curBackState[graph_state] = (currentState, graph_action)
                        heappush(queue, (total_cost + heuristic(graph_state,graph_action), graph_state)) 

            if time() - start_time > limit:
                break

    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None


if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    #print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    #print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    #print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    #print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])
    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)
    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
