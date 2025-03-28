import sys
import subprocess
import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("""
╔════════════════════════════════════════╗
║          TIC TAC TOE LAUNCHER          ║
╚════════════════════════════════════════╝
""")

def run_server():
    """Run the server script"""
    try:
        subprocess.Popen([sys.executable, "server.py"])
        return True
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def run_client(game_mode="single_game"):
    """Run the client script with specified game mode"""
    try:
        subprocess.run([sys.executable, "client.py", game_mode])
    except Exception as e:
        print(f"Error starting client: {e}")

def main():
    clear_screen()
    print_header()
    print("\nWhat would you like to do?")
    print("1. Start Server & Play (Host a game)")
    print("2. Join Game (Connect to a host)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\nStarting server...")
            if run_server():
                time.sleep(1)  # Wait for server to start
                
                # Ask about game mode
                print("\nSelect game mode:")
                print("1. Single Game")
                print("2. Best of Three")
                
                while True:
                    mode_choice = input("Enter choice (1-2): ").strip()
                    if mode_choice == "1":
                        game_mode = "single_game"
                        break
                    elif mode_choice == "2":
                        game_mode = "best_of_3"
                        break
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                
                print(f"\nStarting game in {game_mode} mode...")
                run_client(game_mode)
            break
            
        elif choice == "2":
            host = input("\nEnter server IP (or press Enter for localhost): ").strip()
            if not host:
                host = "localhost"
            print(f"\nConnecting to {host}...")
            os.environ['TICTACTOE_HOST'] = host
            run_client()
            break
            
        elif choice == "3":
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0) 