#!/usr/bin/python3

'''
agent.py
Contains main function and handles network communication
Written by: Daniel Hocking
zID: 5184128
Date created: 13/05/2018

Basic structure:
- agent.py: contains the main function and network communications code, initialise
    instances of the other classes used to solve the game and run a loop to
    continually find steps until a solution has been found
- Player.py: contains the Player class which is used to store the current status
    of player and also some additional helper functions
- GameMap.py: contains the GameMape class which is used to store the map of the game
    world and also some additional helper functions
- Goals.py: contains the Goals class which is used to keep track of game goals
- Path.py: contains the Path class which is used to find the optimal path to a goal
- Search.py: contains the Search class which is the base class used to find paths
- Bfs.py: contains the Bfs class which extends the Search class and implements BFS
- AStar.py: contains the AStar class which extends the Search class and implements A*

Description:
The basic control loop of the program is as follows:
- Receive 24 bytes from the server indicating the current agent view
- Update the internal representation of the map using this new information
    Map is stored using a defaultdict datastructure which allows for an arbitrarily
    sized array and initialises the default value to an empty string, the starting
    location is set to be 100, 100 as this prevents negative/zero coordinates, which
    may cause issues in certain circumstances
- Keep track of if the map actually changes from what was previously known as
this will mean that current paths may need to change
- Keep track of known POI locations (items like key, axe, trees etc.) so that they
can quickly be located and ranked when they are needed
    Uses a set to store each type of POI so that each one will only be stored once
    and has very fast access to elements stored in the set
- Will now try to look for the next goal to get closer to a winning state
- There may be an ongoing path that can simply be continued as long as the map
hasn't been updated
- The top priority goal is to look for a path to obtain the treasure and return
to the start, so it will first try to create a valid path for this
    To do this A* search is carried out using the Manhattan distance for the
    heuristic, it performs the search twice first starting from the current
    position with the current game state and with the treasure as the goal
    state, and then a second search starts using that new location and state
    to find a path back to the start, further implementation details can be
    found in the Astar.py file
- The second priority goal is when the treasure has already been obtained then
try to find a path back to the start, this would usually not happen as a full
path to get the treasure and return would have already been plotted, but this
is a simple extra case just in case something happened to the existing path
    It also uses the same style of A* seach but with only one goal


'''

import sys
import socket
from Player import Player
from GameMap import GameMap
from Goals import Goals
from time import sleep

'''
Takes the 24 bytes received by the server and prints them in human-readable 
format, only used in testing
'''
def print_view(data):
    data = data.decode()
    str_cnt = 0

    print('+-----+')
    for i in range(5):
        print('|', end='')
        for j in range(5):
            if not (i == 2 and j == 2):
                print(data[str_cnt], end='')
                str_cnt += 1
            else:
                print('^', end='')
        print('|')
    print('+-----+')

'''
Allows for keyboard input of an action to take, only used in testing
'''
def get_action():
    while True:
        action = input('Enter Action(s): ')
        action = action.strip().lower()
        for char in action:
            if char in ['f','l','r','c','u','b']:
                return char

'''
Reads next 24 bytes sent by the server into a variable and then returns
'''
def receive_socket_data(socket):
    to_read = 24
    data = bytearray(to_read)
    data_view = memoryview(data)
    while to_read:
        try:
            bytes_read = socket.recv_into(data_view, to_read)
        except ConnectionResetError:
            return None
        data_view = data_view[bytes_read:]
        to_read -= bytes_read
    return data

'''
The main function is where program execution begins:
- Get the command line input or exit if not found
- Open socket connection to server or exit if fails
- Initialise the Player, GameMap and Goals objects used to track game 
state and find goals
- Receive data and issue actions until the game is solved or lost
- After receive data update map, and find what the next move should be
using goal/pathfinding logic
'''
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'python {sys.argv[0]} -p <port>')
        sys.exit()
    try:
        port = int(sys.argv[2])
    except:
        print('Invalid port')
        sys.exit()
    if not 1025 <= port <= 65535:
        print('Invalid port')
        sys.exit()

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket.connect(('localhost', port))
    except ConnectionRefusedError:
         print('Connection refused, check host is running')
         sys.exit()

    player = Player()
    game_map = GameMap(player)
    goals = Goals(game_map)
    while True:
        data = receive_socket_data(socket)
        if not data:
            socket.close()
            sys.exit()
        #print_view(data)
        game_map.update_map(data)
        game_map.print_map()

        #action = get_action()
        action = goals.find_next_goal()
        if not action:
            action = goals.extended_searches()
        player.player_action(action)

        socket.send(str.encode(action))
        #sleep(0.1)
