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

# Set window parameters
surface = pygame.display.set_mode((600, 600))
pygame.display.set_caption('TIC TACO 2X')

# Define colors
CREAM_BG = (255, 253, 208)
BLACK = (0, 0, 0)
BUTTON_BG = (100, 180, 255)
BUTTON_HOVER = (150, 210, 255)
BUTTON_SHADOW = (70, 130, 200)
BUTTON_TEXT = (255, 255, 255)
WIN_TEXT_X = (255, 100, 100)  # Red for X winner
WIN_TEXT_O = (100, 100, 255)  # Blue for O winner
DRAW_TEXT = (100, 100, 100)   # Gray for draw

# Confetti colors
CONFETTI_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
    (255, 192, 203) # Pink
]

# Font setup
title_font = pygame.font.SysFont('comicsans', 72, bold=True)
button_font = pygame.font.SysFont('comicsans', 48)
win_font = pygame.font.SysFont('comicsans', 64, bold=True)
instruction_font = pygame.font.SysFont('comicsans', 24)

# Helper function to play sound safely
def play_sound(sound):
    if sounds_loaded:
        sound.play()

# Confetti class
class Confetti:
    def __init__(self, x, y, winner):
        self.x = x
        self.y = y
        self.size = random.randint(5, 10)
        self.color = random.choice(CONFETTI_COLORS)
        self.speed_y = random.uniform(1, 5)
        self.speed_x = random.uniform(-2, 2)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.lifetime = 255  # Used for fading out
        
        # Adjust color based on winner
        if winner == "X":
            # Add more red to the color mix
            self.color = (
                min(255, self.color[0] + 50), 
                max(0, self.color[1] - 20), 
                max(0, self.color[2] - 20)
            )
        elif winner == "O":
            # Add more blue to the color mix
            self.color = (
                max(0, self.color[0] - 20), 
                max(0, self.color[1] - 20), 
                min(255, self.color[2] + 50)
            )
    
    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.rotation += self.rotation_speed
        self.lifetime -= 1
        return self.lifetime > 0 and self.y < 600  # Remove if off screen or faded out
    
    def draw(self, surface):
        # Create a rotated rect for the confetti piece
        points = []
        rad = math.radians(self.rotation)
        sin = math.sin(rad)
        cos = math.cos(rad)
        
        # Rectangle corners
        for x_offset, y_offset in [(-0.5, -1), (0.5, -1), (0.5, 1), (-0.5, 1)]:
            x = x_offset * self.size
            y = y_offset * self.size
            
            # Rotate point
            x_rot = x * cos - y * sin
            y_rot = x * sin + y * cos
            
            points.append((self.x + x_rot, self.y + y_rot))
        
        # Draw with fading alpha
        color_with_alpha = (self.color[0], self.color[1], self.color[2], 
                            min(255, self.lifetime))
        
        # Create a surface for this confetti piece
        confetti_surface = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.polygon(confetti_surface, color_with_alpha, 
                           [(p[0]-self.x+self.size, p[1]-self.y+self.size) for p in points])
        
        # Blit to main surface
        surface.blit(confetti_surface, (self.x-self.size, self.y-self.size))


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
    play_button = Button(200, 250, 200, 60, "PLAY", BUTTON_TEXT, BUTTON_BG, BUTTON_HOVER, BUTTON_SHADOW)
    exit_button = Button(200, 350, 200, 60, "EXIT", BUTTON_TEXT, BUTTON_BG, BUTTON_HOVER, BUTTON_SHADOW)
    
    menu_running = True
    while menu_running:
        # Fill background
        surface.fill(CREAM_BG)
        
        # Draw title
        title_text = title_font.render("TIC TACO 2X", True, BLACK)
        title_rect = title_text.get_rect(center=(300, 150))
        surface.blit(title_text, title_rect)
        
        # Draw buttons and check for hover
        play_hover = play_button.draw(surface)
        exit_hover = exit_button.draw(surface)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_hover and event.button == 1:  # Left click on play
                    play_button.check_click(pygame.mouse.get_pos(), True)
                elif exit_hover and event.button == 1:  # Left click on exit
                    exit_button.check_click(pygame.mouse.get_pos(), True)
                    
            if event.type == pygame.MOUSEBUTTONUP:
                if play_button.pressed and play_hover:
                    menu_running = False  # Exit menu loop to start game
                    play_button.pressed = False
                elif exit_button.pressed and exit_hover:
                    pygame.quit()
                    sys.exit()
                
                play_button.pressed = False
                
        pygame.display.flip()

