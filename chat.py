import pygame
import time

class ChatWindow:
    def __init__(self, send_message_callback):
        # Window setup
        self.width = 400
        self.height = 500
        self.surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption('Tic Tac Toe - Chat')
        
        # Colors
        self.bg_color = (240, 240, 240)
        self.text_color = (0, 0, 0)
        self.input_bg = (255, 255, 255)
        self.button_color = (100, 180, 255)
        self.button_hover = (150, 210, 255)
        self.player_colors = {"X": (255, 100, 100), "O": (100, 100, 255)}
        
        # Chat elements
        self.messages = []
        self.input_text = ""
        self.input_active = False
        self.input_rect = pygame.Rect(10, self.height - 50, self.width - 110, 40)
        self.send_button_rect = pygame.Rect(self.width - 90, self.height - 50, 80, 40)
        
        # Fonts
        self.font = pygame.font.SysFont('arial', 16)
        self.input_font = pygame.font.SysFont('arial', 18)
        
        # Function to call when sending a message
        self.send_message_callback = send_message_callback
        
        # Store player symbol
        self.player_symbol = None
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Flag to check if window is still running
        self.running = True
        
    def set_player_symbol(self, symbol):
        self.player_symbol = symbol
        
    def add_message(self, player, text):
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.messages.append({
            "player": player,
            "text": text,
            "timestamp": timestamp
        })
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicked on input box
                if self.input_rect.collidepoint(event.pos):
                    self.input_active = True
                else:
                    self.input_active = False
                    
                # Check if clicked send button
                if self.send_button_rect.collidepoint(event.pos):
                    if self.input_text:
                        self.send_message_callback(self.input_text)
                        self.input_text = ""
                        
            elif event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_RETURN:
                        if self.input_text:
                            self.send_message_callback(self.input_text)
                            self.input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode
                        
            elif event.type == pygame.VIDEORESIZE:
                # Update window size
                self.width, self.height = event.size
                self.surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                # Update input box and send button positions
                self.input_rect = pygame.Rect(10, self.height - 50, self.width - 110, 40)
                self.send_button_rect = pygame.Rect(self.width - 90, self.height - 50, 80, 40)
        
        return True
            
    def draw(self):
        self.surface.fill(self.bg_color)
        
        # Draw message area with scrolling
        message_area_height = self.height - 60
        y_offset = message_area_height - min(message_area_height, len(self.messages) * 25)
        
        # Draw messages
        for i, msg in enumerate(self.messages):
            player_color = self.player_colors.get(msg["player"], self.text_color)
            prefix = f"[{msg['timestamp']}] {msg['player']}: "
            message_text = f"{prefix}{msg['text']}"
            
            # Wrap long messages
            words = message_text.split(' ')
            line = ""
            y_pos = y_offset + i * 25
            
            for word in words:
                test_line = line + word + " "
                text_width, _ = self.font.size(test_line)
                
                if text_width < self.width - 20:
                    line = test_line
                else:
                    text_surface = self.font.render(line, True, player_color)
                    self.surface.blit(text_surface, (10, y_pos))
                    y_pos += 20
                    line = word + " "
            
            if line:
                text_surface = self.font.render(line, True, player_color)
                self.surface.blit(text_surface, (10, y_pos))
        
        # Draw input area
        pygame.draw.rect(self.surface, self.input_bg, self.input_rect)
        pygame.draw.rect(self.surface, self.text_color, self.input_rect, 2)
        
        # Draw input text
        if self.input_text:
            text_surface = self.input_font.render(self.input_text, True, self.text_color)
            self.surface.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 10))
            
        # Draw send button
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.button_hover if self.send_button_rect.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.surface, button_color, self.send_button_rect)
        pygame.draw.rect(self.surface, self.text_color, self.send_button_rect, 2)
        
        # Draw send button text
        send_text = self.font.render("Send", True, (255, 255, 255))
        send_text_rect = send_text.get_rect(center=self.send_button_rect.center)
        self.surface.blit(send_text, send_text_rect)
        
        pygame.display.flip()
        
    def run(self):
        """Run the chat window in its own loop"""
        while self.running:
            self.clock.tick(30)
            self.handle_events()
            self.draw() 