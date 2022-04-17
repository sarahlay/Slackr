'''
User Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
import pytest
from user import user_profile, user_profile_setname, user_profile_setemail, \
    user_profile_sethandle, user_profile_uploadphoto
from auth import auth_register
from other import workplace_reset
from error import AccessError, InputError

INVALID = 1024

#######################################
#             USER PROFILE            #
#######################################

def test_user_profile_valid():
    '''
    Tests user_profile for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')
    user2 = auth_register('hpotter@hogwarts.com', 'Quidditch', 'Harry', 'Potter')

    # Check users can view their own profile
    assert user_profile(user1['token'], user1['u_id']) == {
        'user': {
            'u_id' : user1['u_id'],
            'email' : 'adumbledore@hogwarts.com',
            'name_first' : 'Albus',
            'name_last' : 'Dumbledore',
            'handle_str' : 'albusdumbledore1',
            'profile_img_url' : None
        }
    }

    # Check users can view other users' profiles
    assert user_profile(user1['token'], user2['u_id']) == {
        'user': {
            'u_id' : user2['u_id'],
            'email' : 'hpotter@hogwarts.com',
            'name_first' : 'Harry',
            'name_last' : 'Potter',
            'handle_str' : 'harrypotter2',
            'profile_img_url' : None
        }
    }

def test_user_profile_invalid():
    '''
    Tests user_profile for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')

    # AccessError: invalid token
    with pytest.raises(AccessError):
        user_profile(INVALID, user1['u_id'])

    # InputError: invalid user ID
    with pytest.raises(InputError):
        user_profile(user1['token'], INVALID)


#######################################
#         USER PROFILE SETNAME        #
#######################################

def test_user_profile_setname_valid():
    '''
    Tests user_profile_setname for valid cases.
    '''
    # Reset all data and register user
    workplace_reset()
    user1 = auth_register('gweaseley@hogwarts.com', 'BatBogey', 'Ginerva', 'Weasley')

    # Call function
    user_profile_setname(user1['token'], 'Ginny', 'Potter')
    profile1 = user_profile(user1['token'], user1['u_id'])['user']

    # Check user can change their name
    assert profile1['name_first'] == 'Ginny'
    assert profile1['name_last'] == 'Potter'

def test_user_profile_setname_invalid():
    '''
    Tests user_profile_setname for invalid cases.
    '''
    # Reset all data and register user
    workplace_reset()
    user1 = auth_register('gweaseley@hogwarts.com', 'BatBogey', 'Ginerva', 'Weasley')

    # AccessError: invalid token
    with pytest.raises(AccessError):
        user_profile_setname(INVALID, 'Ginny', 'Potter')

    # InputError: empty first name
    with pytest.raises(InputError):
        user_profile_setname(user1['token'], '', 'Potter')

    # InputError: first name exceeds 50 characters
    with pytest.raises(InputError):
        user_profile_setname(user1['token'], 'Ginny' * 50, 'Potter')

    # InputError: empty last name
    with pytest.raises(InputError):
        user_profile_setname(user1['token'], 'Ginny', '')

    # InputError: last name exceeds 50 characters
    with pytest.raises(InputError):
        user_profile_setname(user1['token'], 'Ginny', 'Potter' * 50)


#######################################
#        USER PROFILE SETEMAIL        #
#######################################

def test_user_profile_setemail_valid():
    '''
    Tests user_profile_setemail for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('fweaseley@hogwarts.com', 'MischiefManaged', 'Fred', 'Weasley')

    # Call function
    user_profile_setemail(user1['token'], 'fred@weasleyswizardwheezes.com')
    profile1 = user_profile(user1['token'], user1['u_id'])['user']

    # Check user can change their email
    assert profile1['email'] == 'fred@weasleyswizardwheezes.com'

