import subprocess
import chess
import io
import chess.pgn
import json
from base_game import BaseGame
from user import User
from analyze_game import analyze_pgn
import sys
import time


class TestEngines(BaseGame):
    def __init__(self):
        super().__init__()

    #used to simulate a game between 2 engines
    def startGame(self, weight1, weight2):
        weights_file1 = f"../MaiaNet/lc0/build/release/{weight1}.pb.gz"
        weights_file2 = f"../MaiaNet/lc0/build/release/{weight2}.pb.gz"
        engine1 = self.start_engine(weights_file1)
        engine2 = self.start_engine(weights_file2)
        self.board = chess.Board()
        

        #first weight file takes white color
        engine1_firstMove = self.take_AI_move(engine1)
        self.moves = "position startpos moves " + engine1_firstMove.uci() + " "
        self.board.push(engine1_firstMove)
        print(f"engine {weight1}'s first move: {engine1_firstMove.uci()}")
        self.display_board(self.board)
        #time.sleep(1)

        while not self.game_over():
            engine2_move = self.take_AI_move(engine2)
            self.moves += engine2_move.uci() + " "
            self.board.push(engine2_move)
            print(f"engine {weight2}'s move: {engine2_move.uci()}")
            self.display_board(self.board)
            #time.sleep(1)
            

            if not self.game_over():
                engine1_move = self.take_AI_move(engine1)
                self.moves += engine1_move.uci() + " "
                self.board.push(engine1_move)
                print(f"engine {weight1}'s move: {engine1_move.uci()}")
                self.display_board(self.board)
                #time.sleep(1)
        
def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <arg1> <arg2>")
        return
    
    weights1 = sys.argv[1]
    weights2 = sys.argv[2]

    test = TestEngines()

    test.startGame(weights1, weights2)


if __name__ == "__main__":
    main()
        