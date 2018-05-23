'''
Search.py
Contains the Search class which is the base class used to find paths
Bfs and AStar both extend it for some common functionality
Written by: Daniel Hocking
zID: 5184128
Date created: 18/05/2018
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

    '''
    Used to determine if moving from current_pos to new_pos is valid based on
    the current game_state, the game_state is a list containing:
    have_axe, have_key, have_treasure, num_stones_held, have_raft, cross_divide, 
    on_raft, stone_loc, waste_trees, use_stones
    '''
    def _valid_move(self, current_pos, new_pos, game_state):
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
        if current_tile != '~' and new_tile == '~' and \
                (not game_state[5] and not (game_state[3] and game_state[9])):
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

    '''
    Will find what the new positions should be relative to current location
    will try to keep going forward if possible
    '''
    def _new_directions(self, path):
        if len(path) > 1:
            pre_pos = path[-2]
            pos = path[-1]
            pos_change = (pos[0] - pre_pos[0], pos[1] - pre_pos[1])
            return self.NEW_MOVEMENTS[pos_change]
        else:
            return self.player.DIRECTIONS.values()

    '''
    Find the Manhattan distance between current_pos and goal
    '''
    def _manhattan_distance(self, current_pos, goal):
        x_off = current_pos[0] - goal[0]
        y_off = current_pos[1] - goal[1]
        return abs(x_off) + abs(y_off)

    '''
    The game_state will start off with the current player/map state but may
    change based on movements made during the search, this function sets up
    the initial game_state
    '''
    def _setup_game_state(self, cross_divide, prev_state, waste_trees=False, use_stones=False):
        game_state = [self.player.have_axe, self.player.have_key, self.player.have_treasure,
                      self.player.num_stones_held, self.player.have_raft, cross_divide,
                      self.player.on_raft, (), waste_trees, use_stones]
        if prev_state is not None:
            game_state = list(prev_state)
        return game_state