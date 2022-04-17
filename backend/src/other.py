'''
Other Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
import pickle
from data import get_data, get_id
from helper import get_user, get_profile, validate_user, validate_token,\
    validate_slackr_owner, is_reacted, get_channel_messages
from error import AccessError, InputError

def users_all(token):
    '''
    Returns a list of all users and their associated details.
    Parameters:
        token (str): user's authorisation code

    Returns:
        (dict of str: list): dictionary of list of user dictionaries
    '''
    # Check for errors
    validate_token(token)

    # Create list to store user profiles
    data = get_data()
    users = []

    # Append only relevant user data to the list
    for user in data['users']:
        users.append(get_profile(user))

    return {'users': users}

def search(token, query_str):
    '''
    Returns a collection of messages in all the channels the user is a member
    of that match the query string.

    Parameters:
        token (str): user's authorisation code
        query_str (str): query string to search messages

    Returns:
        (dict of str: list): dictionary of list of messages (str) that contain
            query string
    '''
    u_id = validate_token(token)

    data = get_data()
    user = get_user('u_id', u_id)
    search_return = {'messages': []}

    for channel in user['channel_membership']:
        channel_id = channel['channel_id']
        messages = data['messages'][channel_id]
        for message in messages:
            if query_str in message['message']:
                search_return['messages'].append(message)

    return search_return

def workplace_reset():
    '''
    Resets the workplace state by resetting data structure.

    Returns:
        (dict): empty dictionary
    '''
    # Clear data structure
    data = get_data()
    data['users'] = []
    data['channels'] = {}
    data['messages'] = {}
    with open('data_file.pickle', 'wb') as data_file:
        pickle.dump(data, data_file)

    # Clear ID data structure
    ids = get_id()
    ids['message_id'] = 1
    ids['channel_id'] = 1
    ids['user_id'] = 1
    with open('id_file.pickle', 'wb') as id_file:
        pickle.dump(ids, id_file)

    return {}


#########################################
# 		    Admin Functions     		#
#########################################

def admin_user_remove(token, u_id):
    '''
    Given a user by their user ID, removes the user from Slackr.

    Parameters:
        token (str): user's authorisation code
        u_id (str): user ID of user to be removed

    Returns:
        (dict): empty dicitonary
    '''
    # Convert inputs into appropriate type
    u_id = int(u_id)

    # Check for errors
    validate_user(u_id)
    auth_u_id = validate_token(token)

    # AccessError: authorised user is not an owner of slackr
    auth_user = get_user('u_id', auth_u_id)
    if auth_user['permission_id'] != 1:
        raise AccessError(description="You are not authorised to remove users")

    # Update reacts data
    user = get_user('u_id', u_id)
    for channel in user['channel_membership']:
        channel_id = channel['channel_id']
        messages = get_channel_messages(channel_id)
        for msg in messages:
            for react in msg['reacts']:
                if is_reacted(u_id, msg['message_id'], 1):
                    react['u_ids'].remove(user['u_id'])

    # Update channels data
    data = get_data()
    for channel in user['channel_membership']:
        members = data['channels'][channel['channel_id']]['all_members']
        member = next(i for i in members if i['u_id'] == u_id)
        members.remove(member)

    for channel in user['channel_ownership']:
        owners = data['channels'][channel['channel_id']]['owner_members']
        owner = next(i for i in owners if i['u_id'] == u_id)
        owners.remove(owner)

    # Update users data
    data['users'].remove(user)

    return {}

def admin_userpermission_change(token, u_id, permission_id):
    '''
    Given a user by their ID, change their permissions.

    Parameters:
        token (str): user's authorisation key
        u_id (str): user ID of user to change permission of
        permission_id (str): permission ID to change user's permission to

    Returns:
        (dict): empty dictionary
    '''
    # Convert inputs into appropriate type
    u_id = int(u_id)
    permission_id = int(permission_id)

    # Check for errors
    auth_u_id = validate_token(token)
    validate_user(u_id)
    validate_slackr_owner(auth_u_id)

    # InputError: permission_id does not refer to a value permission
    if permission_id not in (1, 2):
        raise InputError(description="Invalid permission ID")

    # InputError: owners cannot change their own permissions
    if auth_u_id == u_id:
        raise InputError(description="Owners cannot change their own permissions")

    # Change user's permission
    user = get_user('u_id', u_id)
    user['permission_id'] = permission_id

    return {}
