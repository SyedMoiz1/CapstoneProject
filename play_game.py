from voice_input import transcribe_audio
from game.adaptive import AdaptiveGame
from game.standard import StandardGame
from chess_board.app import Board
from user_screen import LogWindow
import threading
import websocket
import time


print("Connecting to Moonraker...")
MOONRAKER_WS_URL = "ws://autochess:7125/websocket"
ws = websocket.WebSocket()
ws.connect(MOONRAKER_WS_URL)
print("Connected to Moonraker WebSocket")

def run_game():
    while True:
        # user_screen.log_to_gui("Pick option 1 or 2 for play style:\n1: Voice Commands\n2: By Hand")
        # while (playstyle := transcribe_audio().lower()) not in {"1", "2"}: user_screen.log_to_gui("Invalid input. Please Say 1 or 2")            
        playstyle = 1
        if playstyle == 1: mode = "Voice Commands"
        else: mode = "By hand"
        user_screen.log_to_gui(f"Game mode selected: {mode}")

        time.sleep(4)
        #ask user if they would like to play standard or adaptive
        # user_screen.log_to_gui("Pick your game mode:\n1: Standard\n2: Adaptive")
        # while (gamemode := transcribe_audio().lower()) not in {"standard", "adaptive"}: user_screen.log_to_gui("Invalid input. Please Say Standard or Adaptive")       
        gamemode = "standard"
        board = Board(ws)
        #start standard/adaptive programs
        if gamemode == "standard": #STANDARD GAME MODE
            game = StandardGame(board, user_screen)
            game.start()
        else: #ADAPTIVE GAME MODE
            game = AdaptiveGame(board, user_screen)
            game.start()
        
        user_screen.log_to_gui("Would you like to restart?")
        while (restart := transcribe_audio().lower()) not in {"yes", "no"}: user_screen.log_to_gui("Invalid input. Please Say 'Yes' or 'No'") 
        if restart == "no":
            break


if __name__ == "__main__":
    # Tkinter must run in the main thread
    user_screen = LogWindow()

    # Start the game logic in a separate thread
    game_thread = threading.Thread(target=run_game, daemon=True)
    game_thread.start()

    # Start Tkinter in the main thread
    user_screen.run()  # This should be the last command in `main`