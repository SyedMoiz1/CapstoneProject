import websocket
import threading
import time
import json
from chess_board.app2 import Board
from user_screen import LogWindow

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
    """
    Main game logic, using the Board instance.
    """
    time.sleep(5)  # Ensure the WebSocket is established
    if board:
        board.home()
        # time.sleep(3)
        # board.processMove("h7h5")
        # time.sleep(1)
        # board.processMove("g7g5")
        # time.sleep(1)
        # board.processMove("f7f5")
        # time.sleep(1)
        # board.processMove("e7e5")
        # time.sleep(1)
        # board.processMove("d7d5")
        # time.sleep(1)
        # board.processMove("c7c5")
        # time.sleep(1)
        # board.processMove("b7b5")
        # time.sleep(1)
        # board.processMove("a7a5")
        # time.sleep(1)

        board.processMove("b1c3")
        board.processMove("b2b4")
        time.sleep(1)
        board.processMove("a7a5")
        time.sleep(1)
        board.processMove("b4a5")
        time.sleep(1)
        board.processMove("b8a6")
        time.sleep(1)
        board.processMove("b1c3")
 
    else:
        print("Board is not initialized yet. WebSocket connection might not be established.")

if __name__ == "__main__":
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
