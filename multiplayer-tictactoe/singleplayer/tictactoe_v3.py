#
# TIC TAC TOE singleplayer.py
# CNT4007 Project by Fareed Fareed-Uddin, Khizer Butt, Kevin Rapkin, Pedro Mantese, Juan Martinez
# version 1 on 3/18/2025 - Kevin Rapkin (game logic, base multiplayer )
# version 2 on 3/20/2025 - Khizer Butt (UI Changes, Sound vfx, Main menu, Turn Indicator, Player win-loss)
#version 3 on 3/21/2025 - Juan Martinez (best of 3)
#
#


import pygame
from board import Board
import sys
import random
import math
import os

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()  # Initialize the mixer for sound

# global variables
play_x = pygame.image.load(os.path.join('img', 'x.png'))
play_o = pygame.image.load(os.path.join('img', 'o.png'))

# Load sound effects
try:
    button_sound = pygame.mixer.Sound(os.path.join('sounds', 'button click.wav'))
    draw_sound = pygame.mixer.Sound(os.path.join('sounds', 'draw.wav'))
    o_sound = pygame.mixer.Sound(os.path.join('sounds', 'O.wav'))
    victory_sound = pygame.mixer.Sound(os.path.join('sounds', 'victory.wav'))
    x_sound = pygame.mixer.Sound(os.path.join('sounds', 'X.wav'))
    sounds_loaded = True
except:
    print("Warning: Could not load sound files. Continuing without sound.")
    sounds_loaded = False

# Helper function to play sound safely
def play_sound(sound):
    if sounds_loaded:
        sound.play()

# Set window parameters - increased vertical size to accommodate turn indicator
surface = pygame.display.set_mode((600, 650))  # Added 50 pixels for indicator
pygame.display.set_caption('TIC TAC TOE')

# Define colors
CREAM_BG = (255, 253, 208)
BLACK = (0, 0, 0)
BUTTON_BG = (100, 180, 255)
BUTTON_HOVER = (150, 210, 255)
BUTTON_SHADOW = (70, 130, 200)
EXIT_BG = (255, 100, 100)  # Red color for exit button (same as X)
EXIT_HOVER = (255, 150, 150)  # Lighter red for hover
EXIT_SHADOW = (200, 70, 70)  # Darker red for shadow
BUTTON_TEXT = (255, 255, 255)
WIN_TEXT_X = (255, 100, 100)  # Red for X winner
WIN_TEXT_O = (100, 100, 255)  # Blue for O winner
DRAW_TEXT = (100, 100, 100)   # Gray for draw
WINNING_LINE_X = (255, 80, 80, 200)  # Semi-transparent red for X winning line
WINNING_LINE_O = (80, 80, 255, 200)  # Semi-transparent blue for O winning line

# Font setup
title_font = pygame.font.SysFont('comicsans', 72, bold=True)
button_font = pygame.font.SysFont('comicsans', 48)
win_font = pygame.font.SysFont('comicsans', 64, bold=True)
instruction_font = pygame.font.SysFont('comicsans', 24)
turn_font = pygame.font.SysFont('comicsans', 36, bold=True)

