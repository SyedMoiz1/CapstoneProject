import chess
import subprocess
import re
from game.config import LC0_PATH

from voice_input import transcribe_audio
import time

class BaseGame:
    def __init__(self, actual_board, user_screen):
        self.board = chess.Board()
        self.moves = ""
        self.weights_file = None
        self.actual_board = actual_board
        self.user_screen = user_screen

    def game_over(self):
        #Checks if game is over
        if self.board.is_game_over():
            # Check the reason
            if self.board.is_checkmate():
                #CHECK WINNER
                if self.board.turn == chess.BLACK:
                    winner = "White"
                else:
                    winner = "Black"
                self.user_screen.log_to_gui(f"Game over!\n The game ended in checkmate.\nThe winner is {winner}.")
            elif self.board.is_stalemate():
                self.user_screen.log_to_gui("Game over!\n The game ended in a stalemate.")
            elif self.board.is_insufficient_material():
                self.user_screen.log_to_gui("Game over!\n The game ended due to insufficient material.")
            elif self.board.can_claim_fifty_moves():
                self.user_screen.log_to_gui("Game over!\n The game ended due to the fifty-move rule.")
            elif self.board.can_claim_threefold_repetition():
                self.user_screen.log_to_gui("Game over!\n The game ended due to threefold repetition.")
            return True
        
    def first_move(self,engine, turn):
       #performs the first move of the game
        
        if turn == "user":
            user_move = self.take_user_move(self.board)
            #user_move = chess.Move.from_uci("e2e4")
            self.user_screen.log_to_gui(f"Your opening move: {user_move.uci()}")
            uci_command = "position startpos moves " + user_move.uci()
            self.send_command(engine, uci_command)
            self.moves += uci_command + " "
            #actual_board.processMove(str(user_move))
            #update board state
            self.board.push(user_move)
            
            self.display_board(self.board)

            time.sleep(2)
            #Take AI's move
            ai_move = self.take_AI_move(engine)
            #ai_move = chess.Move.from_uci("e7e5")
            self.user_screen.log_to_gui("AI's opening move: " + ai_move.uci())
            time.sleep(4)
            self.moves += ai_move.uci() + " "
            #self.actual_board.processMove(str(ai_move))
            #update board state
            self.board.push(ai_move)
            
        else:
            ai_move = self.take_AI_move(engine)
            #ai_move = chess.Move.from_uci("e7e5")
            self.user_screen.log_to_gui("AI's opening move: " + ai_move.uci()+ "\n")
            time.sleep(4)
            self.moves += "position startpos moves " + ai_move.uci() + " "
            #update board state
            #self.actual_board.processMove(str(ai_move))
            self.board.push(ai_move)
            

    def take_AI_move(self, engine):
        #takes AI move and validates it
        print(f"GIVING AI COMMAND: {self.moves}")
        self.send_command(engine, self.moves)
        self.send_command(engine, "go nodes 3")

        while True:
            try:
                output = self.read_response(engine)
                if "bestmove" in output:
                    best_move = output.split("bestmove ")[1].split(" ")[0]
                    if chess.Move.from_uci(best_move) in self.board.legal_moves:
                        self.actual_board.processMove(str(best_move))
                        return chess.Move.from_uci(best_move)
                    else:
                        print(f"Invalid move from engine: {best_move}")
                else:
                    print("No valid move found in engine output.")
                self.send_command(engine, "go nodes 3")
            except (ValueError, IndexError) as e:
                print(f"Error parsing engine output: {e}")
                self.send_command(engine, "go nodes 3")

    def take_user_move(self, board):
        #take users move and validates it, takes board state and checks if move is valid
        while True:
            try:
                #while True:
                move_input = self.take_move("Please enter your move: ")
                    
                verify = self.take_input(f"Move selected: {move_input}, are you sure? (Yes/No)")
                while verify not in {"yes", "no"}:
                    self.user_screen.log_to_gui(f"Input received '{verify}'. Invalid input", clear = False)
                    time.sleep(2)
                    verify = self.take_input(f"Move selected: {move_input}, are you sure? (Yes/No)")

                if verify == "no":
                    continue

                move = chess.Move.from_uci(move_input)

                if move in board.legal_moves:
                    self.actual_board.processMove(str(move))
                    time.sleep(4)
                    return move
                else:
                    self.user_screen.log_to_gui("Invalid move. Please enter a valid move.")
                    time.sleep(2)
            except ValueError:
                self.user_screen.log_to_gui("Invalid input. Please enter a move in UCI format (e.g., e2e4).")
                time.sleep(2)

    def start_engine(self, weights_file):
        lc0_path = LC0_PATH + "lc0"
        command = [lc0_path, f"--weights={weights_file}"]
        #print("Starting engine with command:", " ".join(command))  # Debug print
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    
    def send_command(self, process, command):
        # Send a command to lc0
        process.stdin.write(command + "\n")
        process.stdin.flush() #Forces the command to be sent immediately

    def read_response(self, process):
        output = []
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(line)  # Debug print
                output.append(line)
                if "bestmove" in line:
                    break
        return "\n".join(output)

    def display_board(self, board):
        #Displays the board with ranks and files
        board_str = ""

        BOLD = "\033[1m"
        RESET = "\033[0m"
        files = BOLD + "  a b c d e f g h  " + RESET
        board_str += files + "\n"
        for i, row in enumerate(str(board).split("\n")):
            rank = BOLD + str(8-i) + RESET
            board_str += f"{rank} {row} {rank}\n"
        board_str += files + "\n"
        print(board_str)



    def board_to_matrix(self, board):
        #Converts board to matrix
        board_matrix = []
        for row in str(board).split("\n"):
            print(f"ROW: {row}")
            board_matrix.append(row.split(" ")[0:8])
        print(board_matrix)
        return #board_matrix

    def find_winner(self, board):
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                #black wins
                return False 
            else:
                # White wins
                return True
        else:
            return None #represents a draw/no winner
        
    def take_input(self, prompt):
        self.user_screen.log_to_gui(prompt)
        response = transcribe_audio()
        
        return response
    
    def take_move(self, prompt):
        while True:
            move = self.take_input(prompt)
            self.user_screen.log_to_gui(move)
            move_to_uci = self.convert_to_uci(move)

            if move_to_uci:
                return move_to_uci
            else:
                self.user_screen.log_to_gui(f"Input received: {move}.\nInvalid input format. Please say moves like 'E2 E4'.")

    def convert_to_uci(self, speech_input):
        # Normalize input: Remove commas, extra spaces, and convert to lowercase
        cleaned_input = re.sub(r"[,\s]+", " ", speech_input.strip().lower())

        # Match valid chess move formats (like "e2 e4", "e2e4", "e2, e4")
        pattern = r"([a-h][1-8])\s?([a-h][1-8])"

        match = re.match(pattern, cleaned_input)
        if not match:
            return None

        # Extract the move and concatenate to UCI format
        uci_move = match.group(1) + match.group(2)
        return uci_move