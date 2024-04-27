#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_DGRAM
import threading
import json
import argparse
import time
import math


global clients
global game_state
#list adderss clients
clients = []
#{name_client: {value1: ..., value2: ...}}
game_state = {}

def collision(x, y, width, height, xs, ys, widths, heights):
    if (x + width >= xs) and (xs + widths >= x) and (y + height >= ys) and (ys + heights >= y):
        return True
    return False

def physics(game_state):
    for i in game_state.keys():
        #0[x] 1[y] 2[angle] 3[speed] 4[key_speed] 5[key_angle]
        current_gamer = game_state[i]

        #keyboard gamer
        if current_gamer[0]['key_speed'] == 1:
            current_gamer[1]['speed'] += 0.00001
        elif current_gamer[0]['key_speed'] == -1:
            current_gamer[1]['speed'] -= 0.00008
        if current_gamer[0]['key_angle'] == 1:
            current_gamer[1]['angle'] += 0.00005
        elif current_gamer[0]['key_angle'] == -1:
            current_gamer[1]['angle'] -= 0.00005

        #physics 
        current_gamer[1]['x'] = current_gamer[1]['x'] + (current_gamer[1]['speed']*math.cos(current_gamer[1]['angle']))
        current_gamer[1]['y'] = current_gamer[1]['y'] + (current_gamer[1]['speed']*math.sin(current_gamer[1]['angle']))
        #check collision
        for j in game_state.keys():
            if j == i:
                continue
            if collision(current_gamer[1]['x']-100/2, current_gamer[1]['y']-50/2, 100, 50,
                        game_state[j][1]['x']-100/2, game_state[j][1]['y']-50/2, 100, 50):
                pass
                #print("COLLISION\n*", time.time())

        game_state[i] = current_gamer
    return game_state

#client
def client_send(address, game_state, port):
    s = socket(AF_INET, SOCK_DGRAM)
    msg = (json.dumps(game_state).encode('utf-8'))
    s.sendto(msg,(address, port)) 

def parse_arguments():
    PARSER = argparse.ArgumentParser(
        description="Server genius racer", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    PARSER.add_argument(
        '--server_address', default='localhost', help='server address')
    PARSER.add_argument(
        '--server_port', default=6667, type=int, help='server port')
    PARSER.add_argument(
        '--client_port', default=6668, type=int, help='client port')
    PARSER.add_argument('--version', action='version', version='%(prog)s {0}'.format("1.0"))
    return PARSER.parse_args()

#server
def server_game_state(server_address, server_port):
    global clients
    global game_state
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((server_address, server_port))
    while True:
        #server print message
        msg_server, addr_server = sock.recvfrom(8192)
        client_data_raw = json.loads(msg_server.decode("utf-8"))
        if addr_server[0] not in clients:
            clients.append(addr_server[0])
            client_data = {client_data_raw['name']: [client_data_raw, {"x": 0, "y": 0, "angle": 0, "speed": 0}]}
        else:
            client_data = {client_data_raw['name']: [client_data_raw, game_state[client_data_raw['name']][1]]}
        game_state = {**game_state, **client_data}

def main():
    global clients
    global game_state
    ARGS = parse_arguments()
    client_port = ARGS.client_port
    server_port = ARGS.server_port
    server_address = ARGS.server_address
    thread_server_game_state = threading.Thread(target=server_game_state, args=[server_address, server_port])
    thread_server_game_state.start()
    while True:
        for i in clients:
            game_state = physics(game_state)
            client_send(i, game_state, client_port)
        time.sleep(0.0001)


if __name__ == "__main__":
    main()


