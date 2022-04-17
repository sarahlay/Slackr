'''
Auth Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
import random
from helper import validate_email_form, validate_email_registered, validate_password_size, \
    validate_name_size, validate_token, generate_hash, generate_token, generate_handle, \
    is_used, get_user, added_user
from data import get_data, get_id
from error import InputError

def auth_login(email, password):
    '''
    Logs a user into the system and generates an active token for user to remain authenticated.

    Parameters:
        email (str): user's email
        password (str): user's password

    Returns:
        {u_id, token} (dict of str: int, str: str): dictionary containing user's user ID (int)
            and token (str)
    '''
    # InputErrors
    validate_email_form(email)
    validate_email_registered(email)

    user = get_user('email', email)
    password = generate_hash(password)

    # InputError: password is not correct
    if password != user['password']:
        raise InputError(description="Incorrect password")

    token = generate_token(email, password)


    return {
        'u_id': user['u_id'],
        'token': token
    }


def auth_logout(token):
    '''
    Given an active token, invalidates the token to log the user out.

    Parameters:
        token (str): user's authorisation key

    Returns:
        {is_success} (dict of str: bool): dictionary containing boolean of whether user was
            successfully logged out
    '''	# AccessError: token is not a valid token
    u_id = validate_token(token)
    user = get_user('u_id', u_id)
    is_success = False

    # remove token from user's tokens list
    if token in user['tokens']:
        user['tokens'].remove(token)
        is_success = token not in user['tokens']

    return {
        'is_success': is_success
    }


def auth_register(email, password, name_first, name_last):
    '''
    Creates a new account for a user, generates a handle and returns a new token for authentication
    in their session.

    Parameters:
        email (str): new user's email
        password (str): new user's password
        name_first (str): new user's first name
        name_last (str): new user's last name

    Returns:
        {u_id, token} (dict of str: int, str: str): dictionary containing user's user ID (int)
            and token (str)
    '''
    # InputErrors
    validate_email_form(email)
    validate_password_size(password)
    validate_name_size(name_first)
    validate_name_size(name_last)

    # InputError: email is being used by another user
    if is_used('email', email):
        raise InputError(description="Email has already been registered")

    data = get_data()

    # generate user details
    hashed_password = generate_hash(password)
    u_id = get_id()['user_id']
    handle_str = generate_handle(name_first, name_last, u_id)
    permission_id = 2

    # set permission_id of the first user to owner
    if not data['users']:
        permission_id = 1

    user = {
        'name_first': name_first,
        'name_last': name_last,
        'email': email,
        'password': hashed_password,
        'u_id': u_id,
        'handle_str': handle_str,
        'tokens': [],
        'channel_membership': [],
        'channel_ownership' : [],
        'permission_id': permission_id,
        'profile_img_url': None
    }

    added_user()
    data['users'].append(user)

    # login user
    return auth_login(email, password)

def auth_passwordreset_request(email):
    '''
    Sends the user an email containing a reset code.

    Parameters:
        email (str): user's email

    Returns:
        (dict): empty dictionary
    '''
    # For security reasons, we don't want to raise an exception if not valid
    validate_email_form(email)
    if not is_used('email', email):
        return None

    # Reset code is generated from user_id and a random 6 digit string
    user = get_user('email', email)
    reset_code = str(user['u_id']) + str(random.randint(100000, 999999))
    user['reset_code'] = reset_code

    return {}


def auth_passwordreset_reset(reset_code, new_password):
    '''
    Resets a user's password.

    Parameters:
        reset_code (str): user's code to reset password
        new_password (str): user's new password

    Returns:
        (dict): empty dictionary
    '''
    user = False
    for i in get_data()['users']:
        try:
            reset_code = i['reset_code']
            if reset_code == reset_code:
                user = i
                break
        except KeyError as e:
            pass

    if not user:
        raise InputError(description='Invalid reset code')

    validate_password_size(new_password)

    user['password'] = generate_hash(new_password)

    return {}
