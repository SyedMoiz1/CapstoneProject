import json


    #   Combine multiple metrics into a formula or weighted system 
    #   -Win/Loss Rate (40%)
    #   -Blunder rate (40%)
    #   -Game Duration (20%)

    #   after every 5 games, recalculate the rolling average
    #   blunder_avg=α×new_blunder_rate+(1−α)×blunder_avg
    #   game_duration_avg=α×new_game_duration+(1−α)×game_duration_avg
    #   Where α (alpha) is the weighting factor, typically set as:
    #       α=2/(N+1)
    #       If you want the last 5 games to be weighted more then: α=2/(5+1)=0.33
class User:
    def __init__(self, name, new_user=False, diff_level=None):
        #name
        self.name = name.lower()
        #currently difficulty level 1->1100 5->1500 9->1900
        self.diff_level = None
        self.elo_history = []
        self.games_played = None
        self.game_history = []
        self.wins = 0
        self.losses = 0
        self.blunders = []
        self.avg_duration = None
        
        #initialize the user 
        if new_user == False:
            self.initializeExistingUser()
        else:
            self.diff_level = diff_level
            self.initializeNewUser()

    def initializeNewUser(self):
        new_user_data = {
            "name": self.name,
            "diff_level": self.diff_level,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "blunders": [],
            "blunder_avg": 0,
            "avg_duration": 0,
            "elo_history": [self.diff_level],
            "game_history": []
        }
        try:
            with open("user_data.json", "r") as file:
                user_data = json.load(file)
        except FileNotFoundError:
            user_data = {"users": []}

        user_data["users"].append(new_user_data)
        with open("user_data.json", "w") as file:
            json.dump(user_data, file, indent=4)     


    def initializeExistingUser(self):
        with open("user_data.json", "r") as file:
            user_data = json.load(file)
        users = user_data["users"]
        for user in users:
            if user["name"] == self.name:
                self.diff_level = user["diff_level"]
                self.games_played = user["games_played"]
                self.game_history = user["game_history"]
                self.wins = user["wins"]
                self.losses = user["losses"]
                self.blunders = user["blunders"]
                self.avg_duration = user["avg_duration"]
                self.elo_history = user["elo_history"]
                break
        print(self.diff_level)


if __name__ == "__main__":
    user = User("Syed")
    print(user.name)
    print(user.diff_level)
    print(user.games_played)
    print(user.game_history)
    print(user.wins)
    print(user.losses)
    print(user.blunders)
    print(user.avg_duration)
    print(user.elo_history)
        
        