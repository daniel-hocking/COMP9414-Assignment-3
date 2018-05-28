'''
GameMap.py
Contains the GameMap class which is used to store the map of the game world
and also some additional helper functions
Written by: Daniel Hocking
zID: 5184128
Date created: 13/05/2018
'''

from collections import defaultdict
import numpy as np
from Bfs import Bfs

class GameMap:

    # Depending on current facing the input data may need to be rotated to match up
    ROTATIONS = {'N': 0, 'E': 3,
                 'S': 2, 'W': 1}
    
    def __init__(self, player):
        # Keep a reference to player object so can access the position
        self.player = player
        # Store game world in a defaultdict as unsure of dimensions
        self.map = defaultdict(lambda: defaultdict(str))
        # Keep track of dimensions explored
        self.max_x = self.max_y = 0
        self.min_x = self.min_y = 200
        # Keep track of hard boundaries
        self.min_bound_x = self.min_bound_y = 0
        self.max_bound_x = self.max_bound_y = 200
        # Keep track of location of gold if it is found
        self.gold_loc = None
        # Keep track of location of POI's
        self.axe_loc = set()
        self.key_loc = set()
        self.door_loc = set()
        self.stone_loc = set()
        self.tree_loc = set()
        # When the map updates other calculations need to be run
        self.map_updated = False

    '''
    Call after every move to keep map up to date
    '''
    def update_map(self, data):
        self.map_updated = False
        # Updates take place relative to the current position of the agent in the word
        position = self.player.get_position()
        self._update_dimensions(position)
        pos_x = position[0] - 2
        pos_y = position[1] - 2
        view = self._rotate_view(data)
        for i in range(5):
            for j in range(5):
                if not (i == 2 and j == 2):
                    self._update_map_loc((pos_x + j, pos_y + i), view[i][j])
                    if view[i][j] == '.':
                        self._update_boundaries((pos_x + j, pos_y + i), j, i)

    '''
    Call after every move to show the current world map based on agents knowledge
    only used in testing
    '''
    def print_map(self):
        for i in range(self.min_y, self.max_y + 1):
            for j in range(self.min_x, self.max_x + 1):
                if self.map[i][j]:
                    print(self.map[i][j], end='')
                else:
                    print('?', end='')
            print()

    '''
    Based on known POI locations find the locations of those that are relevant
    ie. Don't care about axe after already have one
    '''
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
        if not self.player.have_raft and not self.player.on_raft and self.player.have_axe \
           and len(self.tree_loc):
            possible_poi += list(self.tree_loc)
        return possible_poi

    '''
    Order the list of POI so the closest (Manhattan distance) is first, this
    is largely to improve efficiency and not change the ability to find a working
    route in the end
    '''
    def find_nearest_poi(self, pois):
        pos = self.player.get_position()
        ranked_poi = []
        for loc in pois:
            distance = abs(pos[0] - loc[0]) + abs(pos[1] - loc[1])
            ranked_poi.append((loc[0], loc[1], distance))
        return sorted(ranked_poi, key=lambda x: x[2])

    '''
    Some times unexplored area can't be reached directly but can get close enough
    to reveal it, this function checks for that situation
    '''
    def any_unexplored_nearby(self, pos, radius = 0):
        if not radius:
            return self.map[pos[1]][pos[0]] == '' and self._position_in_map_bounds(pos)
        pos_x = pos[0] - radius
        pos_y = pos[1] - radius
        for i in range(1 + (radius * 2)):
            for j in range(1 + (radius * 2)):
                if self.map[pos_y + i][pos_x + j] == '' and self._position_in_map_bounds((pos_x + j, pos_y + i)):
                    return True

    '''
    Update the map and check if anything has actually changed, also update
    the location of known POI
    '''
    def _update_map_loc(self, loc, new_tile):
        # If new tile is different from old one then new information has been
        # gained and old paths may be wrong
        if self.map[loc[1]][loc[0]] != new_tile:
            self.map_updated = True
        self.map[loc[1]][loc[0]] = new_tile
        self._update_poi_loc(loc, new_tile)

    '''
    Add location of POI to the appropriate set, the set data structure prevents
    duplicates automatically in the event that it has already been found
    '''
    def _update_poi_loc(self, loc, item):
        if item == '$':
            self.gold_loc = loc
        elif item == 'a':
            self.axe_loc.add(loc)
        elif item == 'k':
            self.key_loc.add(loc)
        elif item == '-':
            self.door_loc.add(loc)
        elif item == 'o':
            self.stone_loc.add(loc)
        elif item == 'T':
            self.tree_loc.add(loc)

    '''
    Update map status based on actions taken, will also remove POI after
    they have been used
    '''
    def update_map_after_move(self, next_step):
        new_pos = self.player.forward_coords()
        new_tile = self.map[new_pos[1]][new_pos[0]]

        if next_step == 'f':
            self.player.move_to_loc(new_tile)
            if new_tile == '$':
                self.map[new_pos[1]][new_pos[0]] = ' '
            elif new_tile == 'a':
                self.axe_loc.discard((new_pos[0], new_pos[1]))
                self.map[new_pos[1]][new_pos[0]] = ' '
            elif new_tile == 'k':
                self.key_loc.discard((new_pos[0], new_pos[1]))
                self.map[new_pos[1]][new_pos[0]] = ' '
            elif new_tile == 'o':
                self.stone_loc.discard((new_pos[0], new_pos[1]))
                self.map[new_pos[1]][new_pos[0]] = ' '
                        
        elif next_step == 'c' and new_tile == 'T':
            self.player.chop_down_tree()
            self.tree_loc.discard((new_pos[0], new_pos[1]))
            self.map[new_pos[1]][new_pos[0]] = ' '
        elif next_step == 'u' and new_tile == '-':
            self.door_loc.discard((new_pos[0], new_pos[1]))
            self.map[new_pos[1]][new_pos[0]] = ' '

    '''
    Used to track the maximum dimensions of the map that have been explored
    Currently only used when printing the map out
    '''
    def _update_dimensions(self, position):
        self.max_x = max((self.max_x, position[0] + 2))
        self.max_y = max((self.max_y, position[1] + 2))
        self.min_x = min((self.min_x, position[0] - 2))
        self.min_y = min((self.min_y, position[1] - 2))

    '''
    Used to track the boundaries of the map if they have been explored
    '''
    def _update_boundaries(self, position, x_rel, y_rel):
        radius = 2
        if x_rel > radius and (y_rel - radius) == 0:
            self.max_bound_x = min((position[0], self.max_bound_x))
        if x_rel < radius and (y_rel - radius) == 0:
            self.min_bound_x = max((position[0], self.min_bound_x))

        if y_rel > radius and (x_rel - radius) == 0:
            self.max_bound_y = min((position[1], self.max_bound_y))
        if y_rel < radius and (x_rel - radius) == 0:
            self.min_bound_y = max((position[1], self.min_bound_y))

    '''
    Test if a position is within the known boundaries of the map
    '''
    def _position_in_map_bounds(self, position):
        if self.min_bound_x < position[0] < self.max_bound_x and \
                self.min_bound_y < position[1] < self.max_bound_y:
            return True
        return False

    '''
    Rotate view to face north, as the data will come from the server relative
    to the agent's current facing
    '''
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

    '''
    Start by finding locations that are acessible, and then find traversable
    land that isn't part of that region
    '''
    def find_unexplored_regions(self):
        bfs = Bfs(self)
        accessible_region = bfs.perform_bfs_search(get_explored=True)
        inaccessible_region = set()
        for i in range(self.min_y, self.max_y + 1):
            for j in range(self.min_x, self.max_x + 1):
                tile = self.map[i][j]
                pos = (j, i)
                if pos not in accessible_region and pos not in inaccessible_region and \
                        (tile in [' ', 'O', 'o', '$', 'a', 'k'] or
                        (tile == 'T' and self.player.have_axe) or
                        (tile == '-' and self.player.have_key)):
                    region = bfs.perform_bfs_search(pos=pos, get_explored=True)
                    inaccessible_region = inaccessible_region.union(region)
        return accessible_region, inaccessible_region

