'''
IdaStar.py
Contains the IdaStar class which extends the Search class and implements IDA*
Uses pseudocode from: https://en.wikipedia.org/wiki/Iterative_deepening_A*
Written by: Daniel Hocking
zID: 5184128
Date created: 18/05/2018
'''

from Search import Search

class IdaStar(Search):
    # No path can be longer than this
    MAXSTEPS = 25

    def __init__(self, game_map, goals):
        super().__init__(game_map)
        self.goals = goals

    def ida_star(self, cross_divide=False, prev_state=None):
        # cross_divide means going from land -> water or water -> land
        game_state = self._setup_game_state(cross_divide, prev_state)
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
        # num_stones = current_pos[2]
        # have_boat  = current_pos[3]
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