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
        # Start by looking for any possible path, if one is found then see if
        # there is something less destructive, this stops the path from cutting
        # down trees or crossing water when it merely saves a few steps
        path = self._find_path_to_goal(goals)
        if path is not None:
            path_no_tree = self._find_path_to_goal(goals, waste_trees=False)
            if path_no_tree is not None:
                path = path_no_tree
                path_no_water = self._find_path_to_goal(goals, False, False)
                if path_no_water is not None:
                    path = path_no_water

        return self._update_path(path)

    def _find_path_to_goal(self, goals, cross_divide = True, waste_trees = True):
        prev_state = None
        path = []
        start_pos = self.player.get_position()
        for goal in goals:
            #search = self.a_star.perform_a_star_search(goal, (start_pos[0], start_pos[1]), cross_divide, prev_state, waste_trees)
            search = self.bfs.perform_bfs_search((start_pos[0], start_pos[1]), [goal],
                        cross_divide=cross_divide, prev_state=prev_state, waste_trees=waste_trees)
            if search is None:
                path = None
                break
            start_pos = search[0][-1]
            path = path + search[0][1::]
            prev_state = search[1]

        return path

    '''
    Gets a list of all relevant and known POI and ranks by distance from current
    location, then performs A* search until it finds a path to one of the POI
    '''
    def find_path_to_poi(self, cross_divide=False):
        path = None
        poi_list = self.game_map.find_nearest_poi(self.game_map.find_poi_list())
        for poi in poi_list:
            #search = self.a_star.perform_a_star_search((poi[0], poi[1]), cross_divide=cross_divide)
            search = self.bfs.perform_bfs_search(goal_coords=[(poi[0], poi[1])], cross_divide=cross_divide)
            if search:
                path = search[0][1::]
                break

        return self._update_path(path)

    '''
    Uses the simplified BFS search to try and find a path to the nearest 
    unexplored area, if can't directly reach will start to look for areas
    that are close to unxplored regions
    '''
    def find_path_to_explore(self, cross_divide=False, waste_trees=False):
        path = None
        for search_radius in range(3):
            bfs_search = self.bfs.perform_bfs_search(cross_divide=cross_divide, expand_search=search_radius, waste_trees=waste_trees)
            if bfs_search:
                path = bfs_search[0][1::]
                break

        return self._update_path(path)

    '''
    First build up a set containing the inaccessible_regions that might be of interest
    to explore and then perform a BFS allowing the use of stones to reach them
    '''
    def find_path_to_new_land(self):
        accessible_region, inaccessible_region = self.game_map.find_unexplored_regions()
        path = None
        bfs_search = self.bfs.perform_bfs_search(goal_coords=inaccessible_region, use_stones=True)
        if bfs_search:
            path = bfs_search[0][1::]
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


