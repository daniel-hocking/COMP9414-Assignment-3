'''
Path.py
Contains the Path class which is used to find the optimal path to a goal
Written by: Daniel Hocking
zID: 5184128
Date created: 14/05/2018
'''

from copy import deepcopy
from collections import deque
from time import time

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

    def find_path_to_goal(self, goal):
        stime = time()
        ida = IdaStar(self.game_map, goal)
        path, bound = ida.ida_star()
        overall_time = time() - stime
        print(f'Time to IDA: {overall_time}')
        if path:
            self.path = path[1::]
            print(f'len {len(path)} {path}')
            self.find_steps()
            print(f'Find steps IDA: {self.steps}')
        return self.has_steps()

    def find_path_to_poi(self):
        stime = time()
        bfs = Bfs(self.game_map)
        path = bfs.find_nearest_poi()
        overall_time = time() - stime
        print(f'Time to BFS: {overall_time}')
        if path:
            self.path = path[1::]
            print(f'BFS path to POI {len(path)}: {path}')
            self.find_steps()
            print(f'Find steps BFS: {self.steps}')
        return self.has_steps()

    def find_path_to_explore(self):
        stime = time()
        bfs = Bfs(self.game_map)
        path = bfs.find_nearest_unexplored()
        overall_time = time() - stime
        print(f'Time to BFS: {overall_time}')
        if path:
            self.path = path[1::]
            print(f'BFS path to unexplored {len(path)}: {path}')
            self.find_steps()
            print(f'Find steps BFS: {self.steps}')
        return self.has_steps()

    def next_step(self):
        if self.has_steps():
            return self.steps.pop(0)
        else:
            return ''

    def has_steps(self):
        return len(self.steps)

    def find_steps(self):
        # Can only create steps if there is a path to follow
        if len(self.path):
            self.steps = []
            current_pos = self.player.get_position()
            current_facing = current_pos[2]

            for new_pos in self.path:
                # Turn if needed
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
                    
                
                
            

'''
Basic implementation of BFS using ideas from 9021 quiz 8 implementation
This is used to find the nearest unexplored area of the map
'''
class Bfs:
    def __init__(self, game_map):
        self.game_map = game_map
        self.player = self.game_map.player

    def _perform_bfs_search(self, goal_coords = None, cross_divide = []):
        # goal_coords = None means looking for unexplored area
        # Otherwise expects a list of coords to find path to
        # cross_divide means going from land -> water or water -> land
        # only if it is possible, will expect a list with number of
        # stones and if have a raft
        queue = deque()
        explored = set()
        pos = self.player.get_position()
        queue.append(([(pos[0], pos[1])], cross_divide))
        explored.add((pos[0], pos[1]))
        directions = self.player.DIRECTIONS
        found = False
        while len(queue):
            path, stone_rafts = queue.popleft()
            stone_rafts = list(stone_rafts)
            pos = path[-1]
            # Now check each of the four possible directions
            # Add to path if not in explored and a possible move
            for direction in directions:
                dir_mod = directions[direction]
                new_pos = (pos[0] + dir_mod[0], pos[1] + dir_mod[1])
                # If new_pos in goal_coords hopefully have shortest path to a goal
                if goal_coords is not None and new_pos in goal_coords:
                    queue.append((path + [new_pos], stone_rafts))
                    found = True
                    break
                # Check if new position is unexplored, this is the goal
                if goal_coords is None and \
                   self.game_map.map[new_pos[1]][new_pos[0]] == '':
                    found = True
                    break
                if new_pos not in explored:
                    cur_cell = self.game_map.map[pos[1]][pos[0]]
                    new_cell = self.game_map.map[new_pos[1]][new_pos[0]]
                    # Allowed to cross land <-> water border
                    if len(stone_rafts):
                        if cur_cell == '~' and new_cell != '~':
                            queue.append((path + [new_pos], stone_rafts))
                            explored.add(new_pos)
                        elif cur_cell != '~' and new_cell == '~' and \
                             (stone_rafts[0] or stone_rafts[1]):
                            if stone_rafts[0]:
                                stone_rafts[0] -= 1
                            else:
                                stone_rafts[1] = False
                            queue.append((path + [new_pos], stone_rafts))
                            explored.add(new_pos)
                    # If current pos on water then we want to stay there
                    if cur_cell == '~' and new_cell == '~':
                        queue.append((path + [new_pos], stone_rafts))
                        explored.add(new_pos)
                    # If current pos not on water then we want to stay out of the water
                    if cur_cell != '~' and new_cell in [' ', 'O']:
                        queue.append((path + [new_pos], stone_rafts))
                        explored.add(new_pos)
            if found:
                break
        return path if found else None

    def find_nearest_unexplored(self):
        return self._perform_bfs_search()

    def find_nearest_poi(self):
        poi_list = self.game_map.find_poi_list()
        print(f'poi_list {poi_list}')
        return self._perform_bfs_search(poi_list)
        
        


