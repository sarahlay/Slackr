'''
Auth Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
import pytest
from auth import auth_register, auth_logout, auth_login, auth_passwordreset_request, \
    auth_passwordreset_reset
from data import get_data
from helper import generate_hash, get_user
from other import workplace_reset
from error import AccessError, InputError

INVALID = 1024

#######################################
#            AUTH REGISTER            #
#######################################

def test_auth_register_valid():
    '''
    Tests auth_register for valid cases.
    '''
    # Reset all data
    workplace_reset()

    # Call function
    user1 = auth_register('hpotter@hogwarts.com', 'Quidditch', 'Harry', 'Potter')
    user2 = auth_register('rweasley@hogwarts.com', 'ChuddleyCannons', 'Ronald', 'Weasley')

    # Check tokens are unique
    assert user1['token'] != user2['token']

    # Check data structure
    data = get_data()
    assert data['users'][0] == {
        'name_first': 'Harry',
        'name_last': 'Potter',
        'email': 'hpotter@hogwarts.com',
        'password': generate_hash('Quidditch'),
        'u_id': 1,
        'handle_str': 'harrypotter1',
        'tokens': [user1['token']],
        'channel_membership': [],
        'channel_ownership' : [],
        'permission_id': 1,
        'profile_img_url': None
    }

    assert data['users'][1] == {
        'name_first': 'Ronald',
        'name_last': 'Weasley',
        'email': 'rweasley@hogwarts.com',
        'password': generate_hash('ChuddleyCannons'),
        'u_id': 2,
        'handle_str': 'ronaldweasley2',
        'tokens': [user2['token']],
        'channel_membership': [],
        'channel_ownership' : [],
        'permission_id': 2,
        'profile_img_url': None
    }

def test_auth_register_invalid():
    '''
    Tests auth_register for simple invalid cases.
    '''
    # Reset all data
    workplace_reset()

    # InputError: empty email
    with pytest.raises(InputError):
        auth_register('', 'Quidditch', 'Harry', 'Potter')

    # InputError: invalid email format
    with pytest.raises(InputError):
        auth_register('hpotter', 'Quidditch', 'Harry', 'Potter')

    # InputError: password is less than 6 characters
    with pytest.raises(InputError):
        auth_register('rweasley@hogwarts.com', 'RW', 'Ronald', 'Weasley')

   # InputError: password exceeds 50 characters
    with pytest.raises(InputError):
        auth_register('rweasley@hogwarts.com', 'ChuddleyCannons' * 50, 'Ronald', 'Weasley')

    # InputError: empty first name
    with pytest.raises(InputError):
        auth_register('rweasley@hogwarts.com', 'ChuddleyCannons', '', 'Weasley')

    # InputError: first name exceeds 50 characters
    with pytest.raises(InputError):
        auth_register('rweasley@hogwarts.com', 'ChuddleyCannons', 'Ronald' * 50, 'Weasley')

    # InputError: empty last name
    with pytest.raises(InputError):
        auth_register('rweasley@hogwarts.com', 'ChuddleyCannons', 'Ronald', '')

    # InputError: last name exceeds 50 characters
    with pytest.raises(InputError):
        auth_register('rweasley@hogwarts.com', 'ChuddleyCannons', 'Ronald', 'Weasley' * 50)

def test_auth_register_invalid_email():
    '''
    Tests auth_register for the case when an email is already in use.
    '''
    # InputError: email already used by another user
    user1 = auth_register('hpotter@hogwarts.com', 'Quidditch', 'Harry', 'Potter')
    user_data1 = get_user('u_id', user1['u_id'])
    with pytest.raises(InputError):
        auth_register(user_data1['email'], 'ChuddleyCannons', 'Ronald', 'Weasley')


#######################################
#              AUTH LOGOUT            #
#######################################

def test_auth_logout_valid():
    '''
    Tests auth_logout for valid cases.
    '''
    # Reset all data and register (and login) users
    workplace_reset()
    user = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')

    logout = auth_logout(user['token'])

    # Check return value of function
    assert logout['is_success']

    # Check token has been removed from data structure
    user_data = get_user('u_id', user['u_id'])
    assert user_data['tokens'] == []

def test_auth_logout_invalid():
    '''
    Tests auth_logout for invalid cases.
    '''
    # Reset all data and register (and login) users
    workplace_reset()
    auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')

    # AccessError: invalid token
    with pytest.raises(AccessError):
        auth_logout(INVALID)


#######################################
#             AUTH LOGIN              #
#######################################

def test_auth_login_valid():
    '''
    Tests auth_login for valid cases.
    '''
    # Reset all data and register and logout user
    workplace_reset()
    user = auth_register('hgranger@hogwarts.com', 'Crookshanks', 'Hermione', 'Granger')
    auth_logout(user['token'])

    # Call function
    user = auth_login('hgranger@hogwarts.com', 'Crookshanks')

    # Check return values of function
    assert user['u_id'] == 1
    assert user['token']

    # Check data structure for active token
    user_data = get_user('u_id', user['u_id'])
    assert user_data['tokens'] == [user['token']]

def test_auth_login_invalid():
    '''
    Tests auth_login for invalid cases.
    '''
    # Reset all data and register and logout user
    workplace_reset()
    user = auth_register('hgranger@hogwarts.com', 'Crookshanks', 'Hermione', 'Granger')
    auth_logout(user['token'])

    # InputError: invalid email format
    with pytest.raises(InputError):
        auth_login('hgranger', 'Crookshanks')

    # InputError: email is not registered
    with pytest.raises(InputError):
        auth_login('hermione@hogwarts.com', 'Crookshanks')

    # InputError: incorrect password
    with pytest.raises(InputError):
        auth_login('hgranger@hogwarts.com', 'Arithmancy')


#######################################
#      AUTH PASSWORDRESET REQUEST     #
#######################################

def test_auth_passwordreset_request_valid():
    '''
    Tests auth_passwordreset_request for valid cases.
    '''
    # Reset all data and register user
    workplace_reset()
    user = auth_register('nlongbottom@hogwarts.com', 'Remembrall', 'Neville', 'Longbottom')

    # Call function
    request = auth_passwordreset_request('nlongbottom@hogwarts.com')

    # Check return value of function
    assert request == {}

    # Check data structure for reset code
    user_data = get_user('u_id', user['u_id'])
    assert isinstance(user_data['reset_code'], str)

def test_auth_passwordreset_request_invalid():
    '''
    Tests auth_passwordreset_request for invalid cases.
    '''
    # Reset all data and register and logout user
    workplace_reset()
    auth_register('nlongbottom@hogwarts.com', 'Remembrall', 'Neville', 'Longbottom')

    # InputError: invalid email format
    with pytest.raises(InputError):
        auth_passwordreset_request('nlongbottom')

    # Check nothing is returned if email is not registered
    assert not auth_passwordreset_request('neville@hogwarts.com')


#######################################
#       AUTH PASSWORDRESET RESET      #
#######################################

def test_auth_passwordreset_reset_valid():
    '''
    Tests auth_passwordreset_reset for valid cases.
    '''
    # Reset all data and register and logout user
    workplace_reset()
    user = auth_register('nlongbottom@hogwarts.com', 'Remembrall', 'Neville', 'Longbottom')

    # Request reset code
    auth_passwordreset_request('nlongbottom@hogwarts.com')

    # Get reset code from data structure
    user_data = get_user('u_id', user['u_id'])
    reset_code = user_data['reset_code']

    # Call function
    auth_passwordreset_reset(reset_code, 'Herbology')

    # Check password is changed in data structure
    assert user_data['password'] == generate_hash('Herbology')

    # Check reset code has been removed from user data
    assert not user_data.get('reset_code')

def test_auth_passwordreset_reset_invalid():
    '''
    Tests auth_passwordreset_reset for invalid cases.
    '''
    # Reset all data and register and logout user
    workplace_reset()
    user = auth_register('nlongbottom@hogwarts.com', 'Remembrall', 'Neville', 'Longbottom')

    # Request reset code
    auth_passwordreset_request('nlongbottom@hogwarts.com')

    # Get reset code from data structure
    user_data = get_user('u_id', user['u_id'])
    reset_code = user_data['reset_code']

    # InputError: invalid reset code
    with pytest.raises(InputError):
        auth_passwordreset_reset(INVALID, 'Herbology')

    # InputError: password is less than 6 characters
    with pytest.raises(InputError):
        auth_passwordreset_reset(reset_code, 'NL')

    # Input Error: password exceeds 50 characters
    with pytest.raises(InputError):
        auth_passwordreset_reset(reset_code, 'Herbology' * 50)
