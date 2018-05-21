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
        # game_state: axe, key, treasure, stones, raft, cross_divide, on_raft, stone_loc, waste_trees
        current_tile = self.game_map.map[current_pos[1]][current_pos[0]]
        new_tile = self.game_map.map[new_pos[1]][new_pos[0]]
        on_raft = game_state[6]
        stone_locs = list(game_state[7])
        if current_pos in stone_locs:
            current_tile = 'O'
        if new_pos in stone_locs:
            new_tile = 'O'
        if current_tile == '~' and new_tile == '~' and game_state[6]:
            return True
        if current_tile == '~' and new_tile != '~' and not game_state[5]:
            return False
        if current_tile == '~' and new_tile != '~' and game_state[5]:
            game_state[6] = False
        if current_tile != '~' and new_tile == '~' and not game_state[5]:
            return False
        if current_tile != '~' and new_tile == '~' and game_state[3]:
            game_state[3] -= 1
            stone_locs.append(new_pos)
            game_state[7] = tuple(stone_locs)
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
            stone_locs.append(new_pos)
            game_state[7] = tuple(stone_locs)
            return True
        if new_tile == 'T' and game_state[0] and not game_state[4] and not on_raft:
            game_state[4] = True
            return True
        if new_tile == 'T' and game_state[0] and game_state[8]:
            return True

        if (new_tile == '-' and game_state[1]) or \
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

    def _manhattan_distance(self, current_pos, goal):
        x_off = current_pos[0] - goal[0]
        y_off = current_pos[1] - goal[1]
        return abs(x_off) + abs(y_off)

    def _setup_game_state(self, cross_divide, prev_state, waste_trees=False):
        game_state = [self.player.have_axe, self.player.have_key, self.player.have_treasure,
                      self.player.num_stones_held, self.player.have_raft, cross_divide, self.player.on_raft, (), waste_trees]
        if prev_state is not None:
            game_state = list(prev_state)
        #print(f'game_state {game_state}')
        return game_state