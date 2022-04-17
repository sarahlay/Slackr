'''
Helper Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
import hashlib
import time
import re
from datetime import datetime
from urllib import request
import jwt
from data import get_data, get_id, get_secret, get_hangman_data
from error import InputError, AccessError

#######################################
#           RETRIEVING DATA           #
#######################################

def get_user(key, value):
    '''
    Returns the user dictionary corresponding to the given detail.

    Parameters:
        key (str): the field of the detail
        value (str or int): the detail

    Returns:
        (dict or bool): dictionary of user's data if user exists in system, otherwise false
    '''
    users = get_data()['users']
    return next((user for user in users if user[key] == value), False)


def get_profile(user):
    '''
    Returns a dictionary of relevant user information.

    Parameters:
        user (dict): dictionary of all the user's stored data

    Returns:
        (dict): dictionary containing user's user ID, email, first and last name, and handle
    '''
    return {
        'u_id' : user['u_id'],
        'email' : user['email'],
        'name_first' : user['name_first'],
        'name_last' : user['name_last'],
        'handle_str' : user['handle_str'],
        'profile_img_url' : user['profile_img_url']
    }


def get_channel(channel_id):
    '''
    Returns the channel data of the specifed channel.

    Parameters:
        channel_id (int): channel ID

    Returns:
        (dict): dictionary containing data of channel
    '''
    return get_data()['channels'][channel_id]


def get_channel_members(channel_id):
    '''
    Returns a list of the members in the specified channel.

    Parameters:
        channel_id (int): channel ID

    Returns:
        (list of dict): list of dictionaries containing channel members' user ID (int), first
            and last names (str)
    '''
    return get_channel(channel_id)['all_members']


def get_channel_owners(channel_id):
    '''
    Returns a list of the owners of the specified channel.

    Parameters:
        channel_id (int): channel ID

    Returns:
        (list of dict): list of dictionaries containing channel owners' user ID (int), first
            and last names (str)
    '''
    return get_channel(channel_id)['owner_members']


def get_standup(channel_id):
    '''
    Returns the standup data of the specified channel.

    Parameters:
        channel_id (int): channel ID

    Returns:
        (dict): dictionary containing whether standup is active (bool), end time (int),
            user ID (int) of user who started standup and the standup messages (str)
    '''
    channel_id = int(channel_id)
    standup = get_channel(channel_id)['standup']

    return standup


def get_channel_messages(channel_id):
    '''
    Returns a list of the messages sent in the specified channel.

    Parameters:
        channel_id (int): channel ID

    Returns:
        (list of dict): list of dictionaries containing message ID (int), user ID (int),
            time message was sent (int), message text (str), and pins (bool) and reacts (dict)
    '''
    return get_data()['messages'][channel_id]


def get_message(message_id):
    '''
    Returns the details of a specified message.

    Parameters:
        message_id (int): message ID

    Returns:
        (dict or bool): dictionary of message's data if message exists in system, otherwise false
    '''
    channel_id = get_channel_by_message(message_id)
    messages = get_channel_messages(channel_id)
    return next((i for i in messages if i['message_id'] == message_id), False)


# Returns channel given the message id
def get_channel_by_message(message_id):
    '''
    Returns the channel data of the channel specified by a message. Raises an InputError if the
    message does not exist.

    Parameters:
        message_id (int): message ID

    Returns:
        (dict): dictionary containing data of channel
    '''
    messages = get_data()['messages']
    for channel in messages:
        message = next((i for i in messages[channel] if i['message_id'] == message_id), False)
        if message:
            return channel
    return False


#######################################
#           ERROR FUNCTIONS           #
#######################################

############ ACCESS ERRORS ############
# all functions except auth_register, auth_login
# invalid token

def validate_token(token):
    '''
    Raises an AccessError if the token is not active, otherwise returns the user's user ID.

    Parameters:
        token (str): user's authorisation key

    Returns:
        (int): user's user ID
    '''
    data = get_data()
    secret = get_secret()
    for user in data['users']:
        if token in user['tokens']:
            try:
                decoded = jwt.decode(token, secret, algorithms=['HS256'])
            except:
                raise AccessError(
                    description="Token cannot be decoded. Try logging out and back in again"
                )
            return decoded['u_id']

    # token not valid
    raise AccessError(description="Invalid token")


def validate_member(u_id, channel_id):
    '''
    Raises an AccessError if the user is not a member of the specified channel.

    Parameters:
        u_id (int): user's user ID
        channel_id (int): channel ID
    '''
    members = get_channel_members(channel_id)
    member = next((i for i in members if i['u_id'] == u_id), False)
    if not member:
        raise AccessError(description=f"User {u_id} is not a member of channel {channel_id}")



def validate_slackr_owner(u_id):
    '''
    Raises an AccessError if the user is not an owner of Slackr.

    Parameters:
        u_id (int): user's user ID
    '''
    user = get_user('u_id', u_id)
    if user['permission_id'] != 1:
        raise AccessError(description=f"User {u_id} is not an owner of Slackr")



# Checks if the authorised user is an owner of SLACKR or channel
def validate_permission(u_id, channel_id):
    '''
    Raises an AccessError if the user is not an owner of Slackr of the specified channel.

    Parameters:
        u_id (int): user's user ID
        channel_id (int): channel ID
    '''
    # Checking if owner of slackr
    permission = get_user('u_id', u_id)['permission_id']
    if permission != 1 and not is_owner(u_id, channel_id):
        raise AccessError(
            description=f"User {u_id} is not an owner of slackr or channel {channel_id}"
        )



# Checks if a channel id is public
def validate_public_channel(channel_id):
    '''
    Raises an AccessError if the specified channel is not public.

    Parameters:
        u_id (int): user's user ID
        channel_id (int): channel ID
    '''
    is_public = get_channel(channel_id)['is_public']
    if not is_public:
        raise AccessError(description=f"Channel {channel_id} is a private channel")



############ INPUT ERRORS #############

def validate_email_form(email):
    '''
    Raises an InputError if the given email does not conform with the set regular expression.

    Parameters:
        email (str): email

    '''
    # make a regular expression for validating an email
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    # pass the regualar expression and the string in search() method
    if re.search(regex, email):
        return None
    raise InputError(description="Invalid email")


def validate_email_registered(email):
    '''
    Raises an InputError if the email has not been registered by a user.

    Parameters:
        email (str): email
    '''
    if not is_used('email', email):
        raise InputError(description="Email does not belong to a registered user")



def validate_user(u_id):
    '''
    Raises an InputError if there is no user profile associated with the given user ID.

    Parameters:
        u_id (int): user ID
    '''
    user = get_user('u_id', u_id)
    if not user:
        raise InputError(description="Invalid user")



def validate_channel(channel_id):
    '''
    Raises an InputError if there is no channel associated with the given channel ID.

    Parameters:
        channel_id (int): channel_id
    '''
    channel_id = int(channel_id)
    channels = get_data()['channels']
    is_valid = channels.get(channel_id)
    if is_valid:
        return None
    raise InputError(description="Invalid channel")


# Checks if start is greater than all messages
def validate_start(channel_id, start):
    '''
    Raises an InputError if the given start index is greater than the total number of messages
    in the specified channel.

    Parameters:
        channel_id (int): channel ID
        start (int): index of a channel message
    '''
    total = count_channel_messages(channel_id)
    if total < start:
        raise InputError(description="Start value is greater than total number of messages")



def validate_channel_name_size(name):
    '''
    Raises an InputError if the given channel name exceeds 20 characters.

    Parameters:
        name (str): channel name
    '''
    if len(name) > 20:
        raise InputError(description="Name must be less than 20 characters")


def validate_name_size(name):
    '''
    Raises an InputError if given name exceeds 50 characters.

    Parameters:
        name (str): name
    '''
    if not is_valid_size(name, 1, 50):
        raise InputError(description="Names must be less than 50 characters")


def validate_handle_size(handle_str):
    '''
    Raises an InputError if given handle is not between 3 and 20 characters.

    Parameters:
        handle_str (str): handle
    '''
    if not is_valid_size(handle_str, 3, 20):
        raise InputError(description="Handle must be between 3 and 20 characters long")


def validate_password_size(password):
    '''
    Raises an InputError if the given password is less than 6 characters.

    Parameters:
        password (str): password
    '''
    if len(password) < 6 or len(password) > 50:
        raise InputError(
            description="Password must be at least 6 characters and less than 50 characters"
        )


# Checks that a message is less than 1000 characters
def validate_message_size(message):
    '''
    Raises an InputError if given message exceeds 1000 characters.

    Parameters:
        message (str): message
    '''
    if len(message) >= 1000:
        raise InputError(description="Message exceeds 1000 characters")


def validate_time(time_sent):
    '''
    Raises an InputError if given time has already passed.

    Parameters:
        time_sent (int): unix timestamp
    '''
    time_til_send = time_sent - datetime.now().timestamp()
    if int(time_til_send) < 0:
        raise InputError(description="Invalid time set")


def validate_message(message_id):
    '''
    Raises an InputError if the specified message does not exist in Slackr.

    Parameters:
        message_id (int): message ID
    '''

    messages = get_data()['messages']
    is_exist = False
    for channel in messages:
        is_exist = next((i for i in messages[channel] if i['message_id'] == message_id), False)
        if is_exist:
            return None
    raise InputError(description="Message does not exist")


def validate_react(react_id):
    '''
    Raises an InputError if the given react ID does not have an associated react.

    Parameters:
        react_id (int): react ID
    '''
    if react_id != 1:
        raise InputError(description="Invalid react ID")


# Checks if a user is already an owner
def existing_owner(u_id, channel_id):
    '''
    Raises an InputError if specified user is already an owner of the specified channel.

    Parameters:
        u_id (int): user ID
        channel_id (int): channel ID
    '''
    if is_owner(u_id, channel_id):
        raise InputError(description="User is already an owner")


def check_valid_url(img_url):
    '''
    Raises an InputError if the uploaded image URL returns an error that is not of 200 code.

    Parameters:
        img_url (str): URL of the image
    '''
    try:
        request.urlopen(img_url)
    except Exception as e:
        if type(e) != 200:
            raise InputError(description='Cannot open requested image')


def check_coords(x_start, y_start, x_end, y_end):
    '''
    Raises an InputError if the enterred coordinates exceed the dimensions of the uploaded image.
    Parameters:
        x_start (int): the starting x-coordinate
        y_start (int): the starting y-coordinate
        x_end (int): the ending x-coordinate
        y_end (int): the ending y-coordinate
    '''
    if x_start >= x_end or y_start >= y_end or min(x_start, x_end, y_start, y_end) < 0:
        raise InputError(description="Crop coordinates are not within dimensions of uploaded image")


def check_image_type(img_url):
    '''
    Raises an InputError is the image is not a jpg or jpeg file.

    Parameters:
        img_url (str): URL of the image
    '''
    valid = img_url.lower().endswith(('.jpg', '.jpeg'))
    if not valid:
        raise InputError(description="Uploaded image is not a JPG or JPEG. Try Again.")

def check_coord_type(x_start, y_start, x_end, y_end):
    '''
    Raises an InputError if the coordinates are not valid

    Parameters:
        x_start (int): x start coord
        y_start (int): y start coord
        x_end (int): x end coord
        y_end (int): y end coord
    '''
    if not isinstance(x_start, int):
        raise InputError(description="x_start coordinate must be an integer")
    if not isinstance(y_start, int):
        raise InputError(description="y_start coordinate must be an integer")
    if not isinstance(x_end, int):
        raise InputError(description="x_end coordinate must be an integer")
    if not isinstance(y_end, int):
        raise InputError(description="y_end coordinate must be an integer")

#######################################
#          BOOLEAN FUNCTIONS          #
#######################################

def is_owner(u_id, channel_id):
    '''
    Returns True if the specified user is already an owner of the specified channel,
    otherwise False.

    Parameters:
        u_id (int): user ID
        channel_id (int): channel ID

    Returns:
        (bool): True if user is an owner of the channel, otherwise False
    '''
    owners = get_channel_owners(channel_id)
    owner = next((i for i in owners if i['u_id'] == u_id), False)
    if owner:
        return True
    return False


def is_used(key, value):
    '''
    Returns True if the given value is being used by a Slackr user for the same field.

    Parameters:
        key (str): the field of the detail
        value (str or int): the detail

    Returns:
        (bool): True if the detail is being used by a user, otherwise False
    '''
    users = get_data()['users']
    for user in users:
        if user[key] == value:
            return True
    return False


def is_valid_size(string, min_length, max_length):
    '''
    Returns True if the given string is between the given minimum and maximum nubmer of characters,
    otherwise False.

    Parameters:
        string (str): string
        min_length (int): minimum number of characters
        max_length (int): maximum number of characters

    Returns:
        (bool): True if the length of the string is between the minimum and maximum number of
            characters, otherwise False
    '''
    if len(string) >= min_length and len(string) <= max_length:
        return True
    return False

def is_pinned(message_id):
    '''
    Returns True if the specified message is pinned.

    Parameters:
        message_id (int): message ID

    Returns:
        (bool): True if the message is pinned, otherwise False
    '''
    message = get_message(message_id)
    return message['is_pinned']

def is_reacted(u_id, message_id, react_id):
    '''
    Returns True if the specified user has reacted to the specified message with the specified
    react ID.

    Parameters:
        u_id (int): user ID
        message_id (int): message ID
        react_id (int): react ID

    Returns:
        (bool): True if the user has reacted to the message, otherwise False
    '''
    reacts = next(i for i in get_message(message_id)['reacts'] if i['react_id'] == react_id)
    for i in reacts:
        reacted = next((i for i in reacts['u_ids'] if i == u_id), False)
        if reacted:
            return True
    return False

#######################################
#        OTHER HELPER FUNCTIONS       #
#######################################

def added_message():
    '''
    Increments the global message ID.
    '''
    ID = get_id()
    ID['message_id'] += 1


def added_channel():
    '''
    Increments the global channel ID.
    '''
    ID = get_id()
    ID['channel_id'] += 1


def added_user():
    '''
    Increments the global user ID.
    '''
    ID = get_id()
    ID['user_id'] += 1


def add_member(u_id, channel_id):
    '''
    Adds the specified user to the list of members of the specified channel.

    Parameters:
        u_id (int): user ID
        channel_id (int): channel ID
    '''

    user = get_user('u_id', u_id)
    get_channel_members(channel_id).append({
        'u_id': user['u_id'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'profile_img_url': user['profile_img_url'],
    })
    user['channel_membership'].append({
        'channel_id': channel_id,
        'name': get_data()['channels'][channel_id]['name']
    })


def count_channel_messages(channel_id):
    '''
    Returns the total number of messages in the specified channel.

    Parameters:
        channel_id (int): channel ID
    '''
    messages = get_channel_messages(channel_id)
    return len(messages)


def generate_hash(password):
    '''
    Generates a hash value of the given password and returns it.

    Parameters:
        password (str): password

    Returns:
        (int): hash value of password
    '''
    hashed = hashlib.sha256(str(password).encode('utf-8')).hexdigest()
    return hashed


def generate_token(email, password):
    '''
    Generates a unique token for the user and adds it to their list of active tokens.

    Parameters:
        email (str): user's email
        password (str): user's password

    Returns:
        {u_id, token} (dict of str: int): dictionary containing the user's user ID (int) and new
            token (str)
    '''
    secret = get_secret()
    user = get_user('email', email)

    # encode u_id in token as email can be changed
    u_id = user['u_id']
    information = {
        'u_id': u_id,
        'time': time.time(),
        'password': password
    }
    encoded = jwt.encode(information, secret, algorithm='HS256')
    token = encoded.decode('utf-8')
    user['tokens'].append(token)

    return token


def generate_handle(name_first, name_last, u_id):
    '''
    Generates a unique handle for the specified user based on their first and last name, and
    returns it.

    Parameters:
        name_first (str): user's first name
        name_last (str): user's last name
        u_id (int): user's user ID

    Returns:
        (str): unique handle
    '''
    # handle is concatenation of lowercase first and last
    handle_str = str(name_first).lower() + str(name_last).lower() + str(u_id)

    # handle should not be longer than 20 characters
    if len(handle_str) > 20:
        handle_str = handle_str[:20]

    # add number to end of handle to ensure uniqueness
    number = 1
    while is_used('handle_str', handle_str):
        suffix = str(number)
        if len(handle_str) == 20:
            handle_str = handle_str[:(20 - len(suffix))]
        number += 1

    return handle_str


def set_react_state(u_id):
    '''
    Sends the 'is_this_user_reacted' state of messages given the user id.

    Parameters:
        u_id (int): user's user ID

    Returns:
        None
    '''
    # Setting state of reacts
    messages = get_data()['messages']
    user = get_user('u_id', u_id)
    for channel in user['channel_membership']:
        channel_id = channel['channel_id']
        channel_messages = messages[channel_id]
        for message in channel_messages:
            message_id = message['message_id']
            for react in message['reacts']:
                react['is_this_user_reacted'] = is_reacted(u_id, message_id, react['react_id'])


def send_message(u_id, channel_id, message):
    '''
    Sends a message from the user with u_id to the channel with given channel_id.

    Parameters:
        u_id (int): user's user ID
        channel_id (int): channel ID
        message (str): message

    Returns:
        message_id (int)
    '''
    # Get message for new message and the existing messages in the channel
    message_id = get_id()['message_id']
    messages = get_channel_messages(channel_id)

    # Create new message dictionary
    new_entry = {
        "message_id": message_id,
        "u_id": u_id,
        "message" : message,
        "time_created": int(datetime.now().timestamp()),
        'reacts': [{
            'u_ids': [],
            'is_this_user_reacted': False,
            'react_id': 1
        }],
        "is_pinned": False
    }

    # Send message to appropriate channel
    messages.insert(0, new_entry)
    added_message()

    return message_id


#######################################
#          HANGMAN FUNCTIONS          #
#######################################

def get_channel_hangman(channel_id):
    '''
    Returns the hangman game data of the specified channel.

    Parameters:
        channel_id (int): channel ID

    Returns:
        (dict of str: str, str: int): dictionary containing the game's secret word,
            unhidden letters, guesses, strikes and response message
    '''
    return get_channel(channel_id)['hangman']

def reset_hangman(channel_id):
    '''
    Resets the hangman game in the specified channel.

    Parameters:
        channel_id (int): channel ID

    Returns:
        (dict of str: str, str: int): dictionary containing the game's secret word,
            unhidden letters, guesses, strikes and response message
    '''
    hangman_game = get_channel_hangman(channel_id)
    hangman_game['word'] = None
    hangman_game['display'] = []
    hangman_game['guesses'] = ''
    hangman_game['strikes'] = 0
    hangman_game['message'] = 'Welcome to hangman!'
    return hangman_game

def hangman_send(token, channel_id):
    '''
    Sends a message to the channel showing the progression of the game.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID

    Returns:
        {message_id} (dict of str: int): dictionary containing the message ID (int) of the message
            sent in the channel to show the game's progress
    '''
    u_id = validate_token(token)
    hangman_data = get_hangman_data()
    hangman_game = get_channel_hangman(channel_id)
    strikes = str(hangman_game['strikes'])

    hangman_message = \
        f"{hangman_game['message']}\n",\
        f"{' '.join(hangman_game['display'])}\n",\
        f"{hangman_data[strikes]}\n",\
        f"You have guessed: {' '.join(hangman_game['guesses'])}"

    return {'message_id': send_message(u_id, channel_id, hangman_message)}

def validate_guess(new_guess):
    '''
    Checks the guess is a single letter of the alphabet.

    Parameters:
        new_guess (str): the guess

    Returns:
        new_guess(str): the guess in lowercase

    '''
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    new_guess = new_guess.lower()
    if new_guess not in alphabet or len(new_guess) > 1:
        raise InputError(description='Enter a letter from a to z')
    return new_guess
