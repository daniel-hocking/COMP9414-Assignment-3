#!/usr/bin/python3

'''
Agent.py
Contains main function and handles network communication
Written by: Daniel Hocking
zID: 5184128
Date created: 13/05/2018
'''

import sys
import socket
from Player import Player
from GameMap import GameMap
from Goals import Goals

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
#if __name__ == '__main__':
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

#stime = time()
#total_processing = 0
player = Player()
game_map = GameMap(player)
goals = Goals(game_map)
while True:
    data = receive_socket_data(socket)
    if not data:
        #overall_time = time() - stime
        #print(f'Overall time taken: {overall_time} processing time: {total_processing}')
        socket.close()
        sys.exit()
    #mtime = time()
    #print_view(data)
    game_map.update_map(data)
    #game_map.print_map()
    
    #action = get_action()
    action = goals.find_next_goal()
    if not action:
        action = goals.allow_cross_divide()
    if not action:
        action = goals.allow_waste_trees()
    player.player_action(action)
    #move_time = time() - mtime
    #total_processing += move_time
    #print(f'Time to process move: {move_time}')
    socket.send(str.encode(action))
