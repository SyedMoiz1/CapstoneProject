import subprocess
import chess
import io
import chess.pgn
import json
from base_game import BaseGame
from user import User
from analyze_game import analyze_pgn

N = 5 #Adapt every 5 games and Weight the last 5 games more heavily

class AdaptiveGame(BaseGame):
    def __init__(self):
        super().__init__()        


    def start(self):
        print("Starting adaptive game...")

        #first check if user already exists in json
        #pass newuser True/False to user class, which decides whether new entry is to be created
        #if new user False, run function which checks if difficulty adjustment is needed based on users data
        #record game in pgn format, and after each game run a full analysis to count the number of blunders, and update

        while True:
            while (new_user := input("Are you a new user? (y/n): ").lower()) not in {"y", "n"}: print("Invalid input.")

        
            name = input("Please enter your name: ")
            
            if new_user == "y" and self.user_exists(name):
                #check if user already exists in json
                while (name_exists_check := input(f"User {name} already exists. Would you like to continue as {name}? (y/n): ").lower()) not in {"y", "n"}: print("Invalid input.")
                if name_exists_check == "n": continue
                else: 
                    user = User(name)
                    print(f"Welcome {name}!")
                    break
            elif new_user == "y":
                while (difficulty := input(f"Please select a starting difficulty level: \n1. Easy\n2. Medium\n3. Hard\n").lower()) not in {"easy", "medium", "hard"}: print("Invalid input.")
                if difficulty == "easy": 
                    elo = 900
                elif difficulty == "medium":
                    elo = 1400
                else:
                    elo = 1800
                user = User(name, new_user=True, diff_level=elo)
                print(f"Welcome {name}!")
                break
            else:
                user = User(name)
                print(f"Welcome {name}!")
                break
        
        while True:  
            num_moves = 0
            winnerIswhite = None #initialize winner as None
            user_win = None
            self.moves = ""

            ######STARTING ENGINE
            self.weights_file = f" {user.diff_level}.pb.gz"
            #print("Starting engine with weights file:", self.weights_file)

            engine = self.start_engine(self.weights_file)
            self.board = chess.Board() #initialize board

            #Taking user color choice
            while (user_color := input(f"Please select a color: \n1. White\n2. Black\n").lower()) not in {"white", "black"}: print("Invalid input.")
            
            print(f"You are playing as {user_color}. Let's start the game!\n")
            self.display_board(self.board)
            #self.board_to_matrix(self.board)
            #print(self.board)

            #First move
            if user_color == "white":
                self.first_move(engine, "user")
                num_moves += 2
            else:
                self.first_move(engine, "AI")
                num_moves += 1

            

            self.display_board(self.board)
            #Game loop
            while not self.game_over():
                #User's move
                print(self.moves + "\n")
                user_move = self.take_user_move(self.board)
                self.moves += user_move.uci() + " "
                #update board state
                self.board.push(user_move)
                self.display_board(self.board)
                print(self.moves)
                num_moves += 1
                #AI's move
                if not self.game_over():
                    ai_move = self.take_AI_move(engine)
                    print("AI's move: " + ai_move.uci())
                    self.moves += ai_move.uci() + " "
                    #update board state
                    self.board.push(ai_move)
                    self.display_board(self.board)
                    num_moves += 1

           
            ####Game over

            #find if user is winner
            winnerIswhite = self.find_winner(self.board)
            if user_color == "white" and winnerIswhite == True:
                user_result = 'win'
            elif user_color == "black" and winnerIswhite == False:
                user_result = 'win'
            elif winnerIswhite == None:
                user_result = 'draw'
            else:
                user_result = 'loss'
 

            #Game analysis through stockfish
            game_pgn = self.convert_to_pgn(self.board)
            print("Analyzing game...")
            if user_color == "white":
                blunders = analyze_pgn(game_pgn, player_white=True)
            else:
                blunders = analyze_pgn(game_pgn, player_white=False)

            #print(blunders) #list of blunders
            print(f"{len(blunders)} blunders") #number of blunders
            print(f"{num_moves} moves played")

            #update user data
            self.update_user_data(user, len(blunders), num_moves, user_result)
            self.adjust_difficulty(user)

            #play again
            while (play_again := input("Would you like to play again? (yes/no): ").lower()) not in {"yes", "no"}: print("Invalid input.")
            if play_again == "no": break 


    def update_user_data(self, user, blunders, num_moves, game_result):
        with open("user_data.json", "r") as file:
            user_data = json.load(file)
        users = user_data.get("users", [])
        for u in users:
            if u["name"] == user.name:
                u['games_played'] += 1
                if game_result == 'win':
                    u["wins"] += 1
                    result = 'win'
                elif game_result == 'loss':
                    u["losses"] += 1
                    result = 'loss'
                else:
                    result = 'draw'
                u["blunders"].append(blunders)

                game_id = len(u['game_history']) + 1
                game_elo = u["diff_level"]
                moves = num_moves

                game_data = {
                    "game_id": game_id,
                    "game_elo": game_elo,
                    "moves": moves,
                    "result": result,
                    "blunders": blunders
                }
                u["game_history"].append(game_data)


                #Calculate new averages
                a = 2/(N+1)
                blunder_average = (a * blunders) + (u["blunder_avg"] * (1 - a))
                avg_moves = (a * num_moves) + (u["avg_duration"] * (1 - a))
                #Update averages
                u["blunder_avg"] = blunder_average
                u["avg_duration"] = avg_moves
                break

        with open("user_data.json", "w") as file:
            json.dump(user_data, file, indent=4)
        print("User data updated.")
        return

    def adjust_difficulty(self, user):
        #BLUNDER THRESHOLDS:
        #AT 1100-1300: decrease if > 3, increase if < 2 
        #AT 1400-1600: decrease if > 2, increase if < 1.5
        #AT 1700-1900: decrease if > 1.5, increase if < 1
        #blunder_score = 1 - min(1, avg_blunders / blunder_threshold)

        #GAME DURATION THRESHOLDS:
        # Minimum moves : 30
        # Maximum moves : 60
        # avg_game_duration_score = (avg_moves - min_moves) / (max_moves - min_moves)

        #win_rate = games_won / total_games

        #difficulty_score=(0.4×blunder_score)+(0.4×win_rate)+(0.2×game_duration_score)

        #if difficulty_score≥ 0.75	Increase difficulty (user is performing too well)
        #if difficulty_score≤ 0.40 Decrease difficulty (user is performing poorly)
        #if 0.40 < difficulty_score < 0.75	Maintain difficulty

        #RESET AVERAGES IF ADJUSTING DIFFICULTY
        
        

        with open("user_data.json", "r") as file:
            user_data = json.load(file)

        users = user_data.get("users", [])   
        N = 5 #Adjust every 5 gamesd and Weight the last 5 games more heavily
        for u in users:
            if u["name"] == user.name:
                #check if adjustment is needed
                if u["games_played"] % N == 0 and u["games_played"] != 0:
                    print(f"Adjusting difficulty for {user.name}...")

                    blunder_score = self.get_blunder_score(u["blunder_avg"], u["diff_level"])
                    game_duration_score = (u["avg_duration"] - 30) / (60 - 30)
                    win_rate = u["wins"] / u["games_played"]
                    difficulty_score = (0.4 * blunder_score) + (0.4 * win_rate) + (0.2 * game_duration_score)

                    print(f"Blunder score: {blunder_score}")
                    print(f"Win rate: {win_rate}")
                    print(f"Game duration score: {game_duration_score}")
                    print(f"Difficulty score: {difficulty_score}")

                    if difficulty_score >= 0.75 and u["diff_level"] < 1900:
                        self.increase_difficulty(user)
                    elif difficulty_score <= 0.40 and u["diff_level"] > 800:
                        self.decrease_difficulty(user)
                    else:
                        print("Difficulty level maintained.")
                    break

    def increase_difficulty(self, user):
        with open("user_data.json", "r") as file:
            user_data = json.load(file)

        users = user_data.get("users", [])
        for u in users:
            if u["name"] == user.name:
                diff_level = u["diff_level"]
                while (increase := 
                       input(f"Your current Difficulty is at {diff_level}, Difficulty increase is recommended, would you like to increase? (yes/no): ").lower()) not in {"yes", "no"}: print("Invalid input.")
                if increase == "yes":
                    u["diff_level"] = diff_level + 100
                    print(f"Difficulty level increased to {diff_level + 100} elo.")
                    u["blunder_avg"] = 0
                    u["avg_duration"] = 0
                    u["elo_history"].append(diff_level + 100)
                    with open("user_data.json", "w") as file:
                        json.dump(user_data, file, indent=4)      
                else:
                    print("Difficulty level maintained.")

                break

    def decrease_difficulty(self, user):
        with open("user_data.json", "r") as file:
            user_data = json.load(file)

        users = user_data.get("users", [])
        for u in users:
            if u["name"] == user.name:
                diff_level = u["diff_level"]
                while (decrease := 
                       input(f"Your current Difficulty is at {diff_level} elo, Difficulty decrease is recommended, would you like to decrease? (yes/no): ").lower()) not in {"yes", "no"}: print("Invalid input.")
                if decrease == "yes":
                    u["diff_level"] = diff_level - 100
                    print(f"Difficulty level decreased to {diff_level - 100} elo.")
                    u["blunder_avg"] = 0
                    u["avg_duration"] = 0
                    u["elo_history"].append(diff_level - 100)
                    with open("user_data.json", "w") as file:
                        json.dump(user_data, file, indent=4)      
                else:
                    print("Difficulty level maintained.")
                
                break


    def get_blunder_score(self, blunder_avg, elo):
        # Set upper and lower thresholds based on ELO
        if elo <= 1200:
            lower_bound, upper_bound = 2.0, 3.0
        elif elo <= 1600:
            lower_bound, upper_bound = 1.5, 2.0
        else:
            lower_bound, upper_bound = 1.0, 1.5

        # Normalize blunder score
        if blunder_avg >= upper_bound:
            return 0  # Too many blunders (bad)
        elif blunder_avg <= lower_bound:
            return 1  # Very few blunders (good)
        else:
            return 1 - (blunder_avg - lower_bound) / (upper_bound - lower_bound)  # Scale between 0-1


    def convert_to_pgn(self, board):
        game = chess.pgn.Game()
        node = game
        
        #replay moves stacked in board to pgn game
        for move in board.move_stack:
            node = node.add_variation(move)


        #export to pgn format
        pgn_exporter = chess.pgn.StringExporter()
        game.accept(pgn_exporter)
        #successfully converted to pgn format
        return str(pgn_exporter)



    def user_exists(self, name):
        try:
            with open("user_data.json", "r") as file:
                user_data = json.load(file)
            users = user_data.get("users", [])
            return any(user["name"] == name for user in users)
        except FileNotFoundError:
            return False

if __name__ == "__main__":
    game = AdaptiveGame()
    game.start()