from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
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
    if user_type == "drawer":
        return render_template('drawer.html', game_id=game_id)
    else:
        return render_template('teller.html', game_id=game_id)

@socketio.on('get_dialog')  
def get_dialog(message):
    emit('dialog', {
        'text':GM.get_dialog(message['game_id'],
        message['user_type']), 
        'game_id':message['game_id'],
        'is_drawer_turn':GM.is_drawer_turn(message['game_id'])
    }, broadcast=True)       

@socketio.on('message')   
def message_recieved(message):        
    GM.append_message(message['game_id'], message['text'], message['user_type'])
    GM.toggle_turn(message['game_id'])
    get_dialog(message)
    
if __name__ == '__main__':
    """ Run the app. """    
    socketio.run(app, port=3000, debug=True)