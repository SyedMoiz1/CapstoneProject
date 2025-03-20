from flask import Flask, render_template, request, jsonify
import json
import requests
from time import sleep
import matplotlib.pyplot as plt
import websocket

#websocket url
MOONRAKER_WS_URL = "ws://autochessV2:7125/websocket"
#ws = websocket.WebSocket()

#request_counter = 0


class Board:
    def __init__(self, ws):
        self.ws = ws
        self.request_counter = 0
        self.graveyardCount = 0
        self.boardState = []
        self.resetBoard()
        self.piece_symbols = {
        "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
        "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
        "": ""
        }
    #send gcode using moon raker

    def send_gcode(self, command):
        
        payload = {
            "jsonrpc": "2.0",
            "method": "printer.gcode.script",
            "params": {"script": command},
            "id": self.request_counter
        }

        # Check if WebSocket is connected
        if not self.ws or not self.ws.connected:
            raise ConnectionError("WebSocket is not connected. Cannot send G-code.")
        

        # Send the G-code command
        try:
            self.ws.send(json.dumps(payload))
            print(f"Sent G-code: {command} (id: {self.request_counter})")
        except Exception as e:
            raise RuntimeError(f"Error sending G-code: {e}")

        # If command is "custom_home", we skip waiting for a response
        if command == "custom_home":
            print("custom_home command sent. No response expected.")
            self.request_counter += 1
            return
        
        gcode_responses = []

        #poll for response
        while True:
            try:
                message = self.ws.recv()

                # Check if message is empty
                # if not message.strip():
                #     raise ValueError("Received an empty response from WebSocket.")
                
                #print(f"Received raw message: {message}")  # Debugging log
                # Try to parse JSON response
                try:
                    data = json.loads(message)
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON Parsing Error: {e}\nInvalid JSON message: {message}")

                # Check for G-code response
                if data.get("method") == "notify_gcode_response":
                    gcode_responses.append(data["params"][0])
                    continue

                # Command acknowledged
                if data.get("id") == self.request_counter:
                    print("\nCommand acknowledged:")
                    print(json.dumps(data, indent=4))
                    break
            except Exception as e:
                raise RuntimeError(f"Error receiving WebSocket message: {e}")
    
        if gcode_responses:
            print("\nG-code response(s):")
            for line in gcode_responses:
                print(line)
        # else:
        #     raise RuntimeError(f"No G-code response received for command: {command}")
            
        self.request_counter += 1


    # Initialize boardState with first four columns empty
    #boardState = []

    def resetBoard(self):
        self.boardState = [
            ["", "", "", "", "r", "n", "b", "q", "k", "b", "n", "r"],
            ["", "", "", "", "p", "p", "p", "p", "p", "p", "p", "p"],
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "P", "P", "P", "P", "P", "P", "P", "P"],
            ["", "", "", "", "R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

    # graveyardCount = 0

    # resetBoard()

    # Unicode chess piece symbols
    # piece_symbols = {
    #     "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    #     "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
    #     "": ""
    # }


    def drawBoard(self):
        fig, ax = plt.subplots(figsize=(12, 8))  # Wider board to accommodate 12 columns
        colors = ["#F0D9B5", "#B58863"]  # Light and dark squares
        graveyard_colors = ["#D3D3D3", "#A9A9A9"]  # Light grey and dark grey for graveyard squares

        num_cols = len(self.boardState[0])  # 12 columns
        num_rows = len(self.boardState)    # 8 rows

        # Draw squares and pieces
        for row in range(num_rows):
            for col in range(num_cols):
                if col < 4:  # First 4 columns are graveyard
                    color = graveyard_colors[(row + col) % 2]  # Checkerboard pattern for graveyard
                else:
                    color = colors[(row + col) % 2]  # Alternate colors
                rect = plt.Rectangle((col, 7 - row), 1, 1, facecolor=color)
                ax.add_patch(rect)
                # Draw piece if it exists
                piece = self.boardState[row][col]
                if piece:
                    ax.text(col + 0.5, 7 - row + 0.5, self.piece_symbols[piece], fontsize=32,
                            ha='center', va='center')

        # Custom file labels (for 12 columns)
        files = ['gr1', 'gr2', 'gr3', 'gr4', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']  # First 4 empty, then standard files
        for i in range(num_cols):
            ax.text(i + 0.5, -0.3, files[i], ha='center', va='center', fontsize=14)  # bottom
            ax.text(i + 0.5, 8.3, files[i], ha='center', va='center', fontsize=14)   # top

        # Add rank numbers (1-8) on sides
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        for i in range(num_rows):
            ax.text(-0.3, i + 0.5, ranks[7 - i], ha='center', va='center', fontsize=14)  # left
            ax.text(num_cols + 0.3, i + 0.5, ranks[7 - i], ha='center', va='center', fontsize=14)  # right

        # Set board limits and hide axes
        ax.set_xlim(-0.5, num_cols + 0.5)
        ax.set_ylim(-0.5, 8.5)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.show()


    # Draw the board
    # drawBoard()

    def chessCoordToArrayCoord(self, coord):
        if len(coord) == 2:
            file = coord[0]
            rank = coord[1]
            col = ord(file) - ord('a') + 4  # Adjust for 4 graveyard columns
            row = 8 - int(rank)
        else:
            file = coord[2]
            rank = coord[3]
            col = int(rank) - 1
            row = 8 - int(file)
            return [row, col]

        return [row, col]

    def chessCoordToPhysicalCoord(self, coord):
        arrX, arrY = self.chessCoordToArrayCoord(coord)

        diffX = 7 - arrX
        diffY = 11 - arrY

        phyX =  28 + diffX * 38
        phyY = 20 + diffY * 38

        return phyX, phyY
    
    def calculateDirection(self, start, end):
        start = self.chessCoordToArrayCoord(start)
        end = self.chessCoordToArrayCoord(end)
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        direction = ""

        #check for north south
        if dx != 0:
            if dx < 0:
                direction += "n"
            else:
                direction += "s"

        #check for east west
        if dy != 0:
            if dy < 0:
                direction += "w"
            else:
                direction += "e"
        
        return direction

    #change to moonraker later
    def sendCoordMove(self, coord, nudge=False, startCoord=None):
        x, y = self.chessCoordToPhysicalCoord(coord)

        nudgeVal = 10
        if nudge:
            direction = self.calculateDirection(startCoord,coord)

            if "n" in direction: x += nudgeVal
            elif "s" in direction: x -= nudgeVal
            elif "e" in direction: y -= nudgeVal
            elif "w" in direction: y += nudgeVal

        gcode = f'_CLIENT_LINEAR_MOVE X={x} Y={y} F=1950 ABSOLUTE=1'
        print(gcode) 
                
        self.send_gcode(gcode)

    def sendTileDeltaMove(self, delta, direction):
        delta = 38 * delta
        
        if direction == "n":
            x = delta
            y = 0
        elif direction == "s":
            x = -delta
            y = 0
        elif direction == "e":
            x = 0
            y = delta
        elif direction == "w":
            x = 0
            y = -delta
        
        gcode = f'_CLIENT_LINEAR_MOVE X={x} Y={y} F=1950 ABSOLUTE=0'
        
        self.send_gcode(gcode)    


    def activateMagnet(self, active):
        if active:
            self.send_gcode("MAG_ON")
        else:
            self.send_gcode("MAG_OFF")

    #home
    def home(self):
        self.send_gcode("custom_home")

    def graveCountToArrayCoord(self, graveCount):
        
        row = (graveCount - 1) // 4 + 1  # Calculate row number
        col = (graveCount - 1) % 4 + 1   # Calculate column number

        coord = self.chessCoordToArrayCoord(f"gr{row}{col}")
        
        return coord

    def updateboardState(self, start, end, graveyard=False):
        print(start, end)
        startCoord = self.chessCoordToArrayCoord(start)

        if not graveyard:
            endCoord = self.chessCoordToArrayCoord(end)
        else:
            endCoord =  self.graveCountToArrayCoord(end)

        self.boardState[endCoord[0]][endCoord[1]] = self.boardState[startCoord[0]][startCoord[1]]
        self.boardState[startCoord[0]][startCoord[1]] = ""

    def moveToGraveyard(self, coord):
        self.sendCoordMove(coord)
        sleep(0.5)
        self.activateMagnet(True)
        sleep(1)
        
        pieceRow, pieceCol = self.chessCoordToArrayCoord(coord)

        print(pieceRow, pieceCol)
        self.graveyardCount += 1
        graveRow, graveCol = self.graveCountToArrayCoord(self.graveyardCount)

        print(graveRow, graveCol)

        if pieceRow > 3:
            # move backwards half a tile
            self.sendTileDeltaMove(0.5,"s")
            offset = 0.5
        else:
            # move forward half a tile
            self.sendTileDeltaMove(0.5,"n")
            offset = -0.5

        eastSlide = (pieceCol - graveCol - 0.5)

        self.sendTileDeltaMove(eastSlide,"e")

        northSouthSlide = (pieceRow - graveRow + offset)
        print(northSouthSlide)

        self.sendTileDeltaMove(northSouthSlide,"n")
        self.sendTileDeltaMove(0.5,"e")

        self.activateMagnet(False)

        self.updateboardState(coord, self.graveyardCount, graveyard=True)

        # return graveRow, graveCol


    def processMove(self, move):
        print(f"Processing move :{move}")
        start = move[:2]
        end = move[2:]

        #array position of start
        arrayPosStart = self.chessCoordToArrayCoord(start)
        pieceType = self.boardState[arrayPosStart[0]][arrayPosStart[1]].lower()

        print(pieceType)

        if pieceType == '':
            print('NO PIECE')
            return

        #check for capture
        arrayPosEnd = self.chessCoordToArrayCoord(end)
        finalPosType = self.boardState[arrayPosEnd[0]][arrayPosEnd[1]].lower()

        if finalPosType != '':
            print('CAPTURE')
            self.moveToGraveyard(end)
        else:
            print('NO CAPTURE')
        
        #check for castling
        if pieceType == 'k' and (start == 'e1' or start == 'e8') and (end == 'g1' or end == 'c1' or end == 'g8' or end == 'c8'):
            #white king side
            if start == 'e1' and end == 'g1':
                self.sendCoordMove('e1')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendCoordMove('g1')
                sleep(0.5)
                self.activateMagnet(False)
                sleep(1)
                self.sendCoordMove('h1')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendTileDeltaMove(0.5,"s")
                self.sendTileDeltaMove(2,"w")
                self.sendTileDeltaMove(0.5,"n")
                sleep(0.5)
                self.activateMagnet(False)
                self.updateboardState('h1', 'f1')
                self.updateboardState('e1', 'g1')
            #white queen side
            elif start == 'e1' and end == 'c1':
                self.sendCoordMove('e1')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendCoordMove('c1')
                sleep(0.5)
                self.activateMagnet(False)
                sleep(1)
                self.sendCoordMove('a1')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendTileDeltaMove(0.5,"s")
                self.sendTileDeltaMove(3,"e")
                self.sendTileDeltaMove(0.5,"n")
                sleep(0.5)
                self.activateMagnet(False)
                self.updateboardState('a1', 'd1')
                self.updateboardState('e1', 'c1')
            #black king side
            elif start == 'e8' and end == 'c8':
                self.sendCoordMove('e8')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendCoordMove('g8')
                sleep(0.5)
                self.activateMagnet(False)
                sleep(1)
                self.sendCoordMove('h8')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendTileDeltaMove(0.5,"n")
                self.sendTileDeltaMove(2,"w")
                self.sendTileDeltaMove(0.5,"s")
                sleep(0.5)
                self.activateMagnet(False)
                self.updateboardState('h8', 'f8')
                self.updateboardState('e8', 'g8')
            elif start == 'e8' and end == 'g8':
                self.sendCoordMove('e8')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendCoordMove('g8')
                sleep(0.5)
                self.activateMagnet(False)
                sleep(1)
                self.sendCoordMove('h8')
                sleep(0.5)
                self.activateMagnet(True)
                sleep(1)
                self.sendTileDeltaMove(0.5,"n")
                self.sendTileDeltaMove(3,"e")
                self.sendTileDeltaMove(0.5,"s")
                sleep(0.5)
                self.activateMagnet(False)
                self.updateboardState('h8', 'f8')
                self.updateboardState('e8', 'g8')
            
        #check for knight
        if pieceType == 'n':
            #check direction of move
            # Calculate difference
            dx = arrayPosEnd[0] - arrayPosStart[0]
            dy = arrayPosEnd[1] - arrayPosStart[1]

            if abs(dx) == 2:
                majorDirection = "n" if dx < 0 else "s"
                minorDirection = "w" if dy > 0 else "e"
            else:
                majorDirection = "e" if dy < 0 else "w"
                minorDirection = "n" if dx < 0 else "s"
            
            self.sendCoordMove(start)
            sleep(0.5)
            self.activateMagnet(True)
            sleep(1)
            self.sendTileDeltaMove(0.5,minorDirection)
            self.sendTileDeltaMove(2,majorDirection)
            self.sendTileDeltaMove(0.5,minorDirection)
            sleep(0.5)
            self.activateMagnet(False)
            self.updateboardState(start, end)
        else:
            self.sendCoordMove(start)
            sleep(0.5)
            self.activateMagnet(True)
            sleep(1)
            self.sendCoordMove(end)
            sleep(0.5)
            self.activateMagnet(False)

            self.updateboardState(start, end)
        # drawBoard()

app = Flask(__name__)

# Initial chess board setup
board_state = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]

# File to store moves
MOVES_FILE = "chess_moves.txt"

@app.route('/')
def index():
    return render_template('chess.html', board=json.dumps(board_state))

@app.route('/move', methods=['POST'])
def move():
    global board_state

    data = request.json
    move_notation = data.get('move_notation')

    print(move_notation)

    board.processMove(move_notation)

    board_state = data.get('new_state')

    return jsonify({"message": "Move recorded successfully!"})

if __name__ == '__main__':
    print("Connecting to Moonraker...")
    MOONRAKER_WS_URL = "ws://autochessV2:7125/websocket"
    ws = websocket.WebSocket()
    ws.connect(MOONRAKER_WS_URL)
    print("Connected to Moonraker WebSocket")

    board = Board(ws)


    board.home()
    board.processMove('e1c1')

    app.run(debug=True)