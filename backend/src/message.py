'''
Message Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
from time import sleep
from datetime import datetime
from error import InputError, AccessError
from helper import validate_token, validate_channel, validate_member, validate_permission, \
    validate_message, validate_message_size, validate_time, validate_react, \
    get_channel_by_message, get_channel_messages, get_message, is_reacted, is_pinned, send_message
from hangman import hangman, guess

def message_send(token, channel_id, message):
    '''
    Sends a message from the authorised user to the specified channel.

    Parameters:
        token (str): user's authorisation code
        channel_id (int): channel ID specifying channel to send message to
        message (str): message to send

    Returns:
        (dict of str: int): dictionary of message ID (int)
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)
    validate_message_size(message)

    if "/hangman" in message:
        message_id = hangman(token, channel_id)
    elif "/guess " in message:
        letter_idx = message.find("/guess ") + 7
        message_id = guess(token, channel_id, message[letter_idx])
    else:
        message_id = send_message(u_id, channel_id, message)

    return {'message_id': message_id}

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Send a message from the authorised user to the specified channel automatically
    at a specified time in the future.

    Parameters:
        token (str): user's authorisation code
        channel_id (str): channel ID specifying channel to send message to
        message (str): message to send
        time_sent (int): time at which to send message

    Returns:
        (dict of str: int): dictionary of message ID (int)
    '''
    # Converting to appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)
    validate_message_size(message)
    validate_time(time_sent)

    # Sleep until time to send message
    timestamp = float(datetime.now().timestamp())
    sleep(time_sent - timestamp)

    # Send message
    return message_send(token, channel_id, message)

def message_react(token, message_id, react_id):
    '''
    Adds a react from the user to the specified message.

    Parameters:
        token (str): user's authorisation code
        message_id (str): message ID specifying message to react to
        react_id (str): react ID to change message's react to

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    message_id = int(message_id)

    # Check for errors
    u_id = validate_token(token)
    validate_message(message_id)
    validate_react(react_id)

    channel_id = get_channel_by_message(message_id)
    validate_member(u_id, channel_id)

    # InputError: Message has already been reacted to
    if is_reacted(u_id, message_id, 1):
        raise InputError(description="Message has already been reacted")

    # Adding a react
    react = next(i for i in get_message(message_id)['reacts'] if i['react_id'] == react_id)
    react['u_ids'].append(u_id)
    react['is_this_user_reacted'] = True

    return {}

def message_unreact(token, message_id, react_id):
    '''
    Removes the react from the user to the specified message.

    Parameters:
        token (str): user's authorisation code
        message_id (str): message ID specifying message to react to
        react_id (str): react ID to change message's react to

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    message_id = int(message_id)

    # Errors
    u_id = validate_token(token)
    validate_message(message_id)
    validate_react(react_id)

    channel_id = get_channel_by_message(message_id)
    validate_member(u_id, channel_id)

    # InputError: Message hasn't been reacted to
    if not is_reacted(u_id, message_id, 1):
        raise InputError(description="Message has no existing react")

    # Removing a react
    react = next(i for i in get_message(message_id)['reacts'] if i['react_id'] == react_id)
    react['u_ids'].remove(u_id)
    react['is_this_user_reacted'] = False

    return {}

def message_pin(token, message_id):
    '''
    Pins the specified message in a channel.

    Parameters:
        token (str): user's authorisation code
        message_id (str): message ID specifying message to react to

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    message_id = int(message_id)

    # Check for errors
    u_id = validate_token(token)
    validate_message(message_id)

    channel_id = get_channel_by_message(message_id)
    validate_member(u_id, channel_id)
    validate_permission(u_id, channel_id)

    # InputError: Message has already been pinned
    if is_pinned(message_id):
        raise InputError(description="Message is already pinned")

    # Pin message
    message = get_message(message_id)
    message['is_pinned'] = True

    return {}

def message_unpin(token, message_id):
    '''
    Unpins the specified message in a channel.

    Parameters:
        token (str): user's authorisation code
        message_id (str): message ID specifying message to react to

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    message_id = int(message_id)

    # Check for errors
    u_id = validate_token(token)
    validate_message(message_id)

    channel_id = get_channel_by_message(message_id)
    validate_member(u_id, channel_id)
    validate_permission(u_id, channel_id)

    # InputError: Message hasn't been pinned
    if not is_pinned(message_id):
        raise InputError(description="Message is not pinned")

    # Unpin message
    message = get_message(message_id)
    message['is_pinned'] = False

    return {}


def message_remove(token, message_id):
    '''
    Removes a specified message from the channel.

    Parameters:
        token (str): user's authorisation code
        message_id (str): message ID specifying message to react to

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    message_id = int(message_id)

    # Check for errors
    u_id = validate_token(token)
    validate_message(message_id)

    channel_id = get_channel_by_message(message_id)

    message_index = get_message(message_id)
    if message_index['u_id'] != u_id:
        # User is not owner of message
        try:
            # Check user is owner of channel/slackr
            validate_permission(u_id, channel_id)
        except AccessError:
            # If not owner of channel/slackr
            raise AccessError(description="User is not authorised to edit message")

    # Remove message from channel
    get_channel_messages(channel_id).remove(message_index)

    return {}

def message_edit(token, message_id, message):
    '''
    Edits the text of the specified message.

    Parameters:
        token (str): user's authorisation code
        message_id (str): message ID specifying message to react to
        message (str): text to change existing message to

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    message_id = int(message_id)

    # Errors
    u_id = validate_token(token)
    validate_message(message_id)
    validate_message_size(message)

    channel_id = get_channel_by_message(message_id)

    message_index = get_message(message_id)
    if message_index['u_id'] != u_id:
        # User is not owner of message
        try:
            # Check user is owner of channel/slackr
            validate_permission(u_id, channel_id)
        except AccessError:
            # If not owner of channel/slackr
            raise AccessError(description="User is not authorised to edit message")

    # Remove message if no text is given
    if message == '':
        message_remove(token, message_id)

    # Edit message
    else:
        message_index['message'] = message

    return {}
