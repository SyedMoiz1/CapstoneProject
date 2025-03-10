import chess
import chess.pgn
import chess.engine
import io
import os
# Path to stockfish 
STOCKFISH_PATH = "../stockfish-engine/stockfish"


def analyze_pgn(pgn_game, threshold=175, player_white=True):
    """Analyze a PGN file for blunders using Stockfish.
    
    Args:
        pgn_path (str): Path to the PGN file.
        threshold (int): Centipawn loss to consider a blunder (default: -300).
    
    Returns:
        list: Blunder moves with position and evaluation drop.
    """

    pgn_io = io.StringIO(pgn_game)
    game = chess.pgn.read_game(pgn_io)

    board = game.board()
    blunders = []

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        for move in game.mainline_moves():

            #Get evaluation before move
            info_before = engine.analyse(board, chess.engine.Limit(depth=20))
            #print(f"MOVE: {move.uci()}")
            #Make move
            if player_white:
                score_before = info_before["score"].white().score(mate_score=10000)
            else: score_before = info_before["score"].black().score(mate_score=10000)
            
            board.push(move)

            #Get evaluation after move
            info_after = engine.analyse(board, chess.engine.Limit(depth=20))

            if player_white:
                score_after = info_after["score"].white().score(mate_score=10000)
            else: score_after = info_after["score"].black().score(mate_score=10000)

            #Check for blunder
            score_drop = score_before - score_after
            #print(f"SCORE DROP: {score_drop}")
            if score_drop > threshold:
                blunders.append((board.fen(), move.uci(), score_drop))
    
    return blunders

if __name__ == "__main__":
    pgn_game = '[Event "?"]\n[Site "?"]\n[Date "????.??.??"]\n[Round "?"]\n[White "?"]\n[Black "?"]\n[Result "*"]\n\n1. f3 d5 2. g4 e5 3. f4 Bxg4 4. f5 Qh4# *'
    #pgn_game = '[Event "?"]\n[Site "?"]\n[Date "????.??.??"]\n[Round "?"]\n[White "?"]\n[Black "?"]\n[Result "*"]\n\n1. e4 e5 2. Qf3 d6 3. Qb3 Nc6 4. Qxb7?? Bxb7 *'
    print(analyze_pgn(pgn_game, player_white=True))