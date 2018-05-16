'''
Goals.py
Contains the Goals class which is used to keep track of game goals
Written by: Daniel Hocking
zID: 5184128
Date created: 14/05/2018
'''

from Path import Path

class Goals:
    def __init__(self, game_map):
        self.game_map = game_map
        self.player = game_map.player

    # Find the highest priority goal that is currently possible
    def find_next_goal(self):
        # Start with very simple logic
        path = Path(self.game_map)
        # If gold in sight then move towards it (unless already have)
        gold_loc = self.game_map.gold_loc
        if gold_loc and not self.player.have_treasure:
            print('gold')
            return path.find_next_step(gold_loc)
        # If have gold then move towards start
        if self.player.have_treasure:
            print('start')
            return path.find_next_step(self.player.get_start_position())
        # Else explore (move towards an unexplored region)
        # To start will just move forwards if possible, else turn right
        print('explore')
        return path.find_next_step(self.player.forward_coords())
        


    
