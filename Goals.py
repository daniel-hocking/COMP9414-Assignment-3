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
        # Keep a reference to the game_map object
        self.game_map = game_map
        # Keep a reference to the player object
        self.player = game_map.player
        # Create new path object and keep reference to it
        self.path = Path(self.game_map)
        # Flag that allows for pathfinding to cross from land -> water or reverse
        self.cross_divide = False
        # Flag that allows for trees to be cut down when a raft is already held
        self.waste_trees = False
        # Winning path means can reach end goal by following the path
        self.winning_path = False

    '''
    Find the highest priority goal that is currently possible
    '''
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
            # Will try to find a route from current position to gold then back to start
            goals = [gold_loc, self.player.get_start_position()]
            if self.path.find_path_to_goal(goals):
                self.winning_path = True
                return self.path.next_step()
        # If have gold then move towards start
        if self.player.have_treasure:
            if self.path.find_path_to_goal([self.player.get_start_position()]):
                self.winning_path = True
                return self.path.next_step()
        # If there are POI's to go to that would be useful then find path to nearest
        if self.path.find_path_to_poi(self.cross_divide):
            return self.path.next_step()
        # Else explore (move towards an unexplored region)
        if self.path.find_path_to_explore(self.cross_divide, self.waste_trees):
            self.cross_divide = False
            self.waste_trees = False
            return self.path.next_step()

    '''
    If nothing else to explore then see if can reach goal/return
    using raft/stones
    '''
    def allow_cross_divide(self):
        self.cross_divide = True
        return self.find_next_goal()

    '''
    If nothing else to explore then see if can reach goal/return
    by wasting trees and using raft/stones (have raft but cut down anyway)
    '''
    def allow_waste_trees(self):
        self.cross_divide = True
        self.waste_trees = True
        return self.find_next_goal()
