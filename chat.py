import tkinter as tk
from tkinter import scrolledtext
import threading
import time

class TkChatWindow:
    def __init__(self, send_message_callback):
        # Run Tkinter in its own thread
        self.thread = threading.Thread(target=self.create_window, args=(send_message_callback,))
        self.thread.daemon = True
        self.thread.start()
        
        self.player_symbol = None
        self.queue = []  # Queue for messages to be displayed
        self.window = None  # Will be set in create_window
        self.running = True  # Flag to control window lifetime
        
    def create_window(self, send_message_callback):
        # Create a new window
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe - Chat")
        self.window.geometry("400x500")
        
        # Create chat display area
        self.chat_display = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(expand=True, fill='both', padx=10, pady=(10, 5))
        
        # Create input frame
        input_frame = tk.Frame(self.window)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Create input field
        self.input_text = tk.Entry(input_frame)
        self.input_text.pack(side='left', expand=True, fill='x')
        self.input_text.bind("<Return>", lambda e: self.send_message(send_message_callback))
        
        # Create send button
        send_button = tk.Button(
            input_frame, 
            text="Send", 
            command=lambda: self.send_message(send_message_callback)
        )
        send_button.pack(side='right', padx=(5, 0))
        
        # Set up periodic check for new messages
        self.check_queue()
        
        # Handler for window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Run Tkinter main loop
        while self.running:
            try:
                self.window.update()
                # Small delay to prevent high CPU usage
                time.sleep(0.01)
            except tk.TclError:
                # Window was likely closed
                break
    
    def on_closing(self):
        """Handle window closing event"""
        self.running = False
        if self.window:
            self.window.destroy()
    
    def check_queue(self):
        """Check for new messages in the queue and display them"""
        if self.queue:
            self.chat_display.config(state='normal')
            for msg in self.queue:
                # Format the message
                timestamp = msg['timestamp']
                player = msg['player']
                text = msg['text']
                
                # Set message color based on player
                if player == "X":
                    tag = "player_x"
                    color = "#ff6464"  # Red for X
                elif player == "O":
                    tag = "player_o"
                    color = "#6464ff"  # Blue for O
                else:
                    tag = "system"
                    color = "#646464"  # Gray for system
                    
                self.chat_display.tag_config(tag, foreground=color)
                
                # Insert the message
                self.chat_display.insert(tk.END, f"[{timestamp}] {player}: ", tag)
                self.chat_display.insert(tk.END, f"{text}\n")
                
            self.chat_display.config(state='disabled')
            self.chat_display.see(tk.END)  # Scroll to the bottom
            self.queue = []
            
        # Schedule next check
        if self.window:
            self.window.after(100, self.check_queue)
    
    def send_message(self, callback):
        """Send a message from the input field"""
        text = self.input_text.get().strip()
        if text:
            callback(text)
            self.input_text.delete(0, tk.END)
    
    def add_message(self, player, text):
        """Add a message to the queue"""
        timestamp = time.strftime("%H:%M:%S")
        self.queue.append({
            "player": player,
            "text": text,
            "timestamp": timestamp
        })
    
    def set_player_symbol(self, symbol):
        """Set the player's symbol"""
        self.player_symbol = symbol
        if self.window:
            self.window.title(f"Tic Tac Toe - Chat (Player {symbol})")
    
    def run(self):
        """Placeholder method - window is already running in its own thread"""
        # The window is already running in its own thread when the class is instantiated
        # This method is here for compatibility with the client's call to run()
        pass

# Alias TkChatWindow as ChatWindow for backwards compatibility with client.py
ChatWindow = TkChatWindow 