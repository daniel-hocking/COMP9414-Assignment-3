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
from time import sleep
from Player import Player
from GameMap import GameMap
from Goals import Goals

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

def get_action():
    while True:
        action = input('Enter Action(s): ')
        action = action.strip().lower()
        for char in action:
            if char in ['f','l','r','c','u','b']:
                return char

def receive_socket_data(socket):
    to_read = 24
    data = bytearray(to_read)
    data_view = memoryview(data)
    while to_read:
        bytes_read = socket.recv_into(data_view, to_read)
        data_view = data_view[bytes_read:]
        to_read -= bytes_read
    return data

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'python {sys.argv[0]} -p <port>')
        sys.exit()
    try:
        port = int(sys.argv[2])
    except:
        print('Invalid port')
        sys.exit
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
            sys.exit()
        print_view(data)
        game_map.update_map(data)
        game_map.print_map()
        
        #action = get_action()
        action = goals.find_next_goal()
        player.player_action(action)
        socket.send(str.encode(action))
        sleep(0.2)
        
    socket.close()

