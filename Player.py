'''
Player.py
Contains the Player class which is used to store the current status of player
and also some additional helper functions
Written by: Daniel Hocking
zID: 5184128
Date created: 13/05/2018
'''

class Player:

    # Convert a direction into a movement
    # Use a standard x/y axis with origin in top left corner
    # So represent north as a tuple with x of 0 and y of 1
    DIRECTIONS = {'N': (0, -1),
                  'E': (1, 0),
                  'S': (0, 1),
                  'W': (-1, 0)}
    
    def __init__(self):
        # Start location is arbitrary but map has soft limit of 80x80
        # Would rather have positive coords no matter what
        self.start_x = self.x = 100
        self.start_y = self.y = 100
        # Start facing is arbitrary but we consider it to be south
        self.facing = 'S'
        # Start with no items
        self.have_axe = False
        self.have_key = False
        self.have_treasure = False
        self.have_raft = False
        self.on_raft = False
        # Not to be used this year
        #self.num_dynamites_held = 0
        self.num_stones_held = 0

    '''
    This function update the position and facing of the player based on actions taken
    '''
    def player_action(self, action):
        if action == 'f':
            self.move_forwards()
        elif action == 'r':
            self.turn_right()
        elif action == 'l':
            self.turn_left()

    def get_position(self):
        return (self.x, self.y, self.facing)

    def get_start_position(self):
        return (self.start_x, self.start_y)

    def get_facing(self):
        return self.facing

    '''
    Allows for two positions and the current facing to be used to find what
    the number if L or R turns will be needed, along with the new facing
    '''
    def change_facing(self, pos, new_pos, facing):
        pos_dif = (new_pos[0] - pos[0], new_pos[1] - pos[1])
        directions_values = list(self.DIRECTIONS.values())
        new_direction_index = directions_values.index(pos_dif)

        directions_keys = list(self.DIRECTIONS.keys())
        direction_index = directions_keys.index(facing)
        
        new_direction = directions_keys[new_direction_index]
        change = new_direction_index - direction_index
        if not change or abs(change) == 1 or abs(change) == 2:
            return (change, new_direction)
        if abs(change) == 3:
            return (-1 if change > 0 else 1, new_direction)
        

    '''
    The coords of what is directly in front of the player
    '''
    def forward_coords(self):
        return self.x + self.DIRECTIONS[self.facing][0],\
               self.y + self.DIRECTIONS[self.facing][1]

    '''
    Move one step in direction of currently facing
    '''
    def move_forwards(self):
        new_coords = self.forward_coords()
        self.x = new_coords[0]
        self.y = new_coords[1]

    '''
    Change direction by a certain amount from current facing
    '''
    def _turn_dir(self, change_by = 1):
        directions_keys = list(self.DIRECTIONS.keys())
        direction_index = directions_keys.index(self.facing)
        self.facing = directions_keys[(direction_index + change_by) % 4]

    '''
    Helper function to turn right once
    '''
    def turn_right(self):
        self._turn_dir()

    '''
    Helper function to turn left once
    '''
    def turn_left(self):
        self._turn_dir(-1)

    '''
    Called when a tree is chopped down to update player status
    Can chop down a tree on a raft but it won't give an extra raft
    '''
    def chop_down_tree(self):
        if self.on_raft == False:
            self.have_raft = True

    '''
    If the new tile is water then reduce stones if have any, or use raft
    '''
    def move_to_water(self):
        if self.num_stones_held:
            self.num_stones_held -= 1
        else:
            self.have_raft = False
            self.on_raft = True

    '''
    Called when new tile isn't water
    '''
    def move_out_of_water(self):
        self.on_raft = False

    '''
    Called when player moves forward, updates status as needed
    '''
    def move_to_loc(self, tile):
        if tile == '$':
            self.have_treasure = True
        elif tile == 'a':
            self.have_axe = True
        elif tile == 'k':
            self.have_key = True
        elif tile == 'o':
            self.num_stones_held += 1

        if tile == '~':
            self.move_to_water()
        elif tile != '~':
            self.move_out_of_water()
