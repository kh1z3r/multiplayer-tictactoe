import sys
import subprocess
import os
import threading
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
        subprocess.Popen([sys.executable, "server.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        return True
    except Exception as e:
        print(f"Error starting server: {e}")
        return False

def run_client():
    """Run the client script"""
    try:
        subprocess.run([sys.executable, "client.py"],
                      creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
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
            clear_screen()
            print_header()
            print("\nStarting server and game client...")
            
            # Start server in a separate process
            if run_server():
                # Wait a moment for server to start
                time.sleep(1)
                # Start client
                run_client()
            break
            
        elif choice == "2":
            clear_screen()
            print_header()
            print("\nStarting client...")
            try:
                run_client()
            except KeyboardInterrupt:
                print("\nClient stopped.")
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