# Modified Board class to handle offset, turn display and winning line
class ModifiedBoard(Board):
    def __init__(self):
        super().__init__()
        self.y_offset = 50  # Offset for the board to account for turn indicator
        self.current_player = "X"  # Track current player
        self.winning_cells = []  # Track the winning cells for highlighting
        self.winning_animation = 0  # Animation counter for winning line
    
    def draw(self, surface):
        # Draw background texture - subtle pattern
        for i in range(0, 600, 20):
            for j in range(self.y_offset, 650, 20):
                if (i + j) % 40 == 0:  # Create a checkered pattern
                    pygame.draw.circle(surface, (245, 243, 198), (i, j), 2)  # Slightly darker cream dots
        
        # Draw modified gridlines with offset
        for line in self.gridlines:
            # Adjust y coordinates for offset
            start_x, start_y = line[0]
            end_x, end_y = line[1]
            
            # Apply offset to vertical position
            adjusted_start = (start_x, start_y + self.y_offset)
            adjusted_end = (end_x, end_y + self.y_offset)
            
            # Draw the line
            pygame.draw.line(surface, BLACK, adjusted_start, adjusted_end, 2)
        
        # Draw pieces with offset
        for y in range(len(self.grid_matrix)):
            for x in range(len(self.grid_matrix[y])):
                cell_val = self.get_cell_val(x, y)
                if cell_val == "X" or cell_val == "O":
                    # Check if this cell is part of the winning line
                    is_winning = (x, y) in self.winning_cells
                    
                    if is_winning and self.gameover:
                        # Add pulsing effect to winning pieces
                        scale = 1.0 + 0.05 * math.sin(self.winning_animation * 0.1)
                        img = play_x if cell_val == "X" else play_o
                        scaled_img = pygame.transform.scale(
                            img, 
                            (int(img.get_width() * scale), int(img.get_height() * scale))
                        )
                        # Center the scaled image
                        x_pos = x * 200 - (scaled_img.get_width() - 200) // 2
                        y_pos = y * 200 + self.y_offset - (scaled_img.get_height() - 200) // 2
                        surface.blit(scaled_img, (x_pos, y_pos))
                    else:
                        # Normal draw
                        if cell_val == "X":
                            surface.blit(play_x, (x * 200, y * 200 + self.y_offset))
                        else:  # cell_val == "O"
                            surface.blit(play_o, (x * 200, y * 200 + self.y_offset))
        
        # Draw winning line if there are winning cells
        if self.winning_cells and len(self.winning_cells) == 3 and self.gameover:
            # Update animation counter
            self.winning_animation += 1
            
            # Determine the winning player
            winner = self.get_cell_val(self.winning_cells[0][0], self.winning_cells[0][1])
            
            # Set line color based on winner
            line_color = WINNING_LINE_X if winner == "X" else WINNING_LINE_O
            
            # Calculate line endpoints (center of first and last winning cells)
            start_x, start_y = self.winning_cells[0]
            end_x, end_y = self.winning_cells[2]
            
            # Convert to screen coordinates
            start_pos = (start_x * 200 + 100, start_y * 200 + 100 + self.y_offset)
            end_pos = (end_x * 200 + 100, end_y * 200 + 100 + self.y_offset)
            
            # Create a pulsing line width effect
            line_width = 10 + 5 * math.sin(self.winning_animation * 0.1)
            
            # Draw the winning line
            pygame.draw.line(surface, line_color, start_pos, end_pos, int(line_width))
    
    def get_mouse_input(self, x, y, user):
        # Store old values to detect changes
        old_gameover = self.gameover
        old_state = [row[:] for row in self.grid_matrix]
        
        # Call parent method for standard behavior
        result = super().get_mouse_input(x, y, user)
        
        # Update current player if move was valid and turn switched
        if self.switch_user:
            self.current_player = "O" if user == "X" else "X"
        
        # If game just ended with a win, find the winning line
        if not old_gameover and self.gameover and not self.board_full():
            # Identify the winning line
            self.find_winning_line(x, y, user)
        
        return result
    
    def find_winning_line(self, last_x, last_y, user):
        """Find the winning line based on the last move"""
        self.winning_cells = []
        
        # Check horizonal
        if all(self.get_cell_val(col, last_y) == user for col in range(3)):
            self.winning_cells = [(col, last_y) for col in range(3)]
            return
            
        # Check vertical
        if all(self.get_cell_val(last_x, row) == user for row in range(3)):
            self.winning_cells = [(last_x, row) for row in range(3)]
            return
            
        # Check diagonal from top-left to bottom-right
        if last_x == last_y and all(self.get_cell_val(i, i) == user for i in range(3)):
            self.winning_cells = [(i, i) for i in range(3)]
            return
            
        # Check diagonal from top-right to bottom-left
        if last_x + last_y == 2 and all(self.get_cell_val(i, 2-i) == user for i in range(3)):
            self.winning_cells = [(i, 2-i) for i in range(3)]
            return
    
    def clear_board(self):
        super().clear_board()
        self.winning_cells = []
        self.winning_animation = 0
        self.current_player = "X"

