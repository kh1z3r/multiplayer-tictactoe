# Tic Tac Toe Game

A Tic Tac Toe game with both multiplayer and singleplayer modes.

## 🎮 Game Modes

### Multiplayer Mode
Network-based multiplayer Tic Tac Toe with the following features:
- Best-of-three match option
- Real-time gameplay over network
- In-game chat system
- Score tracking

### Singleplayer Mode
Local singleplayer mode against AI with adjustable difficulty.

## 🛠️ Setup Instructions

1. Clone this repository
   ```bash
   git clone https://github.com/username/multiplayer-tictactoe.git
   cd multiplayer-tictactoe
   ```

2. Install required packages
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

### Multiplayer Mode
Launch multiplayer mode using:
```bash
python play.py
```

You'll see the following options:
- Option 1: "Start Server & Play" (to host a game)
- Option 2: "Join Game" (to join someone's game)
- Option 3: "Exit"

#### Hosting a Multiplayer Game
1. Select Option 1 from the main menu
2. Choose game mode (single game or best of three)
3. Wait for an opponent to join
4. Your IP address will be displayed for others to connect

#### Joining a Multiplayer Game
1. Select Option 2 from the main menu
2. Enter the host's IP address:
   - Use "localhost" or "127.0.0.1" if playing on the same computer
   - Use the host's IP address if playing over a network

### Singleplayer Mode
Launch singleplayer mode using:
```bash
python singleplayer/tictactoe_v3.py
```

## Controls

| Control | Action |
|---------|--------|
| Mouse | Click to place your mark |
| SPACE | Continue to next round (in best of three) or play again (in single game) |
| ESC | Exit to main menu |


## Network Setup (Multiplayer Only)

If playing multiplayer over the internet:
- Host must ensure port 5555 is open in their firewall/router
- Players must be able to connect to the host's IP address

## Troubleshooting

### Multiplayer Issues
- If server won't start: Check if port 5555 is available
- Connection failed: Verify the host's IP address
- Can't connect: Check firewall settings
- Both players must have the same version of the game

### General Issues
- Make sure all required packages are installed
- Verify Python version compatibility (Python 3.6 or higher recommended)
- Check that all game assets are present in the correct folders

## System Requirements
- Python 3.6 or higher
- Pygame library
- Network connectivity (for multiplayer)

