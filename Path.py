'''
Path.py
Contains the Path class which is used to find the optimal path to a goal
Or at least a possible path
Written by: Daniel Hocking
zID: 5184128
Date created: 14/05/2018
'''

from Bfs import Bfs
from AStar import AStar

class Path:

    def __init__(self, game_map):
        # Keep a reference to the game_map object
        self.game_map = game_map
        # Keep a reference to the player object
        self.player = game_map.player
        # Create new AStar object and keep reference to it
        self.a_star = AStar(self.game_map)
        # Create new Bfs object and keep reference to it
        self.bfs = Bfs(self.game_map)
        # Used to store the path as a set of coords
        self.path = []
        # Used to store the steps required to follow path
        self.steps = []

    '''
    This function takes a list of goal positions and then performs successive A*
    searches keeping track of state to find a path to each of the goals in turn.
    Is mainly used to find a path from current position to treasure and then back
    to the start
    '''
    def find_path_to_goal(self, goals):
        prev_state = None
        path = []
        start_pos = self.player.get_position()
        for goal in goals:
            a_star_search = self.a_star.perform_a_star_search(goal, (start_pos[0], start_pos[1]), True, prev_state)
            if a_star_search is None:
                path = None
                break
            start_pos = a_star_search[0][-1]
            path = path + a_star_search[0][1::]
            prev_state = a_star_search[1]

        return self._update_path(path)

    '''
    Gets a list of all relevant and known POI and ranks by distance from current
    location, then performs A* search until it finds a path to one of the POI
    '''
    def find_path_to_poi(self, cross_divide):
        path = None
        poi_list = self.game_map.find_nearest_poi(self.game_map.find_poi_list())
        for poi in poi_list:
            a_star_search = self.a_star.perform_a_star_search((poi[0], poi[1]), cross_divide=cross_divide)
            if a_star_search:
                path = a_star_search[0][1::]
                break

        return self._update_path(path)

    '''
    Uses the simplified BFS search to try and find a path to the nearest 
    unexplored area, if can't directly reach will start to look for areas
    that are close to unxplored regions
    '''
    def find_path_to_explore(self, cross_divide, waste_trees):
        path = None
        for search_radius in range(3):
            bfs_search = self.bfs.perform_bfs_search(cross_divide=cross_divide, expand_search=search_radius, waste_trees=waste_trees)
            if bfs_search:
                path = bfs_search[1::]
                break

        return self._update_path(path)

    '''
    Find the next step that should be taken by the agent to get closer to
    a goal
    '''
    def next_step(self):
        if self.has_steps():
            next_step = self.steps.pop(0)
            self.game_map.update_map_after_move(next_step)
            return next_step
        else:
            return ''

    '''
    Find if there are any steps left to take on a planned path
    '''
    def has_steps(self):
        return len(self.steps)

    '''
    Get rid of any existing steps or path
    '''
    def clear_steps(self):
        self.path = []
        self.steps = []

    '''
    Update the path and find steps if needed
    '''
    def _update_path(self, path):
        if path:
            self.path = path
            self._find_steps()
        return self.has_steps()

    '''
    Convert the path list which contains coords into a list of actions to take
    by the agent in order to carry out that path, this may require making turns,
    using tools, or moving forwards
    '''
    def _find_steps(self):
        # Can only create steps if there is a path to follow
        if len(self.path):
            self.steps = []
            current_pos = self.player.get_position()
            current_facing = current_pos[2]

            for new_pos in self.path:
                # Turn if needed
                change_facing = self.player.change_facing(current_pos, new_pos, current_facing)
                if change_facing[0] != 0:
                    current_facing = change_facing[1]
                    turn_dir = 'l' if change_facing[0] < 0 else 'r'
                    for _ in range(abs(change_facing[0])):
                        self.steps.append(turn_dir)
                # Determine what is in front of agent
                new_tile = self.game_map.map[new_pos[1]][new_pos[0]]
                # Use tool if needed
                if new_tile == '-':
                    if self.player.have_key:
                        self.steps.append('u')
                    else:
                        break
                if new_tile == 'T':
                    if self.player.have_axe:
                        self.steps.append('c')
                    else:
                        break
                # Move forward if possible
                if new_tile in ['*', '.', '']:
                    break
                self.steps.append('f')
                current_pos = new_pos


