'''
Data
By H09A-PADTHAI
Submitted 19 April 2020

DATA STRUCTURE
DATA = {
    'users' : [] 	# list of user dictionaries
    'channels' : {} # dictionary of channel dictionaries
    'messages' : {}	# dictionary of message dictionaries
}


USERS
[{
    'name_first': first,
    'name_last': last,
    'email': email,
    'password': password,
    'u_id': u_id,
    'handle_str': handle_str,
    'token': token,
    'channel_membership': [{
        'channel_id': channel_id
        'name': channel name
    }],
    'channel_ownership' : [],
    'permission_id': permission_id,
    'profile_img_url': profile_img_url,
}]

CHANNELS
{
    channel_id : {
        'name': channelname,
        'all_members': [{
            'u_id': u_id
            'name_first': firstname,
            'name_last': lastname
            'profile_img_url': profile_img_url,
        }],
        'owner_members': [{
            'u_id': u_id
            'name_first': firstname,
            'name_last': lastname
            'profile_img_url': profile_img_url,
        }],
        'is_public' : is_public,
        'standup': {
            'is_active' : False,
            'time_finish' : None,
            'u_id' : None,
            'messages' : ""
        }
        'hangman': {
            'word': None,
            'display': [],
            'guesses': '',
            'strikes': 0,
            'message': None
        },
    },
}

MESSAGES
{
    channel_id : [{
        'message_id': MESSAGE,
        'u_id': u_id,
        'message' : message,
        'time_created': unix timestamp,
        'reacts': [{
            'u_ids': [u_ids],
            'is_this_user_reacted': True/False,
            'react_id': react_id
        }]
        'is_pinned' : False
    }]
}
'''
import pickle
from time import sleep

with open("data_file.pickle", "rb") as FILE:
    DATA = pickle.load(FILE)

with open("id_file.pickle", "rb") as FILE:
    ID = pickle.load(FILE)

SECRET = 'oursecret'
DATASTORE_INTERVAL = 5

def get_data():
    '''
    Creates and returns global variable for data structure.
    '''
    global DATA
    return DATA

def get_id():
    '''
    Creates and returns global variable for id's.
    '''
    global ID
    return ID

def get_secret():
    '''
    Creates and returns global variable for secret.
    '''
    global SECRET
    return SECRET

def pickle_data():
    '''
    Dumps the data and ID structures in pickle format.
    '''
    try:
        while True:
            sleep(DATASTORE_INTERVAL)
            DATA = get_data()
            with open('data_file.pickle', 'wb') as FILE:
                pickle.dump(DATA, FILE)

            ID = get_id()
            with open('id_file.pickle', 'wb') as FILE:
                pickle.dump(ID, FILE)
    except EOFError:
        return None

HANGMAN_DATA = {
    '0': '''===========''',
    '1': '''===========
|
|
|
|
|''',
    '2': '''===========
| /
|/
|
|
|''',
    '3': '''===========
| /       |
|/
|
|
|''',
    '4': '''===========
| /       |
|/        O
|
|
|''',
    '5': '''===========
| /       |
|/        O
|         |
|
|''',
    '6': '''===========
| /       |
|/        O
|        /|
|
|''',
    '7': '''===========
| /       |
|/        O
|        /|\\
|
|''',
    '8': '''===========
| /       |
|/        O
|        /|\\
|        /
|''',
    '9': '''===========
| /       |
|/        O
|        /|\\
|        / \\
|''',
}

def get_hangman_data():
    '''
    Creates and returns the global variable of hangman data.
    '''
    global HANGMAN_DATA
    return HANGMAN_DATA
