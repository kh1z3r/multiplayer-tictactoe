#
# TIC TAC TOE singleplayer.py
# CNT4007 Project by Fareed Fareed-Uddin, Khizer Butt, Kevin Rapkin, Pedro Mantese, Juan Martinez
# version 1 on 3/18/2025 - Kevin Rapkin
#
#
#
#

import pygame
from board import Board

# set window parameters
surface = pygame.display.set_mode((600, 600))
pygame.display.set_caption('TIC TAC TOE')

running = True

board = Board()

# initialize user as X going first
user = "X"

# main loop
while running:

    for event in pygame.event.get():
        # press X to close game
        if event.type == pygame.QUIT:
            running = False

        # left click event
        if event.type == pygame.MOUSEBUTTONDOWN and not board.gameover:
            if pygame.mouse.get_pressed()[0]:
                # mouse click position on board
                position = pygame.mouse.get_pos()
                # divides position by 200 to separate into 3 x 3 grid matrix on 600 x 600 pixel board with 2 pixel width gridlines
                board.get_mouse_input(position[0] // 200, position[1] // 200, user)
                # switch user between X and O after each user turn, but only if switch_user = True
                if board.switch_user: 
                    if user == "X":
                        user = "O"
                    else:
                        user = "X"
                # prints grid after each input in console
                board.print_grid_matrix()
        # space bar to clear board at gameover
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and board.gameover:
                board.clear_board()
                board.gameover = False

    # board background color = cream(255,253,208)
    surface.fill((255, 253, 208))
    board.draw(surface)
    pygame.display.flip()
