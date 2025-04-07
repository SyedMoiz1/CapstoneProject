from voice_input import transcribe_audio
from game.adaptive import AdaptiveGame
from game.standard import StandardGame
from chess_board.app2 import Board
from user_screen import LogWindow
import threading
import websocket
import time


# Global board instance (initialized in on_open)
board = None

def on_message(ws, message):
    """
    Handle incoming WebSocket messages and pass them to the Board.
    """
    global board
    if board:
        board.handle_response(message)

def on_error(ws, error):
    """
    Handle WebSocket errors.
    """
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    """
    Handle WebSocket closing.
    """
    print("WebSocket closed")

def on_open(ws):
    """
    Initialize the Board when WebSocket connection is established.
    """
    print("WebSocket connected")
    global board
    board = Board(ws)  # Initialize Board with WebSocketApp instance


def run_game():
    time.sleep(5)
    if board:
        while True:
            # # user_screen.log_to_gui("Pick option 1 or 2 for play style:\n1: Voice Commands\n2: By Hand")
            # # while (playstyle := transcribe_audio().lower()) not in {"1", "2"}: user_screen.log_to_gui("Invalid input. Please Say 1 or 2")            
            # playstyle = 1
            # if playstyle == 1: mode = "Voice Commands"
            # else: mode = "By hand"


            user_screen.log_to_gui(f"Welcome to Autochess!")

            time.sleep(3)
            #ask user if they would like to play standard or adaptive
            user_screen.log_to_gui("Pick your game mode:\n1: Standard\n2: Adaptive")
            while (gamemode := transcribe_audio().lower()) not in {"standard", "adaptive"}:
                user_screen.log_to_gui(f"Input recieved: {gamemode}.\nInvalid input.", clear=False)
                time.sleep(2)
                user_screen.log_to_gui("Pick your game mode:\n1: Standard\n2: Adaptive")       
            #gamemode = "standard"
            
            #start standard/adaptive programs
            if gamemode == "standard": #STANDARD GAME MODE
                game = StandardGame(board, user_screen)
                game.start()
            else: #ADAPTIVE GAME MODE
                game = AdaptiveGame(board, user_screen)
                game.start()
            
            user_screen.log_to_gui("Would you like to restart? (Yes or No)")
            while (restart := transcribe_audio().lower()) not in {"yes", "no"}:
                user_screen.log_to_gui(f"Input recieved: {restart}.\nInvalid input.", clear=False)
                time.sleep(2)
                user_screen.log_to_gui("Would you like to restart? (Yes or No)") 
            if restart == "no":
                user_screen.log_to_gui(f"Input selected {restart}. Thank you for playing!", clear=False)
                time.sleep(3)
                break
            else:
                user_screen.log_to_gui(f"Input selected {restart}. Restarting game...", clear=False)
                time.sleep(3)
    else:
        print("Board is not initialized yet. WebSocket connection might not be established.")



if __name__ == "__main__":
    # Tkinter must run in the main thread
    # user_screen = LogWindow()
    # print("Connecting to Moonraker...")
    # MOONRAKER_WS_URL = "ws://autochessV2:7125/websocket"
    # ws = websocket.WebSocket()
    # ws.connect(MOONRAKER_WS_URL)
    # print("Connected to Moonraker WebSocket")


    # # Start the game logic in a separate thread
    # game_thread = threading.Thread(target=run_game, args=(ws,), daemon=True)
    # game_thread.start()

    # # Start Tkinter in the main thread
    # user_screen.run()  # This should be the last command in `main`
        # Start the Tkinter UI
    user_screen = LogWindow()

    print("Connecting to Moonraker...")
    MOONRAKER_WS_URL = "ws://autochessV2:7125/websocket"

    # Initialize WebSocketApp
    ws = websocket.WebSocketApp(
        MOONRAKER_WS_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )

    # Run WebSocket in a separate thread
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()

    # Wait for WebSocket to connect before starting the game logic
    time.sleep(5)  # Give some time for the connection to establish

    # Start the game logic in a separate thread
    game_thread = threading.Thread(target=run_game, daemon=True)
    game_thread.start()

    # Start Tkinter in the main thread
    user_screen.run()  # This should be the last command in `main`