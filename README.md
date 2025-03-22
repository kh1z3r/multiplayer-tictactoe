# Multiplayer Tic Tac Toe

A networked multiplayer Tic Tac Toe game with social features including friend management, messaging, and lobby creation.

## Features
- Multiplayer Tic Tac Toe gameplay
- Best-of-three and best-of-five match options
- Friend system (add, remove, search)
- Direct messaging between friends
- Game lobby creation and management

## Team Members
- Person A: Network Infrastructure
- Person B: Game Logic & Mechanics - Kevin & Fareed
- Person C: User Interface - Khizer
- Person D: Friend System
- Person E: Messaging & Lobby System

## Setup Instructions
1. Clone this repository
2. Install required packages: `pip install -r requirements.txt`
3. Run the server: `python server.py`
4. Run the client: `python client.py`

## How to Play

### Starting a Game
1. Launch the game using `python play.py`
2. Choose one of the following options:
   - Option 1: "Start Server & Play" (to host a game)
   - Option 2: "Join Game" (to join someone's game)
   - Option 3: "Exit"

### Hosting a Game
1. Select Option 1 from the main menu
2. The server will start automatically
3. Wait for an opponent to join your game
4. Your IP address will be displayed for others to connect

### Joining a Game
1. Select Option 2 from the main menu
2. Enter the host's IP address
   - Use "localhost" or "127.0.0.1" if playing on the same computer
   - Use the host's IP address if playing over a network


### Controls
- Mouse: Click to place your mark or select menu options
- SPACE: Start new round after a game ends
- ESC: Return to main menu


## Troubleshooting
- If the server doesn't start, check if the port 5555 is available
- If you can't connect, ensure the host's IP address is correct
- Check your firewall settings if playing over a network
- Ensure both players have the same version of the game
