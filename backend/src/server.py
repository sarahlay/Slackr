'''
Flask Server
By H09A-PADTHAI
Submitted 19 April 2020
'''
import sys
import threading
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from flask_mail import Mail, Message
from data import get_data, pickle_data
from helper import get_user
from error import InputError
import auth
import channel
import channels
import message
import user
import standup
import other

def default_handler(err):
    '''
    Handles the errors to display on the frontend
    '''
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)

APP.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='padthai20t1@gmail.com',
    MAIL_PASSWORD="Padthai666"
)

# Reset function
@APP.route('/workspace/reset', methods=['POST', 'GET'])
def reset():
    '''
    Resets data
    '''
    other.workplace_reset()
    return dumps({})

@APP.route('/getdata', methods=['GET'])
def getdata():
    '''
    Returns data
    '''
    payload = get_data()
    return dumps(payload)

###############
# Auth Routes #
###############

@APP.route('/auth/login', methods=['POST'])
def login():
    '''
    Logs in a user
    given their email and password
    '''
    data = request.get_json('data')
    payload = auth.auth_login(
        data['email'],
        data['password']
    )
    return dumps(payload)

@APP.route('/auth/logout', methods=['POST'])
def logout():
    '''
    Logs out a user
    given their token
    '''
    data = request.get_json('data')
    payload = auth.auth_logout(
        data['token']
    )
    return dumps(payload)

@APP.route('/auth/register', methods=['POST'])
def register():
    '''
    Registers a user
    given their email, password, firstname and lastname
    '''
    data = request.get_json('data')
    payload = auth.auth_register(
        data['email'],
        data['password'],
        data['name_first'],
        data['name_last']
    )
    return dumps(payload)

@APP.route('/auth/passwordreset/request', methods=['POST'])
def password_request():
    '''
    Generates a password reset code for a user and emails it to them
    given an email
    '''
    data = request.get_json('data')
    payload = auth.auth_passwordreset_request(
        data['email']
    )
    email = data['email']
    reset_code = get_user('email', email)['reset_code']

    # Only send email if it belongs to a user
    if reset_code is not None:
        mail = Mail(APP)
        msg = Message(
            "Slackr password reset",
            sender="padthai20t1@gmail.com",
            recipients=[email]
        )
        msg.body = "Your password reset code for Slackr is: " + reset_code
        mail.send(msg)

    return dumps(payload)

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def password_reset():
    '''
    Resets a user's password
    given the reset code
    '''
    data = request.get_json('data')
    payload = auth.auth_passwordreset_reset(
        data['reset_code'],
        data['new_password']
    )
    return dumps(payload)


##################
# Channel Routes #
##################

@APP.route('/channel/invite', methods=['POST'])
def invite():
    '''
    Invites a user to a channel
    given a token, channel_id and user_id
    '''
    data = request.get_json('data')
    payload = channel.channel_invite(
        data['token'],
        data['channel_id'],
        data['u_id']
    )
    return dumps(payload)

@APP.route('/channel/details', methods=['GET'])
def details():
    '''
    Returns channel details
    given a token and a channel_id
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    payload = channel.channel_details(token, channel_id)
    return dumps(payload)

@APP.route('/channel/messages', methods=['GET'])
def get_channel_messages():
    '''
    Returns channel messages
    given a token, channel_id and start
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start_val = int(request.args.get('start'))
    payload = channel.channel_messages(token, channel_id, start_val)
    return dumps(payload)

@APP.route('/channel/leave', methods=['POST'])
def leave():
    '''
    Removes a user from a channel
    given a token and a channel_id
    '''
    data = request.get_json('data')
    payload = channel.channel_leave(
        data['token'],
        data['channel_id']
    )
    return dumps(payload)

@APP.route('/channel/join', methods=['POST'])
def join():
    '''
    Adds a user to a channel
    given a token and a channel_id
    '''
    data = request.get_json('data')
    payload = channel.channel_join(
        data['token'],
        data['channel_id']
    )
    return dumps(payload)

