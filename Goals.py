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

    # Find the highest priority goal that is currently possible
    def find_next_goal(self):
        # Start with very simple logic
        if self.path.has_steps():
            return self.path.next_step()
        # If gold in sight then move towards it (unless already have)
        gold_loc = self.game_map.gold_loc
        if gold_loc and not self.player.have_treasure:
            goals = [gold_loc, self.player.get_start_position()]
            if self.path.find_path_to_goals(goals):
                print('gold')
                return None
                return self.path.next_step()
        # If have gold then move towards start
        if self.player.have_treasure:
            if self.path.find_path_to_goals([self.player.get_start_position()]):
                print('start')
                return None
                return self.path.next_step()
        # If there are POI's to go to then find path to nearest
        if self.path.find_path_to_poi(self.cross_divide):
            print('poi')
            return self.path.next_step()
        # Else explore (move towards an unexplored region)
        if self.path.find_path_to_explore(self.cross_divide):
            print('explore')
            self.cross_divide = False
            return self.path.next_step()
        # If nothing else to explore then see if can reach goal/return
        # Using raft/stones
        if not self.cross_divide:
            self.cross_divide = True
            return self.find_next_goal()
        


    
