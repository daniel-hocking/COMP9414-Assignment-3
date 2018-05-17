'''
GameMap.py
Contains the GameMap class which is used to store the map of the game world
Written by: Daniel Hocking
zID: 5184128
Date created: 13/05/2018
'''

from collections import defaultdict
import numpy as np

class GameMap:
    ROTATIONS = {'N': 0, 'E': 3,
                 'S': 2, 'W': 1,}
    
    def __init__(self, player):
        # Keep a reference to player object so can access the position
        self.player = player
        # Store game word in a defaultdict as unsure of dimensions
        self.map = defaultdict(lambda: defaultdict(str))\
        # Keep track of map dimensions
        self.max_x = self.max_y = 0
        self.min_x = self.min_y = 200
        # Keep track of location of gold if it is found
        self.gold_loc = None
        # Keep track of location of POI's
        self.axe_loc = set()
        self.key_loc = set()
        self.door_loc = set()
        self.stone_loc = set()
        self.tree_loc = set()
        

    # Call after every move to keep map up to date
    def update_map(self, data):
        position = self.player.get_position()
        self._update_dimensions(position)
        pos_x = position[0] - 2
        pos_y = position[1] - 2
        view = self._rotate_view(data)
        #print(view)
        for i in range(5):
            for j in range(5):
                if not (i == 2 and j == 2):
                    #print(f'i {i} j {j} : pos_y {pos_y + i} pos_x {pos_x + j} : {view[i][j]}')
                    self.map[pos_y + i][pos_x + j] = view[i][j]
                    self._update_poi_loc(pos_y + i, pos_x + j, view[i][j]) 

    def print_map(self):
        #print(self.min_y, self.max_y)
        #print(self.min_x, self.max_x)
        for i in range(self.min_y, self.max_y + 1):
            for j in range(self.min_x, self.max_x + 1):
                if self.map[i][j]:
                    print(self.map[i][j], end='')
                else:
                    print('?', end='')
            print()

    def can_move_forwards(self, new_coords = None):
        if new_coords is None:
            new_coords = self.player.forward_coords()
        new_pos = self.map[new_coords[1]][new_coords[0]]
        print(f'new_coords {new_coords} new_pos "{new_pos}"')
        if new_pos in ['T', '-', '~', '*', '.', '']:
            return False
        return True

    def find_poi_list(self):
        possible_poi = []
        if not self.player.have_axe and len(self.axe_loc):
            possible_poi += list(self.axe_loc)
        if not self.player.have_key and len(self.key_loc):
            possible_poi += list(self.key_loc)
        if self.player.have_key and len(self.door_loc):
            possible_poi += list(self.door_loc)
        if len(self.stone_loc):
            possible_poi += list(self.stone_loc)
        if not self.player.have_raft and self.player.have_axe \
           and len(self.tree_loc):
            possible_poi += list(self.tree_loc)
        return possible_poi

    def _find_nearest_poi(self, pois):
        pos = self.player.get_position()
        ranked_poi = []
        for loc in pois:
            distance = abs(pos[0] - loc[0]) + abs(pos[1] - loc[1])
            ranked_poi.append((loc[0], loc[1], distance))
        return ranked_poi
        
    
    def _update_poi_loc(self, pos_y, pos_x, item):
        if item == '$':
            self.gold_loc = (pos_x, pos_y)
        elif item == 'a':
            self.axe_loc.add((pos_x, pos_y))
        elif item == 'k':
            self.key_loc.add((pos_x, pos_y))
        elif item == '-':
            self.door_loc.add((pos_x, pos_y))
        elif item == 'o':
            self.stone_loc.add((pos_x, pos_y))
        elif item == 'T':
            self.tree_loc.add((pos_x, pos_y))

    def update_map_after_move(self, next_step):
        pos = self.player.get_position()
        new_pos = self.player.forward_coords()
        
        tile = self.map[pos[1]][pos[0]]
        new_tile = self.map[new_pos[1]][new_pos[0]]

        if next_step == 'f':
            if new_tile == '$':
                self.player.have_treasure = True
                self.map[new_pos[1]][new_pos[0]] = ' '
            elif new_tile == 'a':
                self.player.have_axe = True
                self.axe_loc.discard((new_pos[0], new_pos[1]))
                self.map[new_pos[1]][new_pos[0]] = ' '
            elif new_tile == 'k':
                self.player.have_key = True
                self.key_loc.discard((new_pos[0], new_pos[1]))
                self.map[new_pos[1]][new_pos[0]] = ' '
            elif new_tile == 'o':
                self.player.num_stones_held += 1
                self.stone_loc.discard((new_pos[0], new_pos[1]))
                self.map[new_pos[1]][new_pos[0]] = ' '
            elif tile != '~' and new_tile == '~':
                if self.player.num_stones_held:
                     self.player.num_stones_held -= 1
                else:
                    self.player.have_raft = False
                    self.player.on_raft = True
            elif tile == '~' and new_tile != '~':
                self.player.on_raft = False
                        
        elif next_step == 'c' and new_tile == 'T':
            self.player.have_raft = True
            self.tree_loc.discard((new_pos[0], new_pos[1]))
            self.map[new_pos[1]][new_pos[0]] = ' '
        elif next_step == 'u' and new_tile == '-':
            self.door_loc.discard((new_pos[0], new_pos[1]))
            self.map[new_pos[1]][new_pos[0]] = ' '
            

    def _update_dimensions(self, position):
        self.max_x = max((self.max_x, position[0] + 2))
        self.max_y = max((self.max_y, position[1] + 2))
        self.min_x = min((self.min_x, position[0] - 2))
        self.min_y = min((self.min_y, position[1] - 2))

    # Rotate view to face north
    def _rotate_view(self, data):
        data = data.decode()
        view = []
        str_cnt = 0
        for i in range(5):
            view_row = []
            for j in range(5):
                if not (i == 2 and j == 2):
                    view_row.append(data[str_cnt])
                    str_cnt += 1
                else:
                    view_row.append('')
            view.append(view_row)
        rotate_by = self.ROTATIONS[self.player.get_facing()]
        return np.rot90(np.array(view), k = rotate_by)
        
