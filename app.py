from flask import * 
from flask_socketio import *
from game_manager import GameManager as GM

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'tmp/'
socketio = SocketIO(app, logger=True)

@app.route('/')
def root():
    """ Send HTML from the server."""
    return render_template('index.html')

@app.route('/<email>/<game_id>/<user_type>', methods = ['GET', 'POST'])
def game(email, game_id, user_type):    
    # TODO: Check if game_id exists with GameManager
    if user_type == "drawer":
        return render_template('drawer.html', game_id=game_id, email=email)
    else:
        return render_template('teller.html', game_id=game_id, email=email)

@app.route('/<game_id>/upload', methods=['POST'])
def upload_drawer_images(game_id):
    if request.method == 'POST' and 'target_image' in request.files and 'target_label' in request.files:           
        if '.jpg' in request.files['target_image'].filename and '.png' in request.files['target_label'].filename:
            target_image = request.files['target_image']
            target_image.save(os.path.join(app.config['UPLOAD_FOLDER'], game_id+'_target_image.jpg'))
            target_label = request.files['target_label']
            target_label.save(os.path.join(app.config['UPLOAD_FOLDER'], game_id+'_target_label.png'))
            # OPTIONAL : Stop user from accidently uploading the same image
            GM.copy_tmp_images(game_id, path=app.config['UPLOAD_FOLDER'])
            GM.toggle(game_id=game_id, flag_name="drawer_uploaded_images", force_true=True)
            return "success"    
    return 'error'

@socketio.on('join_game')  
def join_game(message):    
    join_room(message['game_id'])

@socketio.on('leave_game')
def leave_game(message):    
    leave_room(message['game_id'])

@socketio.on('get_game_data')  
def send_game_data(message):
    game_id = message['game_id']
    user_type = message['user_type']

    text = GM.get_dialog(game_id, user_type)
    is_drawer_turn = GM.is_drawer_turn(game_id)
    drawer_uploaded_images = GM.drawer_uploaded_images(game_id)
    target_image_and_label = GM.get_target_image_and_label(game_id)

    payload = {
    'text':text,
    'game_id':game_id,
    'is_drawer_turn':is_drawer_turn,
    'drawer_uploaded_images':drawer_uploaded_images,
    'target_image_and_label':target_image_and_label
    }

    emit('game_data', payload, broadcast=True, room=game_id)       

@socketio.on('send_message')   
def message_recieved(message):        
    game_id = message['game_id']
    text = message['text']
    user_type = message['user_type']    
    GM.append_message(game_id, text, user_type)
    GM.toggle(game_id=game_id, flag_name="is_drawer_turn")
    if user_type.lower() == "drawer":
        GM.toggle(game_id=game_id, flag_name="drawer_uploaded_images", force_false=True)
    send_game_data(message)

if __name__ == '__main__':
    """ Run the app. """    
    socketio.run(app, port=3000, debug=True)