@APP.route('/channel/addowner', methods=['POST'])
def add_owner():
    '''
    Adds an owner to a channel
    given a token, channel_id and user_id
    '''
    data = request.get_json('data')
    payload = channel.channel_addowner(
        data['token'],
        data['channel_id'],
        data['u_id']
    )
    return dumps(payload)

@APP.route('/channel/removeowner', methods=['POST'])
def remove_owner():
    '''
    Removes an owner from a channel
    given a token, channel_id and user_id
    '''
    data = request.get_json('data')
    payload = channel.channel_removeowner(
        data['token'],
        data['channel_id'],
        data['u_id']
    )
    return dumps(payload)

###################
# Channels Routes #
###################

@APP.route('/channels/list', methods=['GET'])
def list_channels():
    '''
    Returns a list of channels that the user is a part of
    given a token
    '''
    token = request.args.get('token')
    payload = channels.channels_list(token)
    return dumps(payload)

@APP.route('/channels/listall', methods=['GET'])
def list_all_channels():
    '''
    Returns a list of all public channels given a token
    '''
    token = request.args.get('token')
    payload = channels.channels_listall(token)
    return dumps(payload)

@APP.route('/channels/create', methods=['POST'])
def create_channels():
    '''
    Creates a new channel
    given a token, name and public/private booleon
    '''
    data = request.get_json('data')
    payload = channels.channels_create(
        data['token'],
        data['name'],
        data['is_public']
    )
    return dumps(payload)

##################
# Message Routes #
##################

@APP.route('/message/send', methods=['POST'])
def send():
    '''
    Sends a message to a channel
    given a token, channel_id and message
    '''
    data = request.get_json('data')
    payload = message.message_send(
        data['token'],
        data['channel_id'],
        data['message']
    )
    return dumps(payload)

@APP.route('/message/sendlater', methods=['POST'])
def send_later():
    '''
    Sends a delayed message to a channel
    given a token, channel_id, message and time_sent
    '''
    data = request.get_json('data')
    payload = message.message_sendlater(
        data['token'],
        data['channel_id'],
        data['message'],
        data['time_sent']
    )
    return dumps(payload)

@APP.route('/message/react', methods=['POST'])
def react():
    '''
    User reacts to a message
    given a token, message_id and react_id
    '''
    data = request.get_json('data')
    payload = message.message_react(
        data['token'],
        data['message_id'],
        data['react_id']
    )
    return dumps(payload)

@APP.route('/message/unreact', methods=['POST'])
def unreact():
    '''
    User unreacts to a message
    given a token, message_id and react_id
    '''
    data = request.get_json('data')
    payload = message.message_unreact(
        data['token'],
        data['message_id'],
        data['react_id']
    )
    return dumps(payload)

@APP.route('/message/pin', methods=['POST'])
def pin():
    '''
    User pins a message
    given a token and message_id
    '''
    data = request.get_json('data')
    payload = message.message_pin(
        data['token'],
        data['message_id']
    )
    return dumps(payload)

@APP.route('/message/unpin', methods=['POST'])
def unpin():
    '''
    User unpins a message
    given a token and message_id
    '''
    data = request.get_json('data')
    payload = message.message_unpin(
        data['token'],
        data['message_id']
    )
    return dumps(payload)

@APP.route('/message/remove', methods=['DELETE'])
def remove():
    '''
    User removes a message
    given a token and message_id
    '''
    data = request.get_json('data')
    payload = message.message_remove(
        data['token'],
        data['message_id']
    )
    return dumps(payload)

@APP.route('/message/edit', methods=['PUT'])
def edit():
    '''
    User edits a message
    given a token, message_id and new message
    '''
    data = request.get_json('data')
    payload = message.message_edit(
        data['token'],
        data['message_id'],
        data['message']
    )
    return dumps(payload)

