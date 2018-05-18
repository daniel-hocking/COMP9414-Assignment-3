'''
Path.py
Contains the Path class which is used to find the optimal path to a goal
Written by: Daniel Hocking
zID: 5184128
Date created: 14/05/2018
'''

from time import time
from Bfs import Bfs
from AStar import AStar

class Path:
    def __init__(self, game_map):
        self.game_map = game_map
        self.player = game_map.player
        self.path = []
        self.steps = []

    # Determine what the next movement should be to get closer to goal
    def find_next_step(self, goal):
        current_pos = self.player.get_position()
        move_by = self.player.DIRECTIONS[current_pos[2]]
        x_off = current_pos[0] - goal[0]
        x_off_after_move = x_off + move_by[0]
        y_off = current_pos[1] - goal[1]
        y_off_after_move = y_off + move_by[1]


        
        poi_list = self.game_map.find_poi_list()
        wtime_ida = 0
        if len(poi_list):
            poi = poi_list[0]
            stime = time()
            ida = IdaStar(self.game_map, poi)
            path, bound = ida.ida_star()
            overall_time = time() - stime
            wtime_ida = max((wtime_ida, overall_time))
            print(f'Time to IDA: {overall_time} worst: {wtime_ida}')
            if path:
                self.path = path[1::]
                print(f'len {len(path)} {path}')
                self.find_steps()
                print(f'Find steps IDA: {self.steps}')

        wtime_bfs = 0
        stime = time()
        bfs = Bfs(self.game_map)
        path = bfs.find_nearest_unexplored()
        path_poi = bfs.find_nearest_poi()
        overall_time = time() - stime
        wtime_bfs = max((wtime_bfs, overall_time))
        print(f'Time to BFS: {overall_time} worst: {wtime_bfs}')
        if path:
            print(f'BFS path: {path}')
        if path_poi:
            print(f'BFS path to POI {len(path_poi)}: {path_poi}')
        
        if self.game_map.can_move_forwards() and \
           (abs(x_off_after_move) < abs(x_off) or \
           abs(y_off_after_move) < abs(y_off)):
            return 'f'
        # Currently will just turn right if forwards doesnt get closer to goal
        return 'r'

    def find_path_to_goal(self, goals):
        stime = time()
        a_star = AStar(self.game_map)
        path = a_star.find_chained_goals(goals)
        overall_time = time() - stime
        print(f'Time to A*: {overall_time}')
        if path:
            self.path = path
            print(f'len {len(path)} {path}')
            self.find_steps()
            print(f'Find steps A*: {self.steps}')
        return self.has_steps()

    def find_path_to_poi(self, cross_divide):
        stime = time()
        bfs = Bfs(self.game_map)
        path = bfs.find_nearest_poi(cross_divide)
        #a_star = AStar(self.game_map)
        #path = a_star.find_nearest_poi(cross_divide)
        overall_time = time() - stime
        print(f'Time to A*: {overall_time}')
        if path:
            self.path = path[1::]
            print(f'BFS path to POI {len(path)}: {path}')
            self.find_steps()
            print(f'Find steps A*: {self.steps}')
        return self.has_steps()

    def find_path_to_explore(self, cross_divide):
        stime = time()
        bfs = Bfs(self.game_map)
        path = bfs.find_nearest_unexplored(cross_divide)
        overall_time = time() - stime
        print(f'Time to BFS: {overall_time}')
        if path:
            self.path = path[1::]
            print(f'BFS path to unexplored {len(path)}: {path}')
            self.find_steps()
            print(f'Find steps BFS: {self.steps}')
        return self.has_steps()

    def find_path_to_goals(self, goals):
        stime = time()
        bfs = Bfs(self.game_map)
        path = bfs.find_chained_goals(goals)
        overall_time = time() - stime
        print(f'Time to BFS: {overall_time}')
        if path:
            self.path = path
            print(f'BFS path to goals {len(path)}: {path}')
            self.find_steps()
            print(f'Find steps BFS: {self.steps}')
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
                print(f'current_pos {current_pos} new_pos {new_pos}')
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


