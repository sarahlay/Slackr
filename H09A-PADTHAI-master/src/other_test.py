'''
Other Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
import pytest
from channels import channels_create
from channel import channel_invite, channel_addowner
from message import message_send
from auth import auth_register
from data import get_data
from other import users_all, admin_userpermission_change, admin_user_remove,\
    workplace_reset, search
from error import InputError, AccessError
from helper import get_user

OWNER = 1
MEMBER = 2
INVALID = 1024

#####################
# Creating Fixtures #
#####################

def register_user():
    '''
    Creating a fixture to register users for use in testing
    '''
    user1 = auth_register('hpotter@hogwarts.com', 'Chosen1', 'Harry', 'Potter')
    user2 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')
    return [user1, user2]

####################################
# Testing Core Function: users_all #
####################################

def test_users_all_valid():
    '''
    Testing users_all for valid cases
    '''
    workplace_reset()

    user1 = auth_register('hpotter@hogwarts.com', 'Chosen1', 'Harry', 'Potter')
    assert users_all(user1['token']) == {
        'users': [{
            'email': 'hpotter@hogwarts.com',
            'handle_str': 'harrypotter1',
            'name_first': 'Harry',
            'name_last': 'Potter',
            'u_id': 1,
            'profile_img_url': None
        }]
    }

    user2 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')
    assert users_all(user2['token']) == {
        'users': [{
            'email': 'hpotter@hogwarts.com',
            'handle_str': 'harrypotter1',
            'name_first': 'Harry',
            'name_last': 'Potter',
            'u_id': 1,
            'profile_img_url': None
        },
        {
            'email': 'adumbledore@hogwarts.com',
            'handle_str': 'albusdumbledore2',
            'name_first': 'Albus',
            'name_last': 'Dumbledore',
            'u_id': 2,
            'profile_img_url': None
        }]
    }


def test_users_all_invalid_token():
    '''
    Testing users_all for an AccessError given an invalid token
    '''
    workplace_reset()
    with pytest.raises(AccessError):
        users_all(INVALID)


####################################
#   Testing Core Function: search  #
####################################
def test_search_valid():
    '''
    Testing search for all valid cases
    '''
    workplace_reset()
    user1 = auth_register('hpotter@hogwarts.com', 'Chosen1', 'Harry', 'Potter')

    channel1 = channels_create(user1['token'], 'TestChannel', True)
    message_send(user1['token'], channel1['channel_id'], 'Hello')
    query = 'Hello'
    messages = search(user1['token'], query)['messages']
    assert messages[-1]['message'] == query

    query = 'z'
    messages = search(user1['token'], query)['messages']
    assert messages == []


######################################################
# Testing Core Function: admin_userpermission_change #
######################################################

def test_admin_userpermission_change_valid():
    '''
    Testing admin_userpermission_change for valid cases
    '''
    workplace_reset()
    [user1, user2] = register_user()

    # Check function output
    assert admin_userpermission_change(user1['token'], user2['u_id'], 1) == {}

    # Check data structure
    user2 = get_user('u_id', user2['u_id'])
    assert user2['permission_id'] == 1


def test_admin_userpermission_change_invalid_permission_id():
    '''
    Testing admin_userpermission_change for an InputError given an invalid permission_id
    '''
    workplace_reset()
    [user1, user2] = register_user()

    # Throw Input Error
    with pytest.raises(InputError):
        admin_userpermission_change(user1['token'], user2['u_id'], INVALID)

    # Check data structure
    user2 = get_user('u_id', user2['u_id'])
    assert user2['permission_id'] == 2


def test_admin_userpermission_change_invalid_u_id():
    '''
    Testing admin_userpermission_change for an InputError given an invalid u_id
    '''
    workplace_reset()
    user1 = auth_register('hpotter@hogwarts.com', 'Chosen1', 'Harry', 'Potter')

    # Throw Input Error
    with pytest.raises(InputError):
        admin_userpermission_change(user1['token'], INVALID, 1)


def test_admin_userpermission_change_not_owner():
    '''
    Testing admin_userpermission_change for an AccessError given a non-user's token
    '''
    workplace_reset()
    [user1, user2] = register_user()

    # Throw Access Error
    with pytest.raises(AccessError):
        admin_userpermission_change(user2['token'], user1['u_id'], 2)

    # Check data structure
    user1 = get_user('u_id', user1['u_id'])
    assert user1['permission_id'] == 1


def test_admin_userpermission_change_owner():
    '''
    Testing admin_userpermission_change for an InputError if the user
    attempts to change their own permission
    '''
    workplace_reset()
    user1 = auth_register('hpotter@hogwarts.com', 'Chosen1', 'Harry', 'Potter')

    # Throw Input Error
    with pytest.raises(InputError):
        admin_userpermission_change(user1['token'], user1['u_id'], 2)

def test_admin_userpermission_change_invalid_token():
    '''
    Testing admin_userpermission_change for an AccessError if given an invalid token
    '''

    workplace_reset()
    user1 = auth_register('hpotter@hogwarts.com', 'Chosen1', 'Harry', 'Potter')

    with pytest.raises(AccessError):
        admin_userpermission_change(INVALID, user1['u_id'], 2)

#########################################
# 		 Testing: admin_user_remove		#
#########################################

def test_admin_user_remove_simple():
    '''
    Tests user_remove for valid cases
    '''
    workplace_reset()
    [user1, user2] = register_user()

    # create a channel with user1
    public = channels_create(user1['token'], 'Public Channel', True)

    # invite user 2 and add them as an owner
    channel_invite(user1['token'], public['channel_id'], user2['u_id'])
    channel_addowner(user1['token'], public['channel_id'], user2['u_id'])
    admin_user_remove(user1['token'], user2['u_id'])

    data = get_data()

    is_exist = next((i for i in data['users'] if i['u_id'] == user2['u_id']), False)
    assert not is_exist

    is_member = next(
        (
            i for i in data['channels'][public['channel_id']]['all_members']\
            if i['u_id'] == user2['u_id']
        ),
        False
    )
    assert not is_member

    is_owner = next(
        (
            i for i in data['channels'][public['channel_id']]['owner_members']\
            if i['u_id'] == user2['u_id']
        ),
        False
    )
    assert not is_owner


def test_admin_user_remove_error():
    '''
    Tests user_remove for an InputError given an invalid user_id &
    for an AccessError given a non-owners token
    '''
    workplace_reset()
    [user1, user2] = register_user()
    user3 = auth_register('severussnape@hogwarts.com', 'Professor', 'Severus', 'Snape')

    with pytest.raises(InputError):
        assert admin_user_remove(user1['token'], INVALID)

    with pytest.raises(AccessError):
        assert admin_user_remove(user2['token'], user3['u_id'])
