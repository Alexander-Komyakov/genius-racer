#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_DGRAM
import threading
import json
import time
import random
import string
import argparse
import pygame
import math
import copy


game_state = {}

def get_random_string():
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(10))
    # print random string
    return result_str

def parse_arguments():
    PARSER = argparse.ArgumentParser(
        description="Server genius racer", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    PARSER.add_argument(
        '--server_address', default='localhost', help='server address')
    PARSER.add_argument(
        '--server_port', default=6668, type=int, help='server port')
    PARSER.add_argument(
        '--client_port', default=6667, type=int, help='client port')
    PARSER.add_argument(
        '--client_address', default='localhost', help='client address')
    PARSER.add_argument('--version', action='version', version='%(prog)s {0}'.format("1.0"))
    return PARSER.parse_args()

class Car:
    def __init__(self, name):
        #self.x = 0
        #self.y = 0
        #self.angle = 0
        #self.speed = 0
        self.name = name
        #key_speed -1 back 0 no speed +1 up speed
        self.key_speed = 0
        #key_angle -1 left 0 center +1 right
        self.key_angle = 0
        self.width = 100
        self.height = 50
        self.max_speed = 50
    def get_state(self):
        return {'name': self.name, 'key_speed': self.key_speed, 'key_angle': self.key_angle, 'width': self.width, 'height': self.height, 'max_speed': self.max_speed}

#client
def client_send(my_car, server_address, server_port):
    s = socket(AF_INET, SOCK_DGRAM)
    msg = (json.dumps(my_car).encode('utf-8'))
    s.sendto(msg,(server_address, server_port)) 

#server
def server_game_state(client_address, client_port):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((client_address, client_port))
    global game_state
    while True:
        #server print message
        msg_server, addr_server = sock.recvfrom(8192)
        game_state = json.loads(msg_server.decode("utf-8"))


def main():
    WIDTH, HEIGHT = 1920, 1080
    ARGS = parse_arguments()
    server_address = ARGS.server_address
    server_port =    ARGS.server_port
    client_address = ARGS.client_address
    client_port =    ARGS.client_port
    #get server game state
    global game_state
    thread_server_game_state = threading.Thread(target=server_game_state, args=[client_address, client_port])
    thread_server_game_state.start()
    #create my car
    my_car = Car(get_random_string())

    pygame.init()
    
    # Set up the drawing window
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    
    car_original = pygame.image.load('images/sunboy_car.png')
    #car_rect = car.get_rect(bottomright=(WIDTH, HEIGHT))
    # Run until the user asks to quit
    running = True
    clock = pygame.time.Clock()
    while running:
        clock.tick(60) 
        # Did the user click the window close button?

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    my_car.key_angle = -1
                    #my_car.x -= 3
                elif event.key == pygame.K_d:
                    my_car.key_angle = 1
                elif event.key == pygame.K_w:
                    my_car.key_speed = 1
                elif event.key == pygame.K_s:
                    my_car.key_speed = -1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    my_car.key_angle = 0
                elif event.key == pygame.K_d:
                    my_car.key_angle = 0
                elif event.key == pygame.K_w:
                    my_car.key_speed = 0
                elif event.key == pygame.K_s:
                    my_car.key_speed = 0

        pressed = pygame.key.get_pressed()

        client_send(my_car.get_state(), server_address, server_port)
    
        screen.fill((255, 255, 255))
        # Fill the background with white
        for i in game_state.keys():
            x, y, angle = (game_state[i][1]['x'], game_state[i][1]['y'], game_state[i][1]['angle'])
            width = 100
            height = 50
            #angle_c = angle*(180/math.pi)
            angle_c = math.radians(-angle)
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            x_c = x - (cos_angle*width)-(sin_angle*height)
            y_c = y - (sin_angle*width)+(cos_angle*height)
            car = pygame.transform.rotate(car_original, (-angle*(180/math.pi)))
            #screen.blit(copy.copy(car), car.get_rect(center = (x, y)))
            screen.blit(copy.copy(car), (x, y))
            #draw rectangle
            #print(car.get_rect(center=(x,y)))
            mygr = car.get_rect(center=(x,y))
            #pygame.draw.rect(screen, pygame.Color(255, 0, 0, 0), (mygr[0], mygr[1], mygr[2], mygr[3]))
            pygame.draw.rect(screen, pygame.Color(255, 0, 0, 0), (mygr[0], mygr[1], mygr[2], mygr[3]), 1)
            print("angle: ", angle)
            print("angle_c: ", angle_c)
            print("width: ", angle_c)
            print("height: ", angle_c)
            pygame.draw.rect(screen, pygame.Color(0, 255, 0, 0), (x, y, abs((cos_angle*width)+(sin_angle*height)), abs((sin_angle*width)+(cos_angle*height))), 1)
    
        # Draw a solid blue circle in the center
    
        # Flip the display
        pygame.display.flip()
        time.sleep(0.001)
    
    # Done! Time to quit.
    pygame.quit()

main()
