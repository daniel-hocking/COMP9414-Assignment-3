'''
Bfs.py
Contains the Bfs class which extends the Search class and implements BFS
It should be noted that this is a modified BFS that sacrifices optimality
in exchange for being significantly faster, which makes it good for
general exploration
Written by: Daniel Hocking
zID: 5184128
Date created: 18/05/2018
'''

from collections import deque
from Search import Search

class Bfs(Search):

    def __init__(self, game_map):
        super().__init__(game_map)

    '''
    This function carries out the modified BFS, it has a number of optional parameters
    A lot of the options were previously used for finding POI's but this was later
    changed to use A* search instead
    pos: is the start position if none supplied will use current position
    goal_coords: is a list of goal coords if none supplied will look for unexplored areas
    cross_divide: is search allowed to cross between land -> water or the reverse
    prev_state: when simulating chained goals this is the initial state, if none
        then use current player state
    expand_search: if > 0 then only need to get within n tiles of the goal state
    waste_trees: can trees be cut down when a raft is already held
    '''
    def perform_bfs_search(self, pos=None, goal_coords=None, cross_divide=False, prev_state=None, expand_search=0, waste_trees=False):
        game_state = self._setup_game_state(cross_divide, prev_state, waste_trees)
        # Minor efficiency improvement by using a deque which has fast access
        # to both ends
        queue = deque()
        explored = set()
        if pos is None:
            pos = self.player.get_position()
        # Must store game_state along with the path otherwise item use/pickups
        # won't be factored in to checks
        queue.append(([(pos[0], pos[1])], game_state))
        # Keep track of where has already been explored so as not to re-explore
        # This greatly reduces number of tiles visited (only ever visit each once)
        # But it also means the path may not be the most direct
        explored.add((pos[0], pos[1]))
        found = False
        while len(queue):
            path, game_state = queue.popleft()
            directions = self._new_directions(path)
            pos = path[-1]
            # Now check each of the four possible directions
            # Add to path if not in explored and a possible move
            for direction in directions:
                new_pos = (pos[0] + direction[0], pos[1] + direction[1])
                # If new_pos in goal_coords hopefully have shortest path to a goal
                if goal_coords is not None and new_pos in goal_coords:
                    path.append(new_pos)
                    found = True
                    break
                # Check if new position is unexplored, this is the goal
                if goal_coords is None and \
                        self.game_map.any_unexplored_nearby(new_pos, expand_search):
                    found = True
                    break
                if new_pos not in explored:
                    new_game_state = list(game_state)
                    if self._valid_move(pos, new_pos, new_game_state):
                        queue.append((path + [new_pos], new_game_state))
                        explored.add(new_pos)

            if found:
                return path
        return None
