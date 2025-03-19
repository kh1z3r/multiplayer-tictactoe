#
# TIC TAC TOE client.py
# CNT4007 Project by Fareed Fareed-Uddin, Khizer Butt, Kevin Rapkin, Pedro Mantese, Juan Martinez
# version 1 on 3/18/2025 - Kevin Rapkin
#
#
#
#

import pygame
import socket
import threading
from board import Board

# set window parameters
surface = pygame.display.set_mode((600, 600))
pygame.display.set_caption('TIC TAC TOE')

# create a thread
def create_thread(target):
    thread = threading.Thread(target = target)
    # set it as daemon thread so it's killed automatically when game is closed
    thread.daemon = True
    thread.start()


# host is set to local network by default, and port is chosen to be 12345
HOST = '127.0.0.1'
PORT = 12345

sock = socket.socket()
sock.connect((HOST, PORT))

# receive data from server
def receive_data():
    global turn
    while True:
        # receive byte of data and decode it
        data = sock.recv(1024).decode()
        # splits data after every -
        data = data.split('-')
        x = int(data[0])
        y = int(data[1])
        # check if data received indicates client's turn
        if data[2] == 'yourturn':
            turn = True
        # check if game is over
        if data[3] == 'False':
            board.gameover = True
        if board.get_cell_val(x, y) == 0:
            board.set_cell_val(x, y, 'X')
        # show data receieved in console
        print(data)


create_thread(receive_data)

running = True

board = Board()

# initialize user as X going first
user = "O"

# turn doesn't start on client side, waits for server side to make first move
turn = False 
playing = 'True'

# main loop
while running:

    for event in pygame.event.get():
        # press X to close game
        if event.type == pygame.QUIT:
            running = False

        # left click event
        if event.type == pygame.MOUSEBUTTONDOWN and not board.gameover:
            if pygame.mouse.get_pressed()[0]:
                if turn and not board.gameover:
                    # mouse click position on board
                    position = pygame.mouse.get_pos()
                    cell_X, cell_Y = position[0] // 200, position[1] // 200
                    # divides position by 200 to separate into 3 x 3 grid matrix on 600 x 600 pixel board with 2 pixel width gridlines
                    board.get_mouse_input(cell_X, cell_Y, user)
                    # check if game is over before sending more data
                    if board.gameover:
                        playing = 'False'
                    # prepare cell_X and cell_Y data and encode into byte string to send through TCP connection
                    send_data = '{}-{}-{}-{}'.format(cell_X, cell_Y, 'yourturn', playing).encode()
                    # send data to server
                    sock.send(send_data)
                    turn = False
                
        # space bar to clear board at gameover
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and board.gameover:
                board.clear_board()
                board.gameover = False
                playing = 'True'

    # board background color = cream(255,253,208)
    surface.fill((255, 253, 208))
    board.draw(surface)
    pygame.display.flip()
