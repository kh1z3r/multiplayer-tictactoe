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

class TicTacToeClient:
    def __init__(self, host='127.0.0.1', port=12345):
        # Initialize pygame
        pygame.init()
        self.surface = pygame.display.set_mode((600, 600))
        pygame.display.set_caption('TIC TAC TOE CLIENT')
        
        # Game variables
        self.board = Board()
        self.user = "O"
        self.turn = False
        self.playing = 'True'
        self.running = True
        
        # Network variables
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        
        # Initialize network and start game
        self.connect_to_server()
    
    def connect_to_server(self):
        """Connect to the game server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
            
            # Start receiving data in a separate thread
            self.create_thread(self.receive_data)
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
    
    def create_thread(self, target):
        """Create a daemon thread for a given target function"""
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
    
    def receive_data(self):
        """Receive and process data from the server"""
        while self.connected:
            try:
                # Receive and parse data
                data = self.sock.recv(1024).decode()
                if not data:
                    break
                    
                data_parts = data.split('-')
                x = int(data_parts[0])
                y = int(data_parts[1])
                
                # Update game state based on received data
                if data_parts[2] == 'yourturn':
                    self.turn = True
                    
                if data_parts[3] == 'False':
                    self.board.gameover = True
                    
                if self.board.get_cell_val(x, y) == 0:
                    self.board.set_cell_val(x, y, 'X')
                    
                print(f"Received move: {data_parts}")
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.connected = False
                break
    
    def send_move(self, x, y):
        """Send a move to the server"""
        try:
            if self.connected:
                playing_status = 'False' if self.board.gameover else 'True'
                send_data = f'{x}-{y}-yourturn-{playing_status}'.encode()
                self.sock.send(send_data)
        except Exception as e:
            print(f"Error sending data: {e}")
            self.connected = False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            # Handle window close
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if self.turn and not self.board.gameover:
                        # Get and process the move
                        position = pygame.mouse.get_pos()
                        cell_x, cell_y = position[0] // 200, position[1] // 200
                        
                        # Update board and check for game over
                        self.board.get_mouse_input(cell_x, cell_y, self.user)
                        if self.board.gameover:
                            self.playing = 'False'
                            
                        # Send move to server
                        self.send_move(cell_x, cell_y)
                        self.turn = False
            
            # Handle keyboard input
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.board.gameover:
                    self.board.clear_board()
                    self.board.gameover = False
                    self.playing = 'True'
    
    def update_display(self):
        """Update the game display"""
        # Clear screen with cream background
        self.surface.fill((255, 253, 208))
        
        # Draw board
        self.board.draw(self.surface)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update_display()
        
        # Clean up resources when the game ends
        if self.sock:
            self.sock.close()
        pygame.quit()

# Entry point
if __name__ == "__main__":
    client = TicTacToeClient()
    client.run()