'''
Implementation of IDA* search
Uses pseudocode from: https://en.wikipedia.org/wiki/Iterative_deepening_A*
Heuristic is the Manhattan distance to goal
'''
class IdaStar:
    # No path can be longer than this
    MAXSTEPS = 10000
    
    def __init__(self, game_map, goal):
        self.game_map = deepcopy(game_map)
        self.player = self.game_map.player
        self.goal = goal

    def ida_star(self, cross_divide = [0, False]):
        # cross_divide means going from land -> water or water -> land
        # only if it is possible, will expect a list with number of
        # stones and if have a raft
        current_pos = self.player.get_position()
        bound = self._manhattan_distance(current_pos, self.goal)
        path = [(current_pos[0], current_pos[1], cross_divide[0], cross_divide[1])]
        while True:
            search_result = self.search(path, 0, bound)
            if search_result == True:
                return path, bound
            if search_result == self.MAXSTEPS:
                return False, False
            bound = search_result

    def search(self, path, g, bound):
        current_pos = path[-1]
        #num_stones = current_pos[2]
        #have_boat  = current_pos[3]
        f = g + self._manhattan_distance(current_pos, self.goal)
        if f > bound:
            return f
        if self._is_goal(current_pos, self.goal):
            return True
        minimum = self.MAXSTEPS
        successors = self._successors(current_pos, self.goal)
        for successor in successors:
            if successor not in path:
                path.append((successor[0], successor[1], successor[2], successor[3]))
                search_result = self.search(path, g + self._cost(current_pos, successor), bound)
                if search_result == True:
                    return True
                if search_result < minimum:
                    minimum = search_result
                path.pop()
        return minimum
            

    def _manhattan_distance(self, current_pos, goal):
        x_off = current_pos[0] - goal[0]
        y_off = current_pos[1] - goal[1]
        return abs(x_off) + abs(y_off)

    def _is_goal(self, current_pos, goal):
        return current_pos[0] == self.goal[0] and \
               current_pos[1] == self.goal[1]

    def _sucessor(self, current_pos, goal):
        mh = self._manhattan_distance(current_pos, goal)
        return current_pos[0], current_pos[1], mh

    def _valid_move(self, current_pos, new_pos):
        current_tile = self.game_map.map[current_pos[1]][current_pos[0]]
        new_tile = self.game_map.map[new_pos[1]][new_pos[0]]

        if current_tile == '~' and new_tile == '~':
            return current_pos
        if current_tile != '~' and new_tile == '~' and current_pos[2]:
            return (current_pos[0], current_pos[1], current_pos[2] - 1, current_pos[3])
        if current_tile != '~' and new_tile == '~' and current_pos[3]:
            return (current_pos[0], current_pos[1], current_pos[2], False)

        if (new_tile == '-' and self.player.have_key) or \
           (new_tile == 'T' and self.player.have_axe) or \
           new_tile in ['a', 'k', 'o', 'O', '$', ' ']:
            return current_pos
        return False
            

    def _successors(self, current_pos, goal):
        x, y = current_pos[0], current_pos[1]
        successors = []
        # Need to return coords not just manhattan distance
        # then need to sort based on distance
        
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            updated_pos = self._valid_move(current_pos, (x + d[0], y + d[1]))
            if updated_pos:
                successor = self._sucessor((x + d[0], y + d[1]), goal)
                successors.append((successor[0], successor[1], updated_pos[2], updated_pos[3], successor[2]))
                
        return sorted(successors, key=lambda x: x[4])

    def _cost(self, current_pos, successor):
        return 1



    
