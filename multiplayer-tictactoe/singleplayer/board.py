#
# TIC TAC TOE board.py
# CNT4007 Project by Fareed Fareed-Uddin, Khizer Butt, Kevin Rapkin, Pedro Mantese, Juan Martinez
# version 1 on 3/18/2025 - Kevin Rapkin
#
#
#
#

import pygame
import os

# loads the X and O image files
play_o = pygame.image.load(os.path.join('img', 'o.png'))
play_x = pygame.image.load(os.path.join('img', 'x.png'))

class Board:
    def __init__(self):
        # four lines, two horizontal, two vertical, crossing like a tic tac toe grid
        self.gridlines = [((0, 200), (600, 200)), ((0, 400), (600, 400)), ((200, 0), (200, 600)), ((400, 0), (400, 600))]

        # create 3 x 3 grid matrix with default values 0 for empty space
        self.grid_matrix = [[0 for x in range (3)] for y in range(3)]
        self.switch_user = True
        # search coordinates in cardinal directions from center
        #
        #                      North       NW      West      SW     South    SE     East      NE
        self.search_coords = [(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1)]
        self.gameover = False

    # draw board
    def draw(self, surface):
        for line in self.gridlines:
            # grid line color = black (0,0,0)
            pygame.draw.line(surface, (0, 0, 0), line[0], line[1], 2)
        # place X or O on board based on cell values
        for y in range(len(self.grid_matrix)): 
            for x in range(len(self.grid_matrix[y])):
                if self.get_cell_val(x, y) == "X":
                    surface.blit(play_x, (x * 200, y * 200))
                elif self.get_cell_val(x, y) == "O":
                    surface.blit(play_o, (x * 200, y * 200))
                


    # gets cell value from grid
    def get_cell_val(self, x, y):
        return self.grid_matrix[y][x]
    
    # sets cell value from grid, value = X or O that is played by user, empty space = 0
    def set_cell_val(self, x, y, value):
        self.grid_matrix[y][x] = value

    # based on mouse input location, set that cell value to X or O depending on who is moving
    def get_mouse_input(self, x, y, user):
        # only set cell value if its empty
        if self.get_cell_val(x, y) == 0:
            # allows switch to next user
            self.switch_user = True
            # set to x
            if user == "X":
                self.set_cell_val(x, y, "X")
            # set to o
            elif user == "O":
                self.set_cell_val(x, y, "O")
            self.grid_check(x, y, user)
        # if cell not empty, don't switch between X and O users
        else:
            self.switch_user = False

    # checks if cell is within boundary of playing space, returns true if so
    def boundary_check(self, x, y):
        return x >= 0 and x < 3 and y >= 0 and y < 3
    
    # checks for win condition by counting consecutive X or O
    def grid_check(self, x, y, user):
        # count number of X or O for active user
        count = 1
        # loop to search all spaces outward in counter-clockwise order to check for three X or three O win condition
        for index, (x_coord, y_coord) in enumerate(self.search_coords):
            # first boundary check, if surrounding tile is within playing space boundary, if so check if it's set to the letter X or O of the current user playing their turn
            if self.boundary_check(x + x_coord, y + y_coord) and self.get_cell_val(x + x_coord, y + y_coord) == user:
                # increment counter, now 2 in a row X or O
                count += 1
                # increment coordinates in the direction where letter was found
                xx = x + x_coord
                yy = y + y_coord
                # second boundary check
                if self.boundary_check(xx + x_coord, yy + y_coord) and self.get_cell_val(xx + x_coord, yy + y_coord) == user:
                    count += 1
                    if count == 3:
                        break
                if count < 3:
                    new_direction = 0
                    # sets the new direction to the opposite from the center to check in reverse direction for X or O (ex. North search_coords[0] switches to South search_coords[4])
                    if index == 0:
                        new_direction = self.search_coords[4] # North to South
                    elif index == 1:
                        new_direction = self.search_coords[5] # NW to SE
                    elif index == 2:
                        new_direction = self.search_coords[6] # West to East
                    elif index == 3:
                        new_direction = self.search_coords[7] # SW to NE
                    elif index == 4:
                        new_direction = self.search_coords[0] # South to North
                    elif index == 5:
                        new_direction = self.search_coords[1] # SE to NW
                    elif index == 6:
                        new_direction = self.search_coords[2] # East to West
                    elif index == 7:
                        new_direction = self.search_coords[3] # NE to SW
                    
                    if self.boundary_check(x + new_direction[0], y + new_direction[1]) and self.get_cell_val(x + new_direction[0], y + new_direction[1]) == user:
                        count += 1
                        if count == 3:
                            break
                    else:
                        count = 1
        
        # dispaly winner as count of consecutive X or O is now 3 for the user
        if count == 3:
            print(user, 'is the winner')
            self.gameover = True
        else:
            print('no winner')
            self.gameover = self.board_full()
            
    # clears the board by setting all cell values to 0 
    def clear_board(self):
        for y in range(len(self.grid_matrix)):
            for x in range(len(self.grid_matrix[y])):
                self.set_cell_val(x, y, 0)
                    
                    
    def board_full(self):
        # check for open space in the grid matrix cells
        for row in self.grid_matrix:
            for value in row:
                # still have an open space
                if value == 0:
                    return False
        # board is full, no open spaces
        return True
                



    # prints the board in console
    def print_grid_matrix(self):
        for row in self.grid_matrix:
            print(row)

