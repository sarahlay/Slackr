'''
Channel Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
from helper import validate_token, validate_channel, validate_member, validate_user, \
    validate_start, validate_public_channel, validate_permission, \
    get_channel, get_channel_members, get_channel_owners, get_user, get_channel_messages, \
    existing_owner, add_member, set_react_state
from data import get_data

def channel_invite(token, channel_id, u_id):
    '''
    Invites and adds another user to the specified channel.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID of channel to add user to
        u_id (str): user ID of user to add to channel

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)
    u_id = int(u_id)

    # Check for errors
    auth_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(auth_id, channel_id)
    validate_user(u_id)

    # Add member
    add_member(u_id, channel_id)

    return {}

def channel_details(token, channel_id):
    '''
    Provides the channel name, member and owners of the specified channel.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID

    Returns:
        (dict of str: str, str: list): dictionary containing name of channel (str), list of
            owners' user dictionaries and list of members' user dictionaries
    '''
    # Convert inputs into appropriate types
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)

    # Retrieve data
    channel = get_channel(channel_id)

    return {
        'name': channel['name'],
        'all_members': channel['all_members'],
        'owner_members': channel['owner_members']
    }

def channel_messages(token, channel_id, start):
    '''
    Returns up to 50 messages of the specified channel from a start index.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID
        start (int): the index of the first message to be returned

    Returns:
        (dict of str: list, str: int): dictionary containing the relevant messages (list of
            str) and the start and end message indices (int)
    '''
    # Convert input into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)
    validate_start(channel_id, start)

    # Set state of message reacts
    set_react_state(u_id)

    # Get channel messages
    messages = get_channel_messages(channel_id)

    # Store the first 50 messages from the start in a list
    returned_messages = []
    end = start + 50

    i = 0
    while i <= 50:
        try:
            returned_messages.append(messages[i])
        except IndexError:
            end = -1
            break
        i += 1

    return {
        'messages': returned_messages,
        'start': start,
        'end': end
    }

def channel_leave(token, channel_id):
    '''
    Removes a user from the specified channel.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)

    # Remove user from channel members
    members = get_channel_members(channel_id)
    member = next(i for i in members if i['u_id'] == u_id)
    members.remove(member)

    # Remove user for channel owners, if applicable
    owners = get_channel_owners(channel_id)
    owner = next(i for i in owners if i['u_id'] == u_id)
    owners.remove(owner)

    return {}

def channel_join(token, channel_id):
    '''
    Adds a member to the specified public channel.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_public_channel(channel_id)

    # Add member to channel
    add_member(u_id, channel_id)

    return {}

def channel_addowner(token, channel_id, u_id):
    '''
    Promotes the specified member of the channel to owner.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID
        u_id (str): user ID of member to promote

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)
    u_id = int(u_id)

    # Check for errors
    auth_u_id = validate_token(token)
    validate_channel(channel_id)
    validate_user(u_id)
    validate_member(u_id, channel_id)
    existing_owner(u_id, channel_id)
    validate_permission(auth_u_id, channel_id)

    user = get_user('u_id', u_id)

    # Add member to owners of channel
    get_channel_owners(channel_id).append({
        'u_id': user['u_id'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'profile_img_url': user['profile_img_url'],
    })

    # Update user data
    user['channel_ownership'].append({
        'channel_id': channel_id,
        'name': get_data()['channels'][channel_id]['name']
    })

    return {}

def channel_removeowner(token, channel_id, u_id):
    '''
    Demotes the specified owner to member only in the specified channel.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID
        u_id (str): user ID of member to demote

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    # Check for errors
    auth_u_id = validate_token(token)
    validate_channel(channel_id)
    validate_user(u_id)
    validate_permission(auth_u_id, channel_id)

    # Remove user from list of owners
    owners = get_channel_owners(channel_id)
    user = next(i for i in owners if i['u_id'] == u_id)
    owners.remove(user)

    # Remove channel from user's channel_ownership
    user = get_user('u_id', u_id)
    channel = next(i for i in user['channel_ownership'] if i['channel_id'] == channel_id)
    user['channel_ownership'].remove(channel)

    return {}