def game():
    board = Board()
    # initialize user as X going first
    user = "X"
    game_running = True
    winner = None
    is_draw = False
    confetti_pieces = []
    clock = pygame.time.Clock()
    show_confetti = False
    move_sound_played = False
    
    # main game loop
    while game_running:
        clock.tick(60)  # Limit to 60 FPS
        
        for event in pygame.event.get():
            # press X to close game
            if event.type == pygame.QUIT:
                return False  # Signal to exit the program
                
            # left click event
            if event.type == pygame.MOUSEBUTTONDOWN and not board.gameover:
                if pygame.mouse.get_pressed()[0]:
                    # mouse click position on board
                    position = pygame.mouse.get_pos()
                    # Store the current board state to detect if a move is made
                    old_board_state = [row[:] for row in board.grid_matrix]
                    
                    # divides position by 200 to separate into 3 x 3 grid matrix on 600 x 600 pixel board with 2 pixel width gridlines
                    board.get_mouse_input(position[0] // 200, position[1] // 200, user)
                    
                    # Check if a move was actually made (board changed)
                    move_made = old_board_state != board.grid_matrix
                    
                    if move_made and not move_sound_played:
                        # Play the appropriate sound for the player
                        if user == "X":
                            play_sound(x_sound)
                        else:
                            play_sound(o_sound)
                        move_sound_played = True
                    
                    # Check if someone won after this move
                    if board.gameover:
                        # If the game is over and the board is not full, it means the current user won
                        if not board.board_full():
                            winner = user
                            show_confetti = True
                            # Play victory sound
                            play_sound(victory_sound)
                            # Create initial confetti burst
                            for _ in range(150):  # Number of confetti pieces
                                confetti_pieces.append(Confetti(random.randint(100, 500), 
                                                               random.randint(0, 200),
                                                               winner))
                        else:
                            is_draw = True
                            # Play draw sound
                            play_sound(draw_sound)
                    
                    # switch user between X and O after each user turn, but only if switch_user = True
                    if board.switch_user:
                        if user == "X":
                            user = "O"
                        else:
                            user = "X"
                    # prints grid after each input in console
                    board.print_grid_matrix()
            
            # Reset move sound flag when mouse button is released
            if event.type == pygame.MOUSEBUTTONUP:
                move_sound_played = False
                    
            # space bar to clear board at gameover or ESC to return to menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and board.gameover:
                    # Play button sound for space bar restart
                    play_sound(button_sound)
                    board.clear_board()
                    board.gameover = False
                    winner = None
                    is_draw = False
                    confetti_pieces = []
                    show_confetti = False
                elif event.key == pygame.K_ESCAPE:
                    # Play button sound for ESC menu return
                    play_sound(button_sound)
                    return True  # Return to menu
                    
        # board background color = cream(255,253,208)
        surface.fill(CREAM_BG)
        board.draw(surface)
        
        # Update and draw confetti if needed
        if show_confetti:
            # Add a few new pieces each frame for continuous effect
            if len(confetti_pieces) < 500 and random.random() < 0.3:  # 30% chance each frame
                for _ in range(5):
                    confetti_pieces.append(Confetti(random.randint(100, 500), 
                                                   random.randint(-50, 0),
                                                   winner))
            
            # Update all pieces
            confetti_pieces = [piece for piece in confetti_pieces if piece.update()]
            
            # Draw all pieces
            for piece in confetti_pieces:
                piece.draw(surface)
        
        # If game is over, show winner message or draw
        if board.gameover:
            # Semi-transparent overlay
            overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))  # White with 150 alpha (semi-transparent)
            surface.blit(overlay, (0, 0))
            
            # Show winner text
            if is_draw:
                result_text = win_font.render("DRAW!", True, DRAW_TEXT)
            else:
                result_text = win_font.render(f"{winner} WINS!", True, WIN_TEXT_X if winner == "X" else WIN_TEXT_O)
                
            result_rect = result_text.get_rect(center=(300, 250))
            surface.blit(result_text, result_rect)
            
            # Instructions
            restart_text = instruction_font.render("Press SPACE to play again or ESC for menu", True, BLACK)
            restart_rect = restart_text.get_rect(center=(300, 350))
            surface.blit(restart_text, restart_rect)
            
        pygame.display.flip()
    
    return True  # Return to menu by default

# Main program loop
running = True
while running:
    main_menu()   # Show the main menu
    running = game()  # Start the game, return to menu if requested

pygame.quit()