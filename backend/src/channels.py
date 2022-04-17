'''
Channels Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
from helper import validate_token, validate_channel_name_size, get_user, added_channel,\
    get_channel_members
from data import get_data, get_id

def channels_create(token, name, is_public):
    '''
    Creates a new channel.

    Parameters:
        token (str): user's authorisation key
        name (str): name of new channel
        is_public (bool): True if channel will be public, False for private

    Returns:
        (dict of str: int): dictionary containing the channel ID (int)

    '''
    # Check for errors
    u_id = validate_token(token)
    validate_channel_name_size(name)

    # Create channel dictionary
    user = get_user('u_id', u_id)
    channels = get_data()['channels']
    channel_id = get_id()['channel_id']

    channels[channel_id] = {
        'name' : name,
        'all_members': [{
            'u_id': user['u_id'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'profile_img_url': user['profile_img_url']
        }],
        'owner_members' :[{
            'u_id': user['u_id'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'profile_img_url': user['profile_img_url']
        }],
        'is_public': is_public,
        'standup': {
            'is_active' : False,
            'time_finish' : None,
            'u_id' : None,
            'messages' : ""
        },
        'hangman': {
            'word': None,
            'display': [],
            'guesses': '',
            'strikes': 0,
            'message': None
        },
    }

    # Update user data structure
    user['channel_membership'].append({
        'channel_id': channel_id,
        'name': name
    })
    user['channel_ownership'].append({
        'channel_id': channel_id,
        'name': name
    })

    # Update message data structure
    get_data()['messages'][int(channel_id)] = []

    # Update channel data structure
    added_channel()

    return {
        'channel_id': channel_id,
    }

def channels_list(token):
    '''
    Provides a list of the channels the user is in.

    Parameters:
        token (str): user's authorisation key

    Returns:
        (dict of str: list): dictionary containing list of channel names (str) and
        IDs (int) stored in dictionaries
    '''
    # Check for errors
    u_id = validate_token(token)

    # Create list to store channel dictionaries
    channel_list = []

    # Append channel details to list if user is a member
    channels = get_data()['channels']
    for channel in channels:
        is_member = next((user for user in channels[channel]['all_members'] \
            if user['u_id'] == u_id), False)
        if is_member:
            channel_list.append({
                'channel_id': channel,
                'name': channels[channel]['name']
            })

    return {'channels': channel_list}

def channels_listall(token):
    '''
    Provides a list of all Slackr channels and their details.

    Parameters:
        token (str): user's authorisation key

    Returns:
        (dict of str: list): dictionary containing list of channel names (str) and
        IDs (int) stored in dictionaries
    '''
    # Check for errors
    u_id = validate_token(token)

    user = get_user('u_id', u_id)

    # Create list to store channel dictionaries
    channel_list = []

    # Append channel details to list
    channels = get_data()['channels']
    for channel in channels:
        members = get_channel_members(channel)
        member = next((i for i in members if i['u_id'] == u_id), False)
        if user['permission_id'] == 1 or channels[channel]['is_public'] or member:
            channel_list.append({
                'channel_id': channel,
                'name': channels[channel]['name']
            })

    return {'channels': channel_list}
