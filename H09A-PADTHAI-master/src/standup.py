'''
Standup Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
from datetime import datetime
from helper import validate_token, validate_channel, validate_member, validate_message_size, \
    get_standup, get_user, send_message
from error import InputError

def standup_start(token, channel_id, length):
    '''
    Starts a standup in the specified channel.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID of channel to start standup in
        length (int): the time duration of the standup, in seconds

    Returns:
        (dict of str: int): dictionary containing the finish time of the standup
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)

    # InputError: Standup is already active in the channel
    standup = get_standup(channel_id)
    if standup['is_active']:
        raise InputError(description="Standup is already active in this channel")

    # Calculate finish time
    time_finish = int(datetime.now().timestamp() + length)

    # Activate standup
    standup['u_id'] = u_id
    standup['is_active'] = True
    standup['time_finish'] = time_finish

    return {'time_finish' : standup['time_finish']}


def standup_active(token, channel_id):
    '''
    Returns whether a standup is active in the specified channel and what time the
    standup finishes.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID of channel

    Returns:
        (dict of str: bool, str: int): dictionary containing the whether the standup
            is active (bool) and the finish time (int) of the standup
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)

    # Get standup data
    standup = get_standup(channel_id)

    # If message isnt sent yet, send message at correct time and reinitialise parameters
    standup_message_send(standup, channel_id)

    return {
        'is_active' : standup['is_active'],
        'time_finish' : standup['time_finish']
    }

def standup_send(token, channel_id, message):
    '''
    Sends a message to get buffered in the standup queue, assuming the standup is active.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID of channel to send standup message in
        message (str): new standup message

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)
    validate_message_size(message)

    standup = get_standup(channel_id)

    # InputError: Standup is not currently active running in this channel
    if not standup['is_active']:
        raise InputError(description="No currently active standup in this channel")

    # Add new message to list of buffered messages
    user = get_user('u_id', u_id)
    new_standup_message = f"{user['handle_str']}: {message}\n"

    # Create a message to be sent at the end of the standup
    standup['messages'] += new_standup_message

    # Send message at correct time and reinitialise parameters
    standup_message_send(standup, channel_id)

    return {}

def standup_message_send(standup, channel_id):
    '''
    Sends the standup bundled message into the specified channel at the given time.

    Parameters:
        channel_id (int): channel ID
        standup (dict): a dictionary containing is_active, time_finish, u_id and messages

    Returns:
        {message_id} (dict of str: int): dictionary of message ID (int)
    '''
    current_time = int(datetime.now().timestamp())
    if standup['is_active'] and standup['time_finish'] <= current_time:
        standup_token = get_user('u_id', standup['u_id'])['tokens'][-1]
        u_id = validate_token(standup_token)
        send_message(u_id, channel_id, standup['messages'])
        standup['is_active'] = False
        standup['time_finish'] = None
        standup['u_id'] = None
        standup['messages'] = ""