###############
# User Routes #
###############

@APP.route('/user/profile', methods=['GET'])
def profile():
    '''
    Returns a user's profile
    given a token & user_id
    '''
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    payload = user.user_profile(token, u_id)
    return dumps(payload)

@APP.route('/user/profile/setname', methods=['PUT'])
def set_name():
    '''
    Sets a new name for a user
    given a token, new firstname and new lastname
    '''
    data = request.get_json('data')
    payload = user.user_profile_setname(
        data['token'],
        data['name_first'],
        data['name_last']
    )
    return dumps(payload)

@APP.route('/user/profile/setemail', methods=['PUT'])
def set_email():
    '''
    Sets a new email for a user given a token and new email
    '''
    data = request.get_json('data')
    payload = user.user_profile_setemail(
        data['token'],
        data['email']
    )
    return dumps(payload)

@APP.route('/user/profile/sethandle', methods=['PUT'])
def set_handle():
    '''
    Sets a new handle for a user given a token and new handle
    '''
    data = request.get_json('data')
    payload = user.user_profile_sethandle(
        data['token'],
        data['handle_str']
    )
    return dumps(payload)

@APP.route('/user/profile/uploadphoto', methods=['POST'])
def upload_photo():
    '''
    Uploads a photo for the user
    '''
    data = request.get_json('data')
    try:
        payload = user.user_profile_uploadphoto(
            data['token'],
            data['img_url'],
            data['x_start'],
            data['y_start'],
            data['x_end'],
            data['y_end']
        )
    except KeyError:
        raise InputError("Invalid Input")
    return dumps(payload)


#################
# Search Routes #
#################

@APP.route('/search', methods=['GET'])
def new_search():
    '''
    Returns a list of messages contains the query string
    given a token and a query string
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    payload = other.search(token, query_str)
    return dumps(payload)

##################
# Standup Routes #
##################

@APP.route('/standup/start', methods=['POST'])
def start():
    '''
    Starts a standup in the channel with channel_id
    given a token, channel_id and length of standup
    '''
    data = request.get_json('data')
    payload = standup.standup_start(
        data['token'],
        data['channel_id'],
        data['length']
    )
    return dumps(payload)

@APP.route('/standup/active', methods=['GET'])
def active():
    '''
    Returns if a standup is active on a channel
    given a token and a channel_id
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    payload = standup.standup_active(token, channel_id)
    return dumps(payload)

@APP.route('/standup/send', methods=['POST'])
def post():
    '''
    Sends a message to a standup
    given a token, channel_id and message
    '''
    data = request.get_json('data')
    payload = standup.standup_send(
        data['token'],
        data['channel_id'],
        data['message']
    )
    return dumps(payload)

################
# Other Routes #
################

@APP.route('/users/all', methods=['GET'])
def get_all():
    '''
    Returns a list of all users
    given a token
    '''
    token = request.args.get('token')
    payload = other.users_all(token)
    return dumps(payload)

@APP.route('/admin/userpermission/change', methods=['POST'])
def userpermission_change():
    '''
    Sets a new userpermission
    given a token, user_id and permission_id
    '''
    data = request.get_json('data')
    payload = other.admin_userpermission_change(
        data['token'],
        data['u_id'],
        data['permission_id']
    )
    return dumps(payload)

@APP.route('/admin/user/remove', methods=['DELETE'])
def user_remove():
    '''
    Removes a user
    given a token and user_id
    '''
    data = request.get_json('data')
    payload = other.admin_user_remove(
        data['token'],
        data['u_id']
    )
    return dumps(payload)

def app_run():
    '''
    Runs the Flask App
    '''
    APP.run(port=int(sys.argv[1]) if len(sys.argv) == 2 else 8080)

if __name__ == "__main__":
    try:
        threading.Thread(target=app_run).start()
        threading.Thread(target=pickle_data, daemon=True).start()
    except KeyboardInterrupt:
        sys.exit()
