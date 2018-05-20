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

    def a_star(self, start_pos=None, goal_coords=None, cross_divide=False, prev_state=None):
        game_state = self._setup_game_state(cross_divide, prev_state)
        if start_pos is None:
            player_pos = self.player.get_position()
            start_pos = (player_pos[0], player_pos[1])

        closed_set = set()
        open_set = {start_pos}
        came_from = dict()
        game_states = {start_pos:list(game_state)}

        g_score = defaultdict(lambda: self.MAXSTEPS)
        g_score[start_pos] = 0

        h_score = defaultdict(lambda: self.MAXSTEPS)
        h_score[start_pos] = self._manhattan_distance(start_pos, goal_coords)

        while len(open_set):
            current = min(open_set, key=lambda x: g_score[x] + h_score[x])
            game_state = game_states[current]
            if current == goal_coords:
                return self.reconstruct_path(came_from, current), game_state

            open_set.remove(current)
            closed_set.add(current)

            directions = self._new_directions([current])
            for direction in directions:
                new_pos = (current[0] + direction[0], current[1] + direction[1])
                new_game_state = list(game_state)
                if not self._valid_move(current, new_pos, new_game_state):
                    continue
                if new_pos in closed_set:
                    continue
                if new_pos not in open_set:
                    open_set.add(new_pos)

                tentative_g_score = g_score[current] + 1
                if tentative_g_score >= g_score[new_pos]:
                    continue
                game_states[new_pos] = new_game_state
                came_from[new_pos] = current
                g_score[new_pos] = tentative_g_score
                h_score[new_pos] = g_score[new_pos] + self._manhattan_distance(new_pos, goal_coords)
        return None

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return list(reversed(total_path))

    def find_chained_goals(self, goals):
        prev_state = None
        overall_path = []
        start_pos = self.player.get_position()
        for goal in goals:
            path = self.a_star((start_pos[0], start_pos[1]), goal, True, prev_state)
            if path is None:
                return None
            start_pos = path[0][-1]
            overall_path = overall_path + path[0][1::]
            prev_state = path[1]
        return overall_path

    def find_nearest_poi(self, cross_divide=False):
        poi_list = self.game_map.find_nearest_poi(self.game_map.find_poi_list())
        start_pos = self.player.get_position()
        for poi in poi_list:
            path = self.a_star((start_pos[0], start_pos[1]), (poi[0], poi[1]), cross_divide)
            if path:
                return path[0][1::]
        return None
