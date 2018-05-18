'''
Search.py
Contains the Search class which is the base class used to find paths
Bfs, IdaStar, Ida all extend it for some common functionality
Written by: Daniel Hocking
zID: 5184128
Date created: 18/05/2018
'''

'''
Base class for search, Bfs and IdaStar extend it
'''
class Search:

    # Determine valid movements based on current direction of movement, favour continue straight line
    NEW_MOVEMENTS = {(0, -1): [(0, -1), (-1, 0), (1, 0)],
                  (1, 0): [(1, 0), (0, -1), (0, 1)],
                  (0, 1): [(0, 1), (1, 0), (-1, 0)],
                  (-1, 0): [(-1, 0), (0, 1), (0, -1)]}

    def __init__(self, game_map):
        self.game_map = game_map
        self.player = self.game_map.player

    def _valid_move(self, current_pos, new_pos, game_state):
        # game_state: axe, key, treasure, stones, raft, cross_divide, on_raft, on_stone
        current_tile = self.game_map.map[current_pos[1]][current_pos[0]]
        new_tile = self.game_map.map[new_pos[1]][new_pos[0]]

        if current_tile == '~' and new_tile == '~' and game_state[6]:
            return True
        if current_tile == '~' and new_tile != '~' and not game_state[5] and not game_state[7]:
            return False
        if current_tile == '~' and new_tile != '~' and game_state[5]:
            game_state[6] = False
            game_state[7] = False
        if current_tile != '~' and new_tile == '~' and not game_state[5]:
            return False
        if current_tile != '~' and new_tile == '~' and game_state[3]:
            game_state[3] -= 1
            game_state[7] = True
            return True
        if current_tile != '~' and new_tile == '~' and game_state[4]:
            game_state[4] = False
            game_state[6] = True
            return True
        if new_tile == 'a':
            game_state[0] = True
            return True
        if new_tile == 'k':
            game_state[1] = True
            return True
        if new_tile == '$':
            game_state[2] = True
            return True
        if new_tile == 'o':
            game_state[3] += 1
            return True

        if (new_tile == '-' and game_state[1]) or \
           (new_tile == 'T' and game_state[0]) or \
           new_tile in ['O', ' ']:
            return True
        return False

    def _new_directions(self, path):
        if len(path) > 1:
            pre_pos = path[-2]
            pos = path[-1]
            pos_change = (pos[0] - pre_pos[0], pos[1] - pre_pos[1])
            return self.NEW_MOVEMENTS[pos_change]
        else:
            return self.player.DIRECTIONS.values()