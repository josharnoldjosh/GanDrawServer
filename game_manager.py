import os
import json

class GameManager:

    @classmethod
    def append_message(self, game_id, text, user_type):
        path = os.path.join('data/games/', game_id, 'dialog.json')
        if not os.path.exists(path): return

        with open(path, 'r') as file:
            dialog = json.load(file)

            turn = {'text':text, 'user_type':user_type, 'turn_idx':len(dialog['dialog'])}
            dialog['dialog'].append(turn)            
        
            with open(path, 'w') as file:
                json.dump(dialog, file)    


    @classmethod
    def get_dialog(self, game_id, user_type):
        path = os.path.join('data/games/', game_id, 'dialog.json')
        if not os.path.exists(path): return "[Error loading data]"

        result = ""

        with open(path, 'r') as file:
            dialog = json.load(file)
            for turn in dialog['dialog']:                
                result += turn['user_type'] + ': ' + turn['text'] + '\n\n'            
            return result

        return result

    @classmethod
    def toggle_turn(self, game_id):
        flags_path = os.path.join('data/games/', game_id, 'flags.json')

        with open(flags_path, 'r') as file:
            flags = json.load(file)

            flags["is_drawer_turn"] = not flags["is_drawer_turn"]
            print("opened")

            with open(flags_path, 'w') as file:
                json.dump(flags, file)
                print("dumpped")
        return

    @classmethod
    def is_drawer_turn(self, game_id):
        path = os.path.join('data/games/', game_id, 'flags.json')
        if not os.path.exists(path): print("Error loading flags for game", game_id)

        with open(path, 'r') as file:
            flags = json.load(file)
            return flags["is_drawer_turn"]
        