# Button class for 3D effect
class Button:
    def __init__(self, x, y, width, height, text, text_color, bg_color, hover_color, shadow_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.shadow_color = shadow_color
        self.shadow_offset = 5
        self.pressed = False
        self.sound_played = False
        
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = (self.x <= mouse_pos[0] <= self.x + self.width and 
                       self.y <= mouse_pos[1] <= self.y + self.height)
        
        # Draw shadow (3D effect)
        if not self.pressed:
            pygame.draw.rect(surface, self.shadow_color, 
                            (self.x, self.y + self.shadow_offset, 
                             self.width, self.height))
        
        # Draw button
        color = self.hover_color if is_hovering else self.bg_color
        # If pressed, offset button to create "pressed" effect
        button_y = self.y + (self.shadow_offset if self.pressed else 0)
        pygame.draw.rect(surface, color, (self.x, button_y, self.width, self.height))
        
        # Draw text
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(self.x + self.width//2, 
                                               button_y + self.height//2))
        surface.blit(text_surf, text_rect)
        
        return is_hovering
    
    def check_click(self, pos, mouse_pressed):
        if (self.x <= pos[0] <= self.x + self.width and 
            self.y <= pos[1] <= self.y + self.height):
            if mouse_pressed and not self.sound_played:
                play_sound(button_sound)
                self.sound_played = True
            self.pressed = mouse_pressed
            return mouse_pressed
        if not mouse_pressed:
            self.sound_played = False
        return False

def main_menu():
    # Create buttons
    play_button = Button(200, 200, 200, 60, "PLAY", BUTTON_TEXT, BUTTON_BG, BUTTON_HOVER, BUTTON_SHADOW)
    best_of_3_button = Button(150, 280, 300, 60, "BEST OF 3", BUTTON_TEXT, BUTTON_BG, BUTTON_HOVER, BUTTON_SHADOW)
    exit_button = Button(200, 400, 200, 60, "EXIT", BUTTON_TEXT, EXIT_BG, EXIT_HOVER, EXIT_SHADOW)
    
    menu_running = True
    selected_mode = None  # Track what mode the player picks

    while menu_running:
        surface.fill(CREAM_BG)

        # Draw Title
        title_text = title_font.render("TIC TAC TOE", True, BLACK)
        title_rect = title_text.get_rect(center=(300, 120))
        surface.blit(title_text, title_rect)

        # Draw buttons
        play_hover = play_button.draw(surface)
        best3_hover = best_of_3_button.draw(surface)
        exit_hover = exit_button.draw(surface)

        # Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_hover and event.button == 1:
                    play_button.check_click(pygame.mouse.get_pos(), True)
                elif best3_hover and event.button == 1:
                    best_of_3_button.check_click(pygame.mouse.get_pos(), True)
                elif exit_hover and event.button == 1:
                    exit_button.check_click(pygame.mouse.get_pos(), True)

            if event.type == pygame.MOUSEBUTTONUP:
                if play_button.pressed and play_hover:
                    selected_mode = "single"
                    menu_running = False
                elif best_of_3_button.pressed and best3_hover:
                    selected_mode = "best_of_3"
                    menu_running = False
                elif exit_button.pressed and exit_hover:
                    pygame.quit()
                    sys.exit()

                play_button.pressed = False
                best_of_3_button.pressed = False
                exit_button.pressed = False

        pygame.display.flip()

    return selected_mode

def game():
    board = ModifiedBoard()  # Use our modified board class
    user = "X"
    game_running = True
    winner = None
    is_draw = False
    clock = pygame.time.Clock()
    move_sound_played = False
    animation_timer = 0  # Add animation timer

    while game_running:
        clock.tick(60)
        animation_timer += 1  # Increment animation timer
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not board.gameover:
                if pygame.mouse.get_pressed()[0]:
                    position = pygame.mouse.get_pos()
                    old_board_state = [row[:] for row in board.grid_matrix]
                    board.get_mouse_input(position[0] // 200, position[1] // 200, user)
                    move_made = old_board_state != board.grid_matrix
                    if move_made and not move_sound_played:
                        play_sound(x_sound if user == "X" else o_sound)
                        move_sound_played = True

                    if board.gameover:
                        if not board.board_full():
                            winner = user
                            play_sound(victory_sound)
                        else:
                            is_draw = True
                            play_sound(draw_sound)

                    if board.switch_user:
                        user = "O" if user == "X" else "X"
                        board.current_player = user

            if event.type == pygame.MOUSEBUTTONUP:
                move_sound_played = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and board.gameover:
                    play_sound(button_sound)
                    board.clear_board()
                    board.gameover = False
                    winner = None
                    is_draw = False
                    user = "X"
                    board.current_player = "X"
                    animation_timer = 0  # Reset animation timer
                elif event.key == pygame.K_ESCAPE:
                    play_sound(button_sound)
                    return "Exit"

        surface.fill(CREAM_BG)
        
        # Draw turn indicator at the top of screen
        if not board.gameover:
            text = f"{board.current_player}'S TURN"
            text_color = WIN_TEXT_X if board.current_player == "X" else WIN_TEXT_O
            text_surf = turn_font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=(300, 25))
            surface.blit(text_surf, text_rect)
            
            # Draw line under the indicator
            line_color = WIN_TEXT_X if board.current_player == "X" else WIN_TEXT_O
            line_width = 2 + math.sin(animation_timer * 0.1) * 0.5  # Pulsing line width
            pygame.draw.line(surface, line_color, (0, 45), (600, 45), int(line_width))
        
        board.draw(surface)

        # If game is over, show winner message or draw
        if board.gameover:
            # Semi-transparent overlay
            overlay = pygame.Surface((600, 650), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 128))  # Fixed alpha value
            surface.blit(overlay, (0, 0))
            
            # Show winner text
            if is_draw:
                result_text = win_font.render("DRAW!", True, DRAW_TEXT)
            else:
                result_text = win_font.render(f"{winner} WINS!", True, WIN_TEXT_X if winner == "X" else WIN_TEXT_O)
                
            # Add pulsing scale effect to the text
            scale = 1 + math.sin(animation_timer * 0.1) * 0.05
            scaled_text = pygame.transform.scale(result_text, 
                                              (int(result_text.get_width() * scale),
                                               int(result_text.get_height() * scale)))
            result_rect = scaled_text.get_rect(center=(300, 300))
            surface.blit(scaled_text, result_rect)
            
            # Instructions text
            restart_text = instruction_font.render("Press SPACE to play again or ESC for menu", True, BLACK)
            restart_rect = restart_text.get_rect(center=(300, 350))
            surface.blit(restart_text, restart_rect)

        pygame.display.flip()

        # If game over, pause and WAIT for player click or key to move on
        if board.gameover:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                        waiting = False

            # After waiting, return the winner or draw
            if winner:
                return winner
            elif is_draw:
                return "Draw"

    return True  # Return to menu by default

def best_of_three():
    player1_wins = 0
    player2_wins = 0
    rounds_needed = 2
    round_num = 1

    while player1_wins < rounds_needed and player2_wins < rounds_needed:
        print(f"\n--- Round {round_num} ---")
        result = game()

        if result == "Exit":
            return "Exit"

        if result == 'X':
            player1_wins += 1
        elif result == 'O':
            player2_wins += 1

        # Display current score on screen
        surface.fill(CREAM_BG)
        score_text = win_font.render(f"X - {player1_wins} | O - {player2_wins}", True, BLACK)
        score_rect = score_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 50))
        surface.blit(score_text, score_rect)
        pygame.display.update()
        pygame.time.wait(2000)  # Pause to show score

        round_num += 1

    # Final Winner Message
    final_winner = "Player X Wins!" if player1_wins == rounds_needed else "Player O Wins!"
    print("\n🎉", final_winner)

    # Show winner on screen
    surface.fill(CREAM_BG)
    final_text = win_font.render(final_winner, True, WIN_TEXT_X if player1_wins == rounds_needed else WIN_TEXT_O)
    final_rect = final_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(final_text, final_rect)
    pygame.display.update()
    pygame.time.wait(3000)  # Pause to show final winner

# Main program loop
running = True
while running:
    mode = main_menu()  # Show menu and get the selected mode ('single' or 'best_of_3')

    if mode == "single":
        result = game()  # Run one single game
        if result == "Exit":
            running = False

    elif mode == "best_of_3":
        result = best_of_three()  # Run Best of 3 mode
        if result == "Exit":
            running = False

    else:
        running = False  # If player clicks Exit or somehow no mode is chosen

pygame.quit()
