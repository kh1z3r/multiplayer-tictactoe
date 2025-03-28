import pygame
import socket
import json
import threading
import sys
import os
from board import Board
import math
from chat import ChatWindow

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constants
WINDOW_SIZE = (600, 650)
PORT = 5555

# Colors
CREAM_BG = (255, 253, 208)
BLACK = (0, 0, 0)
BUTTON_BG = (100, 180, 255)
BUTTON_HOVER = (150, 210, 255)
BUTTON_SHADOW = (70, 130, 200)
EXIT_BG = (255, 100, 100)
EXIT_HOVER = (255, 150, 150)
EXIT_SHADOW = (200, 70, 70)
BUTTON_TEXT = (255, 255, 255)
WIN_TEXT_X = (255, 100, 100)
WIN_TEXT_O = (100, 100, 255)
DRAW_TEXT = (100, 100, 100)
WINNING_LINE_X = (255, 80, 80, 200)
WINNING_LINE_O = (80, 80, 255, 200)

# Load assets
try:
    play_x = pygame.image.load(os.path.join('img', 'x.png'))
    play_o = pygame.image.load(os.path.join('img', 'o.png'))
    button_sound = pygame.mixer.Sound(os.path.join('sounds', 'button click.wav'))
    draw_sound = pygame.mixer.Sound(os.path.join('sounds', 'draw.wav'))
    o_sound = pygame.mixer.Sound(os.path.join('sounds', 'O.wav'))
    victory_sound = pygame.mixer.Sound(os.path.join('sounds', 'victory.wav'))
    x_sound = pygame.mixer.Sound(os.path.join('sounds', 'X.wav'))
    sounds_loaded = True
except:
    print("Warning: Could not load assets. Continuing without sounds/images.")
    sounds_loaded = False

# Font setup
title_font = pygame.font.SysFont('arial', 72, bold=True)
button_font = pygame.font.SysFont('arial', 48)
win_font = pygame.font.SysFont('arial', 64, bold=True)
instruction_font = pygame.font.SysFont('arial', 24)
turn_font = pygame.font.SysFont('arial', 36, bold=True)

