import subprocess
import chess
from game.base_game import BaseGame
from game.config import LC0_PATH

class StandardGame(BaseGame):
    def __init__(self, board):
        super().__init__(board)
        self.difficulty = None
        


    def start(self):
        print("Starting standard game...")
        
        self.difficulty = self.take_input("Please select a difficulty level: \n1. Easy\n2. Medium\n3. Hard\n").lower()
        while self.difficulty not in {"easy", "medium", "hard"}:
            print(f"Input recieved: {self.difficulty}")
            self.difficulty = self.take_input("Invalid input. Please select a difficulty level: \n1. Easy\n2. Medium\n3. Hard\n").lower()


        print("Difficulty level selected: " + self.difficulty)
        if self.difficulty == "easy": 
            self.weights_file = LC0_PATH + "900.pb.gz"
        elif self.difficulty == "medium":
            self.weights_file = LC0_PATH + "1400.pb.gz"
        else:
            self.weights_file = LC0_PATH + "1800.pb.gz"    

#########STARTING ENGINE
        engine = self.start_engine(self.weights_file)

        #Taking user color choine
        user_color = self.take_input("Please select a color: \n1. White\n2. Black\n").lower()
        while user_color not in {"white", "black"}:
            print(f"Input recieved: {user_color}")
            user_color = self.take_input("Invalid input. Please select a color: \n1. White\n2. Black\n").lower()

        print("You are playing as " + user_color + ". Let's start the game!\n")
        self.display_board(self.board)

        #First move
        if user_color == "white":
            self.first_move(engine, "user")
        else:
            self.first_move(engine, "AI")

        
        self.display_board(self.board)
        #Game loop
        move_count = 0 #counter to reset board.home()
        while not self.game_over():
            #User's move
            print(self.moves + "\n")
            user_move = self.take_user_move(self.board)
            self.moves += user_move.uci() + " "
            #update board state
            self.board.push(user_move)
            self.display_board(self.board)
            print(self.moves)

            move_count += 1
            # Call self.board.home() every 10 moves
            if move_count % 10 == 0:
                print("Recalibrating magnet to home position...")
                self.board.home()

            #AI's move
            if not self.game_over():
                ai_move = self.take_AI_move(engine)
                print("AI's move: " + ai_move.uci())
                self.moves += ai_move.uci() + " "
                #update board state
                self.board.push(ai_move)
                self.display_board(self.board)

                move_count += 1
                # Call self.board.home() every 10 moves
                if move_count % 10 == 0:
                    print("Recalibrating magnet to home position...")
                    self.board.home()

if __name__ == "__main__":
    game = StandardGame()
    game.start()