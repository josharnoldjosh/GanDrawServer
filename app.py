from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_manager import GameManager as GM

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=True)

@app.route('/')
def root():
    """ Send HTML from the server."""
    return render_template('index.html')

@app.route('/<email>/<game_id>/<user_type>')
def game(email, game_id, user_type):    

    # TODO: Check if game_id exists with GameManager

    if user_type == "drawer":
        return render_template('drawer.html', game_id=game_id, email=email)
    else:
        return render_template('teller.html', game_id=game_id, email=email)

@socketio.on('join_game')  
def join_game(message):    
    join_room(message['game_id'])

@socketio.on('leave_game')
def leave_game(message):    
    leave_room(message['game_id'])

@socketio.on('get_dialog')  
def get_dialog(message):
    game_id = message['game_id']
    user_type = message['user_type']
    text = GM.get_dialog(game_id, user_type)
    payload = {'text':text, 'game_id':game_id, 'is_drawer_turn':GM.is_drawer_turn(game_id)}
    emit('dialog', payload, broadcast=True, room=game_id)       

@socketio.on('message')   
def message_recieved(message):        
    GM.append_message(message['game_id'], message['text'], message['user_type'])
    GM.toggle_turn(message['game_id'])
    get_dialog(message)

@socketio.on('get_game_data')
def load_target_image_and_label(message):
    game_id = message['game_id']
    images = GM.get_target_image_and_label(game_id)
    emit('game_data', {'images':images, 'game_id':game_id}, broadcast=True, room=game_id)    


if __name__ == '__main__':
    """ Run the app. """    
    socketio.run(app, port=3000, debug=True)