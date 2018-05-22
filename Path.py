'''
Path.py
Contains the Path class which is used to find the optimal path to a goal
Or at least a possible path
Written by: Daniel Hocking
zID: 5184128
Date created: 14/05/2018
'''

from Bfs import Bfs
from AStar import AStar

class Path:

    def __init__(self, game_map):
        # Keep a reference to the game_map object
        self.game_map = game_map
        # Keep a reference to the player object
        self.player = game_map.player
        # Used to store the path as a set of coords
        self.path = []
        # Used to store the steps required to follow path
        self.steps = []

    def find_path_to_goal(self, goals):
        a_star = AStar(self.game_map)
        path = a_star.find_chained_goals(goals)
        if path:
            self.path = path
            self.find_steps()
        return self.has_steps()

    def find_path_to_poi(self, cross_divide):
        a_star = AStar(self.game_map)
        path = a_star.find_nearest_poi(cross_divide)
        if path:
            self.path = path
            self.find_steps()
        return self.has_steps()

    def find_path_to_explore(self, cross_divide, waste_trees):
        bfs = Bfs(self.game_map)
        path = bfs.find_nearest_unexplored(cross_divide, waste_trees)
        if path:
            self.path = path[1::]
            self.find_steps()
        return self.has_steps()

    def next_step(self):
        if self.has_steps():
            next_step = self.steps.pop(0)
            self.game_map.update_map_after_move(next_step)
            return next_step
        else:
            return ''

    def has_steps(self):
        return len(self.steps)

    def clear_steps(self):
        self.path = []
        self.steps = []

    def find_steps(self):
        # Can only create steps if there is a path to follow
        if len(self.path):
            self.steps = []
            current_pos = self.player.get_position()
            current_facing = current_pos[2]

            for new_pos in self.path:
                # Turn if needed
                #print(f'current_pos {current_pos} new_pos {new_pos}')
                change_facing = self.player.change_facing(current_pos, new_pos, current_facing)
                if change_facing[0] != 0:
                    current_facing = change_facing[1]
                    turn_dir = 'l' if change_facing[0] < 0 else 'r'
                    for _ in range(abs(change_facing[0])):
                        self.steps.append(turn_dir)
                # Determine what is in front of agent
                new_tile = self.game_map.map[new_pos[1]][new_pos[0]]
                # Use tool if needed
                if new_tile == '-':
                    if self.player.have_key:
                        self.steps.append('u')
                    else:
                        break
                if new_tile == 'T':
                    if self.player.have_axe:
                        self.steps.append('c')
                    else:
                        break
                # Move forward if possible
                current_tile = self.game_map.map[current_pos[1]][current_pos[0]]
                if new_tile in ['*', '.', '']:
                    break
                self.steps.append('f')
                current_pos = new_pos


