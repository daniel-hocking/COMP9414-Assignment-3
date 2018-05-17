'''
Path.py
Contains the Path class which is used to find the optimal path to a goal
Written by: Daniel Hocking
zID: 5184128
Date created: 14/05/2018
'''

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

    def find_path_to_goal(self, goals):
        stime = time()
        ida = IdaStar(self.game_map, goals)
        path, bound = ida.ida_star(True)
        overall_time = time() - stime
        print(f'Time to IDA: {overall_time}')
        if path:
            self.path = path[1::]
            print(f'len {len(path)} {path}')
            self.find_steps()
            print(f'Find steps IDA: {self.steps}')
        return self.has_steps()

    def find_path_to_poi(self, cross_divide):
        stime = time()
        bfs = Bfs(self.game_map)
        path = bfs.find_nearest_poi(cross_divide)
        overall_time = time() - stime
        print(f'Time to BFS: {overall_time}')
        if path:
            self.path = path[1::]
            print(f'BFS path to POI {len(path)}: {path}')
            self.find_steps()
            print(f'Find steps BFS: {self.steps}')
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
            self.path = path[1::]
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
Base class for search, Bfs and IdaStar extend it
'''
class Search:
    def __init__(self, game_map):
        self.game_map = game_map
        self.player = self.game_map.player

    def _valid_move(self, current_pos, new_pos, game_state):
        # game_state: axe, key, treasure, stones, raft, cross_divide
        current_tile = self.game_map.map[current_pos[1]][current_pos[0]]
        new_tile = self.game_map.map[new_pos[1]][new_pos[0]]

        if current_tile == '~' and new_tile == '~':
            return True
        if current_tile == '~' and new_tile != '~' and not game_state[5]:
            return False
        if current_tile != '~' and new_tile == '~' and game_state[3]:
            game_state[3] -= 1
            return True
        if current_tile != '~' and new_tile == '~' and game_state[4]:
            game_state[4] = False
            return True
        if new_tile == 'a':
            game_state[0] = True
            return True
        if new_tile == 'k':
            game_state[1] = True
            return True
        if new_tile == '$':
            game_state[2] = True
            return True
        if new_tile == 'o':
            game_state[3] += 1
            return True

        if (new_tile == '-' and game_state[1]) or \
           (new_tile == 'T' and game_state[0]) or \
           new_tile in ['O', ' ']:
            return True
        return False


'''
Basic implementation of BFS using ideas from 9021 quiz 8 implementation
This is used to find the nearest unexplored area of the map
'''
class Bfs(Search):
    def __init__(self, game_map):
        super().__init__(game_map)

    def _perform_bfs_search(self, goal_coords = None, cross_divide = False, prev_state = None):
        # goal_coords = None means looking for unexplored area
        # Otherwise expects a list of coords to find path to
        # cross_divide means going from land -> water or water -> land
        game_state = [self.player.have_axe, self.player.have_key, self.player.have_treasure, 0, False, cross_divide]
        if cross_divide:
            if prev_state is not None:
                game_state = list(prev_state)
            else:
                game_state[3] = self.player.num_stones_held
                game_state[4] = self.player.have_raft
        queue = deque()
        explored = set()
        pos = self.player.get_position()
        queue.append(([(pos[0], pos[1])], game_state))
        explored.add((pos[0], pos[1]))
        directions = self.player.DIRECTIONS
        found = False
        while len(queue):
            path, game_state = queue.popleft()
            pos = path[-1]
            # Now check each of the four possible directions
            # Add to path if not in explored and a possible move
            for direction in directions:
                dir_mod = directions[direction]
                new_pos = (pos[0] + dir_mod[0], pos[1] + dir_mod[1])
                # If new_pos in goal_coords hopefully have shortest path to a goal
                if goal_coords is not None and new_pos in goal_coords:
                    path.append(new_pos)
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

                    game_state = list(game_state)
                    is_valid = self._valid_move(pos, new_pos, game_state)
                    if is_valid:
                        queue.append((path + [new_pos], game_state))
                        explored.add(new_pos)
                    
            if found:
                break
        return path, game_state if found else None

    def find_nearest_unexplored(self, cross_divide = False):
        path = self._perform_bfs_search(None, cross_divide)
        if path:
            return path[0]
        return None

    def find_nearest_poi(self, cross_divide = False):
        poi_list = self.game_map.find_poi_list()
        print(f'poi_list {poi_list}')
        path =  self._perform_bfs_search(poi_list, cross_divide)
        if path:
            return path[0]
        return None

    def find_chained_goals(self, goals):
        prev_state = None
        overall_path = []
        for goal in goals:
            path = self._perform_bfs_search([goal], True, prev_state)
            if path is None:
                return None
            overall_path = overall_path + path[0][1::]
            prev_state = path[1]
        return overall_path
            
        
        


'''
Implementation of IDA* search
Uses pseudocode from: https://en.wikipedia.org/wiki/Iterative_deepening_A*
Heuristic is the Manhattan distance to goal
'''
class IdaStar(Search):
    # No path can be longer than this
    MAXSTEPS = 25
    
    def __init__(self, game_map, goals):
        super().__init__(game_map)
        self.goals = goals

    def ida_star(self, cross_divide = False):
        # cross_divide means going from land -> water or water -> land
        game_state = [self.player.have_axe, self.player.have_key, self.player.have_treasure, 0, False, cross_divide]
        if cross_divide:
            game_state[3] = self.player.num_stones_held
            game_state[4] = self.player.have_raft
        current_pos = self.player.get_position()
        path = [(current_pos[0], current_pos[1])]
        bound = self._manhattan_distance(current_pos, self._current_goal(path))
        game_states = [game_state]
        while True:
            search_result = self.search(path, game_states, 0, bound)
            if search_result == True:
                return path, bound
            if search_result == self.MAXSTEPS:
                return False, False
            bound = search_result

    def search(self, path, game_states, g, bound):
        current_pos = path[-1]
        game_state = game_states[-1]
        #num_stones = current_pos[2]
        #have_boat  = current_pos[3]
        f = g + self._manhattan_distance(current_pos, self._current_goal(path))
        if f > bound:
            return f
        if self._is_goal(current_pos):
            return True
        minimum = self.MAXSTEPS
        successors = self._successors(current_pos, self._current_goal(path), game_state)
        for successor in successors:
            new_pos = (successor[0], successor[1])
            if new_pos not in path:
                path.append(new_pos)
                game_states.append(successor[2])
                search_result = self.search(path, game_states, g + self._cost(current_pos, successor), bound)
                if search_result == True:
                    return True
                if search_result < minimum:
                    minimum = search_result
                path.pop()
                game_states.pop()
        return minimum

    def _manhattan_distance(self, current_pos, goal):
        x_off = current_pos[0] - goal[0]
        y_off = current_pos[1] - goal[1]
        return abs(x_off) + abs(y_off)

    def _current_goal(self, path):
        for goal in self.goals:
            if goal not in path:
                return goal
        return False
    
    def _is_goal(self, current_pos):
        final_goal = self.goals[-1]
        return current_pos[0] == final_goal[0] and \
               current_pos[1] == final_goal[1]

    def _sucessor(self, current_pos, goal):
        mh = self._manhattan_distance(current_pos, goal)
        return current_pos[0], current_pos[1], mh

    def _successors(self, current_pos, goal, game_state):
        x, y = current_pos[0], current_pos[1]
        successors = []
        # Need to return coords not just manhattan distance
        # then need to sort based on distance
        
        for d in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            changed_state = list(game_state)
            is_valid = self._valid_move(current_pos, (x + d[0], y + d[1]), changed_state)
            if is_valid:
                successor = self._sucessor((x + d[0], y + d[1]), goal)
                successors.append((successor[0], successor[1], changed_state, successor[2]))
                
        return sorted(successors, key=lambda x: x[3])

    def _cost(self, current_pos, successor):
        return 1



    
