'''
AStar.py
Contains the AStar class which extends the Search class and implements A*
Uses pseudocode from: https://en.wikipedia.org/wiki/A*_search_algorithm
Written by: Daniel Hocking
zID: 5184128
Date created: 18/05/2018
'''

from Search import Search
from collections import defaultdict

class AStar(Search):

    # No path can be longer than this
    MAXSTEPS = 10000

    def __init__(self, game_map):
        super().__init__(game_map)

    '''
    This function carries out A* search using the Manhattan distance as the
    heuristic for determining which game states to explore first, the
    optional parameters include
    goal_coords: the goal location (is required)
    start_pos: is the start position if none supplied will use current position
    cross_divide: is search allowed to cross between land -> water or the reverse
    prev_state: when simulating chained goals this is the initial state, if none
        then use current player state
    '''
    def perform_a_star_search(self, goal_coords, start_pos=None, cross_divide=False, prev_state=None, waste_trees=False):
        game_state = self._setup_game_state(cross_divide, prev_state, waste_trees)
        if start_pos is None:
            player_pos = self.player.get_position()
            start_pos = (player_pos[0], player_pos[1])

        # Because game_state is so relevant to solvability of the problem it is
        # included with the current position to make up the overall state, so two
        # different states at the same position count separately
        start_state = start_pos + tuple(game_state)
        closed_set = set()
        open_set = {start_state}
        came_from = dict()

        # g_score is path length at that state, default to maxsteps
        g_score = defaultdict(lambda: self.MAXSTEPS)
        g_score[start_state] = 0

        # h_score is herusitic score at that statem default to maxsteps
        h_score = defaultdict(lambda: self.MAXSTEPS)
        h_score[start_state] = self._manhattan_distance(start_pos, goal_coords)

        while len(open_set):
            # Find the state in open_set with lowest overall g_score + h_score
            current = min(open_set, key=lambda x: g_score[x] + h_score[x])
            current_pos = current[:2:]
            game_state = list(current)[2::]
            # Reached the goal so find path used to get there
            if current_pos == goal_coords:
                return self._reconstruct_path(came_from, current), game_state

            open_set.remove(current)
            closed_set.add(current)

            # Find possible new moves and check if they are valid/worthwhile moves
            directions = self._new_directions([current_pos])
            for direction in directions:
                new_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
                new_game_state = list(game_state)
                if not self._valid_move(current_pos, new_pos, new_game_state):
                    continue
                new_state = new_pos + tuple(new_game_state)
                if new_state in closed_set:
                    continue
                if new_state not in open_set:
                    open_set.add(new_state)

                # If a more direct path already found then don't try this
                tentative_g_score = g_score[current] + 1
                if tentative_g_score >= g_score[new_state]:
                    continue
                # If it all checks out then add new state
                came_from[new_state] = current
                g_score[new_state] = tentative_g_score
                h_score[new_state] = g_score[new_state] + self._manhattan_distance(new_pos, goal_coords)
        return None

    '''
    Once the goal has been found this is used to find out what path was used
    to get to that goal state
    '''
    def _reconstruct_path(self, came_from, current):
        total_path = [(current[0], current[1])]
        while current in came_from:
            current = came_from[current]
            total_path.append((current[0], current[1]))
        return list(reversed(total_path))
