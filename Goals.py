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
        self.path = Path(self.game_map)
        self.cross_divide = False
        # Winning path means can reach end goal by following the path
        self.winning_path = False

    # Find the highest priority goal that is currently possible
    def find_next_goal(self):
        # If map updated then stop current path as it may be wrong
        if self.game_map.map_updated and not self.winning_path:
            self.path.clear_steps()
        # If have an existing path then continue following it
        if self.path.has_steps():
            return self.path.next_step()
        # If gold in sight then move towards it (unless already have)
        gold_loc = self.game_map.gold_loc
        if gold_loc and not self.player.have_treasure:
            goals = [gold_loc, self.player.get_start_position()]
            if self.path.find_path_to_goal(goals):
                #print('gold')
                self.winning_path = True
                return self.path.next_step()
        # If have gold then move towards start
        if self.player.have_treasure:
            if self.path.find_path_to_goal([self.player.get_start_position()]):
                #print('start')
                self.winning_path = True
                return self.path.next_step()
        # If there are POI's to go to then find path to nearest
        if self.path.find_path_to_poi(self.cross_divide):
            #print('poi')
            return self.path.next_step()
        # Else explore (move towards an unexplored region)
        if self.path.find_path_to_explore(self.cross_divide):
            #print('explore')
            self.cross_divide = False
            return self.path.next_step()

    def allow_cross_divide(self):
        # If nothing else to explore then see if can reach goal/return
        # Using raft/stones
        self.cross_divide = True
        return self.find_next_goal()
        


    
