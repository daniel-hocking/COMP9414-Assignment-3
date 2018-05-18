'''
Bfs.py
Contains the Bfs class which extends the Search class and implements BFS
Written by: Daniel Hocking
zID: 5184128
Date created: 18/05/2018
'''

from collections import deque
from Search import Search

class Bfs(Search):
    def __init__(self, game_map):
        super().__init__(game_map)

    def _perform_bfs_search(self, pos=None, goal_coords=None, cross_divide=False, prev_state=None):
        # goal_coords = None means looking for unexplored area
        # Otherwise expects a list of coords to find path to
        # cross_divide means going from land -> water or water -> land
        game_state = [self.player.have_axe, self.player.have_key, self.player.have_treasure,
                      0, False, cross_divide, self.player.on_raft, False]
        if cross_divide:
            if prev_state is not None:
                game_state = list(prev_state)
            else:
                game_state[3] = self.player.num_stones_held
                game_state[4] = self.player.have_raft
        print(f'game_state {game_state}')
        queue = deque()
        explored = set()
        if pos is None:
            pos = self.player.get_position()
        queue.append(([(pos[0], pos[1])], game_state))
        explored.add((pos[0], pos[1]))
        found = False
        while len(queue):
            path, game_state = queue.popleft()
            print(f'abc path {path}  game_state {game_state}')
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
                        self.game_map.map[new_pos[1]][new_pos[0]] == '':
                    found = True
                    break
                if new_pos not in explored:
                    game_state = list(game_state)
                    is_valid = self._valid_move(pos, new_pos, game_state)
                    if is_valid:
                        queue.append((path + [new_pos], game_state))
                        explored.add(new_pos)

            if found:
                return path, game_state
        return None

    def find_nearest_unexplored(self, cross_divide=False):
        path = self._perform_bfs_search(None, None, cross_divide)
        if path:
            print(f'cross_divide {cross_divide} game_state {path}')
            return path[0]
        return None

    def find_nearest_poi(self, cross_divide=False):
        poi_list = self.game_map.find_poi_list()
        if len(poi_list):
            print(f'poi_list {poi_list}')
            path = self._perform_bfs_search(None, poi_list, cross_divide)
            if path:
                return path[0]
        return None

    def find_chained_goals(self, goals):
        prev_state = None
        overall_path = []
        start_pos = self.player.get_position()
        for goal in goals:
            path = self._perform_bfs_search(start_pos, [goal], True, prev_state)
            if path is None:
                return None
            start_pos = path[0][-1]
            print(f'patial path: {path}')
            overall_path = overall_path + path[0][1::]
            prev_state = path[1]
        return overall_path