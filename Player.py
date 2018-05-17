'''
Player.py
Contains the Player class which is used to store the current status of player
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
                  'W': (-1, 0),}
    
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
        self.num_dynamites_held = 0
        self.num_stones_held = 0

    def player_action(self, action):
        if action == 'f':
            self.move_forwards()
        elif action == 'r':
            self.turn_right()
        elif action == 'l':
            self.turn_left()
        print(self.get_position())

    def get_position(self):
        return (self.x, self.y, self.facing)

    def get_start_position(self):
        return (self.start_x, self.start_y)

    def get_facing(self):
        return self.facing

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
        

    def forward_coords(self):
        print(f'facing {self.facing}')
        return self.x + self.DIRECTIONS[self.facing][0],\
               self.y + self.DIRECTIONS[self.facing][1]
    
    def move_forwards(self):
        new_coords = self.forward_coords()
        self.x = new_coords[0]
        self.y = new_coords[1]

    def _turn_dir(self, change_by = 1):
        directions_keys = list(self.DIRECTIONS.keys())
        direction_index = directions_keys.index(self.facing)
        self.facing = directions_keys[(direction_index + change_by) % 4]

    def turn_right(self):
        self._turn_dir()

    def turn_left(self):
        self._turn_dir(-1)
        
        
        