class NetworkGame:
    def __init__(self):
        self.surface = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption('TIC TAC TOE - Multiplayer')
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.board.y_offset = 50
        self.player_symbol = None
        self.current_player = "X"
        self.game_over = False
        self.winner = None
        self.client = None
        self.connected = False
        self.waiting_for_opponent = True
        self.animation_timer = 0
        self.winning_cells = []
        self.game_mode = "single_game"
        self.show_current_score = False
        self.show_final_winner = False
        self.player1_wins = 0
        self.player2_wins = 0
        self.rounds_needed = 2
        
        ######### Chat related properties #########
        self.chat_window = None
        # Chat button removed as chat opens automatically
        self.chat_thread = None
        self.pending_messages = []


    def connect_to_server(self, host):
        """Connect to the game server"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, PORT))
            self.connected = True
            # Start thread to handle server messages
            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    ####### chat related methods #########
    def open_chat_window(self):
        """Open the chat window in a separate thread"""
        if self.chat_window is None:
            self.chat_window = ChatWindow(self.send_chat_message)
            if self.player_symbol:
                self.chat_window.set_player_symbol(self.player_symbol)
            
            # Add any pending messages
            for msg in self.pending_messages:
                self.chat_window.add_message(msg["player"], msg["text"])
            self.pending_messages = []
            
            # Note: ChatWindow already creates its own thread in its __init__ method
            # so we don't need to create another thread here.
    
    def send_chat_message(self, text):
        """Send chat message to server"""
        if self.connected and text:
            try:
                self.client.send(json.dumps({
                    "type": "chat_message",
                    "text": text
                }).encode())
            except Exception as e:
                print(f"Error sending chat message: {e}")
                self.connected = False

    ####### end chat related methods #########

    def receive_messages(self):
        """Handle messages from server"""
        buffer = ""
        while self.connected:
            try:
                chunk = self.client.recv(1024).decode()
                if not chunk:
                    break

                buffer += chunk
                
                # Process all complete messages in the buffer
                while buffer:
                    try:
                        # Find the end of the first JSON object
                        json_end = buffer.find("}")
                        if json_end == -1:
                            # No complete JSON object found, wait for more data
                            break
                            
                        # Extract the complete JSON object (plus closing brace)
                        json_end += 1
                        message = buffer[:json_end]
                        buffer = buffer[json_end:]  # Remove processed message from buffer
                        
                        # Try to parse the JSON
                        data = json.loads(message)
                        
                        # Process the message based on its type
                        if data["type"] == "symbol":
                            self.player_symbol = data["symbol"]
                            # Update chat window if it exists
                            if self.chat_window:
                                self.chat_window.set_player_symbol(self.player_symbol)
                        
                        elif data["type"] == "chat_message":
                            # If chat window exists, add the message
                            if self.chat_window:
                                self.chat_window.add_message(data["player"], data["text"])
                            else:
                                # Store message for when chat window is opened
                                self.pending_messages.append(data)
                        
                        elif data["type"] == "start_game":
                            self.waiting_for_opponent = False
                            self.current_player = data["current_player"]
                            # Automatically open chat window when game starts
                            self.open_chat_window()
                        
                        elif data["type"] == "update_board":
                            x, y = data["position"]
                            player = data["player"]
                            self.board.grid_matrix[y][x] = player
                            if sounds_loaded:
                                sound = x_sound if player == "X" else o_sound
                                sound.play()
                        
                        elif data["type"] == "next_turn":
                            self.current_player = data["player"]
                        
                        elif data["type"] == "update_game_mode":
                            # Update local game mode to match server's
                            self.game_mode = data["game_mode"]
                            print(f"Game mode set to: {self.game_mode}")
                        
                        elif data["type"] == "game_over":
                            self.game_over = True
                            self.winner = data["winner"]
                            if sounds_loaded:
                                if self.winner == "Draw":
                                    draw_sound.play()
                                else:
                                    victory_sound.play()
                        
                        elif data["type"] == "restart_game":
                            self.board.clear_board()
                            self.game_over = False
                            self.winner = None
                            self.current_player = data["current_player"]
                            self.winning_cells = []
                            
                            # If round_num is in the data, update it (for best-of-3 mode)
                            if "round_num" in data:
                                self.round_num = data["round_num"]
                            
                            # Reset any flags that might be active
                            self.show_current_score = False
                            self.show_final_winner = False
                        
                        elif data["type"] == "opponent_disconnected":
                            self.waiting_for_opponent = True
                            self.board.clear_board()
                            self.game_over = False
                            self.winner = None
                        
                        elif data["type"] == "server_full":
                            print("Server is full!")
                            self.connected = False
                            break
        
                        elif data["type"] == "game_of_3_over":
                            self.show_current_score = True
                            self.game_over = True
                            self.winner = data["winner"]
                            if sounds_loaded:
                                if self.winner == "Draw":
                                    draw_sound.play()
                                else:
                                    victory_sound.play()
                            self.round_num = data["round_num"]
                            self.player1_wins = data["player1_wins"]
                            self.player2_wins = data["player2_wins"]
                            # Display a hint to press SPACE to continue to next round
                            print("Press SPACE to continue to the next round")
                            
        
                        elif data["type"] == "restart_game_of_3":
                            self.round_num = data["round_num"]
                            self.player1_wins = data["player1_wins"]
                            self.player2_wins = data["player2_wins"]
                            self.show_final_winner = True
                            self.game_over = True
                            # Do NOT call request_restart() here, we'll wait for user input
                            
                        elif data["type"] == "current_score":
                            # We change current score when drawing the screen
                            self.show_current_score = True
                            
                    except json.JSONDecodeError:
                        # If we can't parse the JSON yet, we might have an incomplete message
                        # Put the processed part back in the buffer and wait for more data
                        break
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        # Continue to the next message
                        continue

            except Exception as e:
                print(f"Connection error: {e}")
                self.connected = False
                break

        print("Connection to server lost")
        self.connected = False

    def send_move(self, x, y):
        """Send move to server"""
        if self.connected and not self.game_over and self.current_player == self.player_symbol:
            try:
                self.client.send(json.dumps({
                    "type": "move",
                    "position": [x, y]
                }).encode())
            except:
                self.connected = False

    def send_game_mode(self):
        """Send game mode to server"""
        if self.connected:
            try:
                self.client.send(json.dumps({
                    "type": "game_mode",
                    "game_mode": self.game_mode}).encode())
            except:
                self.connected = False

    def request_restart(self):
        """Request game restart from server"""
        if self.connected and self.game_over:
            try:
                # Reset local state flags immediately to prevent visual issues
                self.show_final_winner = False
                
                self.client.send(json.dumps({
                    "type": "restart"
                }).encode())
            except:
                self.connected = False
    
    def request_current_score(self):
        """Request current score from server"""
        if self.connected:
            try:
                self.client.send(json.dumps({
                    "type": "current_score"
                }).encode())
            except:
                self.connected = False

    def draw_board(self):
        """Draw the game board and pieces"""
        self.surface.fill(CREAM_BG)
        
        
        # Draw background pattern
        for i in range(0, 600, 20):
            for j in range(self.board.y_offset, 650, 20):
                if (i + j) % 40 == 0:
                    pygame.draw.circle(self.surface, (245, 243, 198), (i, j), 2)

        # Draw grid lines
        for line in self.board.gridlines:
            start_x, start_y = line[0]
            end_x, end_y = line[1]
            adjusted_start = (start_x, start_y + self.board.y_offset)
            adjusted_end = (end_x, end_y + self.board.y_offset)
            pygame.draw.line(self.surface, BLACK, adjusted_start, adjusted_end, 2)

        # Draw pieces
        for y in range(3):
            for x in range(3):
                piece = self.board.grid_matrix[y][x]
                if piece:
                    img = play_x if piece == "X" else play_o
                    self.surface.blit(img, (x * 200, y * 200 + self.board.y_offset))

        # Move the tally display to be above the turn indicator
        if self.game_mode == "best_of_3" and not self.waiting_for_opponent:
            tally_text = instruction_font.render(f"X Wins: {self.player1_wins}  |  O Wins: {self.player2_wins}", True, BLACK)
            tally_rect = tally_text.get_rect(center=(300, 15))
            self.surface.blit(tally_text, tally_rect)

        # Move the turn indicator down slightly
        if not self.game_over and not self.waiting_for_opponent:
            if self.current_player == self.player_symbol:
                text = "YOUR TURN"
            else:
                text = "OPPONENT'S TURN"
            
            text_color = WIN_TEXT_X if self.current_player == "X" else WIN_TEXT_O
            text_surf = turn_font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=(300, 45))  # Moved down from 25 to 45
            self.surface.blit(text_surf, text_rect)
            
            line_color = WIN_TEXT_X if self.current_player == "X" else WIN_TEXT_O
            line_width = 2 + math.sin(self.animation_timer * 0.1) * 0.5
            pygame.draw.line(self.surface, line_color, (0, 65), (600, 65), int(line_width))  # Moved down from 45 to 65

        # Enhanced game over display
        if self.game_over:
            overlay = pygame.Surface((600, 650), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 128))
            self.surface.blit(overlay, (0, 0))
            
            if self.game_mode == "best_of_3":
                # Best of 3 display
                if self.winner == "Draw":
                    result_text = win_font.render("DRAW!", True, DRAW_TEXT)
                else:
                    # Only show "X/O WINS!" if the match isn't over yet
                    if not (self.player1_wins >= self.rounds_needed or self.player2_wins >= self.rounds_needed):
                        result_text = win_font.render(f"{self.winner} WINS!", True, 
                                                    WIN_TEXT_X if self.winner == "X" else WIN_TEXT_O)
                    else:
                        # If match is over, only show "X/O WON THE MATCH!"
                        winner = "X" if self.player1_wins >= self.rounds_needed else "O"
                        result_text = win_font.render(f"{winner} WON THE MATCH!", True, 
                                                    WIN_TEXT_X if winner == "X" else WIN_TEXT_O)
                
                scale = 1 + math.sin(self.animation_timer * 0.1) * 0.05
                scaled_text = pygame.transform.scale(result_text, 
                                                 (int(result_text.get_width() * scale),
                                                 int(result_text.get_height() * scale)))
                result_rect = scaled_text.get_rect(center=(300, 250))
                self.surface.blit(scaled_text, result_rect)
                
                # Different text based on whether the match is over or not
                if self.player1_wins >= self.rounds_needed or self.player2_wins >= self.rounds_needed:
                    # Show score and exit instruction only
                    score_text = instruction_font.render(f"Score: X: {self.player1_wins} - O: {self.player2_wins}", True, BLACK)
                    exit_text = instruction_font.render("Press ESC to exit", True, BLACK)
                    score_rect = score_text.get_rect(center=(300, 350))
                    exit_rect = exit_text.get_rect(center=(300, 390))
                    self.surface.blit(score_text, score_rect)
                    self.surface.blit(exit_text, exit_rect)
                else:
                    # Only show continue text for next round
                    continue_text = instruction_font.render("Press SPACEBAR to continue", True, BLACK)
                    exit_text = instruction_font.render("Press ESC to exit", True, BLACK)
                    continue_rect = continue_text.get_rect(center=(300, 320))
                    exit_rect = exit_text.get_rect(center=(300, 360))
                    self.surface.blit(continue_text, continue_rect)
                    self.surface.blit(exit_text, exit_rect)
            
            else:
                # Single game display
                if self.winner == "Draw":
                    result_text = win_font.render("DRAW!", True, DRAW_TEXT)
                else:
                    result_text = win_font.render(f"{self.winner} WINS!", True, 
                                                WIN_TEXT_X if self.winner == "X" else WIN_TEXT_O)
                
                scale = 1 + math.sin(self.animation_timer * 0.1) * 0.05
                scaled_text = pygame.transform.scale(result_text, 
                                                 (int(result_text.get_width() * scale),
                                                 int(result_text.get_height() * scale)))
                result_rect = scaled_text.get_rect(center=(300, 250))
                self.surface.blit(scaled_text, result_rect)
                
                # Add play again instructions
                continue_text = instruction_font.render("Press SPACEBAR to play again", True, BLACK)
                exit_text = instruction_font.render("Press ESC to exit", True, BLACK)
                continue_rect = continue_text.get_rect(center=(300, 350))
                exit_rect = exit_text.get_rect(center=(300, 390))
                self.surface.blit(continue_text, continue_rect)
                self.surface.blit(exit_text, exit_rect)

        # Draw waiting message with background panel
        if self.waiting_for_opponent:
            # Create solid blue panel
            panel_width = 400
            panel_height = 100
            panel = pygame.Surface((panel_width, panel_height))
            panel.fill(BUTTON_BG)  # Use solid button blue color
            pygame.draw.rect(panel, BUTTON_HOVER, (0, 0, panel_width, panel_height), 3)  # Lighter blue border
            
            # Add subtle shadow
            shadow = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 50), (5, 5, panel_width, panel_height))
            self.surface.blit(shadow, (100, 275))
            
            # Draw panel
            panel_x = 100
            panel_y = 275
            self.surface.blit(panel, (panel_x, panel_y))
            
            # Draw waiting text with pulsing effect centered in panel
            waiting_font = pygame.font.SysFont('comicsans', 40, bold=True)
            alpha = 128 + int(127 * math.sin(self.animation_timer * 0.05))
            waiting_text = waiting_font.render("Waiting for opponent...", True, BUTTON_TEXT)  # Changed to white (BUTTON_TEXT)
            
            # Ensure text fits within panel
            text_width = waiting_text.get_width()
            scale_factor = min(1.0, (panel_width - 40) / text_width)  # Leave 20px padding on each side
            if scale_factor < 1.0:
                waiting_text = pygame.transform.smoothscale(
                    waiting_text,
                    (int(text_width * scale_factor), int(waiting_text.get_height() * scale_factor))
                )
            
            waiting_rect = waiting_text.get_rect()
            waiting_rect.center = (panel_x + panel_width // 2, panel_y + panel_height // 2)
            self.surface.blit(waiting_text, waiting_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.clock.tick(60)
            self.animation_timer += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and not self.waiting_for_opponent:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Regular game click handling
                    if pygame.mouse.get_pressed()[0] and not self.game_over:
                        pos = pygame.mouse.get_pos()
                        x = pos[0] // 200
                        y = (pos[1] - self.board.y_offset) // 200
                        if 0 <= x < 3 and 0 <= y < 3 and not self.board.grid_matrix[y][x]:
                            self.send_move(x, y)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_over:
                        # If we're showing the final winner screen, clear that flag first
                        if self.show_final_winner:
                            self.show_final_winner = False
                        self.request_restart()
                        # Reset local game state to ensure consistency
                        self.show_final_winner = False
                    elif event.key == pygame.K_ESCAPE and self.game_over:
                        running = False

                # when a round in best of 3 is finished, we show the current score
                if self.show_current_score and not self.show_final_winner:
                    # Display current score on screen
                    self.surface.fill(CREAM_BG)
                    score_text = win_font.render(f"X - {self.player1_wins} | O - {self.player2_wins}", True, BLACK)
                    score_rect = score_text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2 - 50))
                    self.surface.blit(score_text, score_rect)
                    pygame.display.update()
                    pygame.time.wait(2000)  # Pause to show score

                    self.show_current_score = False

                # when there is a definite winner in best of 3, we show the final winner
                if self.show_final_winner:
                    final_winner = "Player X Wins!" if self.player1_wins >= self.rounds_needed else "Player O Wins!"

                    # Show winner on screen
                    self.surface.fill(CREAM_BG)
                    final_text = win_font.render(final_winner, True, WIN_TEXT_X if self.player1_wins >= self.rounds_needed else WIN_TEXT_O)
                    final_rect = final_text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2))
                    self.surface.blit(final_text, final_rect)
                    
                    # Add instruction for starting a new Best of 3 game
                    instruction_text = instruction_font.render("Press SPACE to start a new Best of 3 game", True, BLACK)
                    instruction_rect = instruction_text.get_rect(center=(self.surface.get_width() // 2, self.surface.get_height() // 2 + 60))
                    self.surface.blit(instruction_text, instruction_rect)
                    
                    pygame.display.update()
                    # Don't continue with regular game drawing when showing final winner
                    continue  # Add this line to prevents the regular game board from being drawn

            self.draw_board()

            # Only exit the game loop if explicitly disconnected
            if not self.connected and not self.waiting_for_opponent:
                running = False
        
        if self.client:
            # Clean up chat window when client disconnects
            if self.chat_window:
                # Signal the chat window to close
                self.chat_window.running = False
                self.chat_window = None
            self.client.close()

def main():
    """Main program entry point"""
    # Get host from environment variable if set
    host = os.environ.get('TICTACTOE_HOST', 'localhost')
    
    # Get game mode from command line argument if provided
    game_mode = "single_game"
    if len(sys.argv) > 1:
        game_mode = sys.argv[1]
    
    game = NetworkGame()
    if game.connect_to_server(host):
        game.game_mode = game_mode
        game.send_game_mode()
        game.run()
    else:
        print("Failed to connect to server")

if __name__ == "__main__":
    main() 