def test_user_profile_setnemail_invalid():
    '''
    Tests user_profile_setemail for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('fweaseley@hogwarts.com', 'MischiefManaged', 'Fred', 'Weasley')
    user2 = auth_register('gweaseley@hogwarts.com', 'Saintlike', 'George', 'Weasley')
    profile1 = user_profile(user1['token'], user1['u_id'])['user']
    profile2 = user_profile(user2['token'], user2['u_id'])['user']

    # AccessError: invalid token
    with pytest.raises(AccessError):
        user_profile_setemail(INVALID, 'fred@weasleyswizardwheezes.com')

    # InputError: empty email
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], '')

    # InputError: invalid email format
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], 'weasleyswizardwheezes.com')

    # AccessError: email already used by the user
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], profile1['email'])

    # AccessError: email already used by another user
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], profile2['email'])


#######################################
#        USER PROFILE SETHANDLE       #
#######################################

def test_user_profile_sethandle_valid():
    '''
    Tests user_profile_sethandle for valid cases.
    '''
    # Reset all data and register user
    workplace_reset()
    user1 = auth_register('triddle@hogwarts.com', 'Nagini', 'Tom', 'Riddle')

    # Call function
    user_profile_sethandle(user1['token'], 'lordvoldemort')
    profile1 = user_profile(user1['token'], user1['u_id'])['user']

    # Check user can change their handle
    assert profile1['handle_str'] == 'lordvoldemort'

def test_user_profile_sethandle_invalid():
    '''
    Tests user_profile_sethandle for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('triddle@hogwarts.com', 'Nagini', 'Tom', 'Riddle')
    user2 = auth_register('lordvoldemort@darkmagic.com', 'Nagini', 'Lord', 'Voldemort')
    profile1 = user_profile(user1['token'], user1['u_id'])['user']
    profile2 = user_profile(user2['token'], user2['u_id'])['user']

    # AccessError: invalid token
    with pytest.raises(AccessError):
        user_profile_sethandle(INVALID, 'lordvoldemort')

    # InputError: empty handle
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], '')

    # InputError: handle exceeds 20 characters
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], 'lordvoldemort' * 20)

    # AccessError: handle already used by the user
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], profile1['handle_str'])

    # AccessError: handle already used by another user
    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], profile2['handle_str'])

###################################################
# Testing Core Function: user_profile_uploadphoto #
###################################################

def test_user_profile_uploadphoto_valid():
    '''Test to check a valid upload of photo'''
    workplace_reset()
    user1 = auth_register('triddle@hogwarts.com', 'Nagini', 'Tom', 'Riddle')
    url = "https://api.time.com/wp-content/uploads/2015/01/harry-potter-illustrations-04.jpg"
    assert user_profile_uploadphoto(user1['token'], url, 0, 200, 1800, 2000) == {}

def test_user_profile_uploadphoto_wrong_type():
    '''Test to check if an InputError is raised when an image with the wrong format is uploaded'''
    workplace_reset()
    user1 = auth_register('triddle@hogwarts.com', 'Nagini', 'Tom', 'Riddle')
    url = "https://vignette.wikia.nocookie.net/parsel/images/6/65/Severus_Snape.png"
    with pytest.raises(InputError):
        user_profile_uploadphoto(user1['token'], url, 0, 0, 200, 300)

def test_user_profile_uploadphoto_wrong_dimensions():
    '''Test to check if an InputError is raised when the wrong crop dimensions are entered'''
    workplace_reset()
    user1 = auth_register('triddle@hogwarts.com', 'Nagini', 'Tom', 'Riddle')
    url = "https://api.time.com/wp-content/uploads/2015/01/harry-potter-illustrations-04.jpg"
    with pytest.raises(InputError):
        user_profile_uploadphoto(user1['token'], url, 10000, 10000, 200, 300)

def test_user_profile_uploadphoto_wrong_url():
    '''Test to check if an InputError is raised when an invalid url is entered'''
    workplace_reset()
    user1 = auth_register('triddle@hogwarts.com', 'Nagini', 'Tom', 'Riddle')
    url = "https://api.time.com/wp-content/uploads/2020/01/harry-potter-illustrations-04.jpg"
    with pytest.raises(InputError):
        user_profile_uploadphoto(user1['token'], url, 0, 200, 1800, 2000)
