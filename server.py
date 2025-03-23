import socket
import threading
import json
import sys

class TicTacToeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.clients = []
        self.addresses = []
        self.current_player = "X"
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.game_mode = "single_game"  # default game mode
        # for best of 3 game mode variables
        self.player1_wins = 0
        self.player2_wins = 0
        self.rounds_needed = 2
        self.round_num = 1
        self.game_over = False
        print(f"Server started on {host}:{port}")
        print(f"Your IP address is: {socket.gethostbyname(socket.gethostname())}")

    def broadcast(self, message):
        """Send message to all connected clients"""
        for client in self.clients:
            try:
                client.send(json.dumps(message).encode())
            except:
                self.remove_client(client)

    def handle_client(self, client, address):
        """Handle individual client connection"""
        # Assign player symbol (X or O)
        player = "X" if len(self.clients) == 1 else "O"
        client.send(json.dumps({"type": "symbol", "symbol": player}).encode())

        # If we have two players, start the game
        if len(self.clients) == 2:
            self.broadcast({"type": "start_game", "current_player": self.current_player})

        # this condition is always true unless we are in best of 3 game mode and it is over
        while True:
            try:
                message = client.recv(1024).decode()
                if not message:
                    break

                data = json.loads(message)
                if data["type"] == "move":
                    if self.current_player == player:
                        x, y = data["position"]
                        if self.is_valid_move(x, y):
                            self.board[y][x] = player
                            self.broadcast({
                                "type": "update_board",
                                "board": self.board,
                                "position": [x, y],
                                "player": player
                            })

                            if self.check_winner(player):
                                # checks game mode
                                if self.game_mode == "single_game":
                                    self.broadcast({
                                        "type": "game_over",
                                        "winner": player
                                    })
                                elif self.game_mode == "best_of_3":
                                    if player == "X":
                                        self.player1_wins += 1
                                        print(f"Player X won round {self.round_num}, total wins: {self.player1_wins}")
                                    elif player == "O":
                                        self.player2_wins += 1
                                        print(f"Player O won round {self.round_num}, total wins: {self.player2_wins}")
                                    self.broadcast({
                                        "type": "game_of_3_over",
                                        "winner": player,
                                        "round_num": self.round_num,
                                        "player1_wins": self.player1_wins,
                                        "player2_wins": self.player2_wins,
                                    })
                                self.game_over = True
                                
                            elif self.is_board_full():
                                self.broadcast({
                                    "type": "game_over",
                                    "winner": "Draw"
                                })
                                self.game_over = True
                            else:
                                self.current_player = "O" if self.current_player == "X" else "X"
                                self.broadcast({
                                    "type": "next_turn",
                                    "player": self.current_player
                                })

                elif data["type"] == "restart":
                    self.board = [['' for _ in range(3)] for _ in range(3)]
                    self.current_player = "X"
                    self.game_over = False
                    
                    if self.game_mode == "best_of_3":
                        # Only increment round number when restarting in best-of-3 mode
                        # and when the game is not over (player1_wins or player2_wins < rounds_needed)
                        if self.player1_wins < self.rounds_needed and self.player2_wins < self.rounds_needed:
                            self.round_num += 1
                            print(f"Starting round {self.round_num} of best-of-3")
                        else:
                            # Reset for a new best-of-3 game if someone has already won
                            self.reset_best_of_3()
                            print(f"Starting a new best-of-3 game")
                    
                    self.broadcast({
                        "type": "restart_game",
                        "current_player": self.current_player,
                        "round_num": self.round_num  # Send round number to clients
                    })

                # this will only happen if the game mode is best of 3
                elif data["type"] == "current_score":
                    self.broadcast({
                        "type": "current_score",
                        "player1_wins": self.player1_wins,
                        "player2_wins": self.player2_wins,
                        "round_num": self.round_num
                    })

                # Handle game mode selection from client
                elif data["type"] == "game_mode":
                    self.game_mode = data["game_mode"]
                    print(f"Game mode set to: {self.game_mode}")

                # if someone wins the best of 3 game, we send a message to show the winner and let them decide to do another game or not
                if self.player1_wins >= self.rounds_needed or self.player2_wins >= self.rounds_needed:
                    final_winner = "X" if self.player1_wins >= self.rounds_needed else "O"
                    print(f"Player {final_winner} has won the best-of-3 match!")
                    
                    self.broadcast({
                        "type": "restart_game_of_3",
                        "round_num": self.round_num,
                        "player1_wins": self.player1_wins,
                        "player2_wins": self.player2_wins,
                    })
                    
                    # Reset for the next best-of-3 game
                    self.reset_best_of_3()
                    self.game_over = True
            except:
                break
        

        self.remove_client(client)

    def remove_client(self, client):
        """Remove client and clean up"""
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            self.addresses.pop(index)
            client.close()
            if len(self.clients) < 2:
                self.board = [['' for _ in range(3)] for _ in range(3)]
                self.current_player = "X"
                self.game_over = False
                if self.clients:
                    self.clients[0].send(json.dumps({"type": "opponent_disconnected"}).encode())

    def is_valid_move(self, x, y):
        """Check if move is valid"""
        return 0 <= x < 3 and 0 <= y < 3 and self.board[y][x] == ''

    def check_winner(self, player):
        """Check if current player has won"""
        # Check rows
        for row in self.board:
            if all(cell == player for cell in row):
                return True

        # Check columns
        for col in range(3):
            if all(self.board[row][col] == player for row in range(3)):
                return True

        # Check diagonals
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2-i] == player for i in range(3)):
            return True

        return False

    def is_board_full(self):
        """Check if board is full (draw)"""
        return all(cell != '' for row in self.board for cell in row)

    def start(self):
        """Start the server and accept connections"""
        while True:
            client, address = self.server.accept()
            if len(self.clients) < 2:
                print(f"Connection from {address}")
                self.clients.append(client)
                self.addresses.append(address)
                thread = threading.Thread(target=self.handle_client, args=(client, address))
                thread.daemon = True
                thread.start()
            else:
                client.send(json.dumps({"type": "server_full"}).encode())
                client.close()

    def reset_best_of_3(self):
        """Reset the best-of-3 game state"""
        self.player1_wins = 0
        self.player2_wins = 0
        self.round_num = 1
        print("Best-of-3 game has been reset")

if __name__ == "__main__":
    try:
        server = TicTacToeServer()
        server.start()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 