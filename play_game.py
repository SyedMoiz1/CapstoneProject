from voice_input import transcribe_audio
from game.adaptive import AdaptiveGame
from game.standard import StandardGame
from chess_board.app import Board
import websocket

print("Connecting to Moonraker...")
MOONRAKER_WS_URL = "ws://autochess:7125/websocket"
ws = websocket.WebSocket()
ws.connect(MOONRAKER_WS_URL)
print("Connected to Moonraker WebSocket")


#ask user if they would like to play through voice commands or physically move pieces
while True:
    print("Pick option 1 or 2 for play style:\n1: Voice Commands\n2: By Hand")
    while (playstyle := transcribe_audio().lower()) not in {"1", "2"}: print("Invalid input. Please Say 1 or 2")            

    if playstyle == 1: mode = "Voice Commands"
    else: mode = "By hand"
    print(f"Game mode selected: {mode}")

    #ask user if they would like to play standard or adaptive
    print("Pick your game mode:\n1: Standard\n2: Adaptive")
    while (gamemode := transcribe_audio().lower()) not in {"standard", "adaptive"}: print("Invalid input. Please Say Standard or Adaptive")       

    board = Board(ws)
    #start standard/adaptive programs
    if gamemode == "standard": #STANDARD GAME MODE
        game = StandardGame(board)
        game.start()
    else: #ADAPTIVE GAME MODE
        game = AdaptiveGame(board)
        game.start()
    
    print("Would you like to restart?")
    while (restart := transcribe_audio().lower()) not in {"yes", "no"}: print("Invalid input. Please Say 'Yes' or 'No'") 
    if restart == "no":
        break