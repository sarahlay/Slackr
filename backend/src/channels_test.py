'''
Channels Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
import pytest
from channels import channels_create, channels_list, channels_listall
from auth import auth_register, auth_logout
from data import get_data
from other import workplace_reset
from error import AccessError, InputError

INVALID = 1024

#######################################
#            CHANNELS LIST            #
#######################################

def test_channels_list_valid():
    '''
    Tests channels_list for valid cases.
    '''
    # Reset all data and register User 1
    workplace_reset()
    token1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')['token']

    # User 1- Create public and private channels
    channels_create(token1, 'TestChannel', True)
    channels_create(token1, 'SecondChannel', False)
    channels_create(token1, 'SecretChannel', False)
    channels_create(token1, 'COMP1531', True)

    # Check function return value - details of the channels that User 1 is a member of
    assert channels_list(token1) == {
        'channels': [
            {'channel_id': 1, 'name': 'TestChannel'},
            {'channel_id': 2, 'name': 'SecondChannel'},
            {'channel_id': 3, 'name': 'SecretChannel'},
            {'channel_id': 4, 'name': 'COMP1531'}
        ]
    }

    # Logout User 1
    auth_logout(token1)

    # Register User 2
    token2 = auth_register('randomUser@gmail.com', 'nf2931f', 'R', 'U')['token']

    # User 2- Create public and private channels
    channels_create(token2, 'COMP1511', True)
    channels_create(token2, 'MATH1231', True)
    channels_create(token2, 'MATH1131', True)
    channels_create(token2, 'INFS3634', True)

    # Check function return value - details of the channels that the User 2 is a member of
    assert channels_list(token2) == {
        'channels': [
            {'channel_id': 5, 'name': 'COMP1511'},
            {'channel_id': 6, 'name': 'MATH1231'},
            {'channel_id': 7, 'name': 'MATH1131'},
            {'channel_id': 8, 'name': 'INFS3634'}
        ]
    }

def test_channels_list_invalid():
    '''
    Tests channels_list for invalid cases.
    '''
    # Reset all data and register a user
    workplace_reset()
    auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channels_list(INVALID)


#######################################
#          CHANNELS LISTALL           #
#######################################

def test_channels_listall_valid():
    '''
    Tests channels_listall for valid cases.
    '''
    # Reset all data and register User 1 and User 2
    workplace_reset()
    token1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')['token']
    token2 = auth_register('randomUser@gmail.com', 'nf2931f', 'R', 'U')['token']

    # User 1- Create public and private channels
    channels_create(token1, 'TestChannel', True)
    channels_create(token1, 'SecondChannel', False)
    channels_create(token1, 'SecretChannel', False)
    channels_create(token1, 'COMP1531', True)

    # User 2- Create public and private channels
    channels_create(token2, 'COMP1511', True)
    channels_create(token2, 'MATH1231', True)
    channels_create(token2, 'MATH1131', True)
    channels_create(token2, 'INFS3634', True)

    # Check functio return value - details of all public channels
    assert channels_listall(token2) == {
        'channels': [
            {'channel_id': 1, 'name': 'TestChannel'},
            {'channel_id': 4, 'name': 'COMP1531'},
            {'channel_id': 5, 'name': 'COMP1511'},
            {'channel_id': 6, 'name': 'MATH1231'},
            {'channel_id': 7, 'name': 'MATH1131'},
            {'channel_id': 8, 'name': 'INFS3634'}
        ]
    }

def test_channels_listall_invalid():
    '''
    Tests channels_listall for invalid cases.
    '''
    # Reset all data and register a user
    workplace_reset()
    auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channels_listall(INVALID)


#######################################
#           CHANNELS CREATE           #
#######################################

def test_channels_create_valid():
    '''
    Tests channels_create for valid cases.
    '''
    # Reset all data and register User 1 and User 2
    workplace_reset()
    token1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')['token']

    # Check function return value
    assert channels_create(token1, 'TestChannel', True) == {'channel_id': 1}
    assert channels_create(token1, 'TopSecretChannel', False) == {'channel_id': 2}

    # Check data structure
    assert get_data()['channels'] == {
        1: {
            'name': 'TestChannel',
            'all_members': [{
                'u_id': 1,
                'name_first': 'M',
                'name_last': 'L',
                'profile_img_url':
                None
            }],
            'owner_members': [{
                'u_id': 1,
                'name_first': 'M',
                'name_last': 'L',
                'profile_img_url': None
            }],
            'is_public': True,
            'standup': {
                'is_active': False,
                'time_finish': None,
                'u_id': None,
                'messages': ''
            },
            'hangman': {
                'word': None,
                'display': [],
                'guesses': '',
                'strikes': 0,
                'message': None
            }
        },
        2: {
            'name': 'TopSecretChannel',
            'all_members': [{
                'u_id': 1,
                'name_first': 'M',
                'name_last': 'L',
                'profile_img_url': None
            }],
            'owner_members': [{
                'u_id': 1,
                'name_first': 'M',
                'name_last': 'L',
                'profile_img_url': None
            }],
            'is_public': False,
            'standup': {
                'is_active': False,
                'time_finish': None,
                'u_id': None,
                'messages': ''
            },
            'hangman': {
                'word': None,
                'display': [],
                'guesses': '',
                'strikes': 0,
                'message': None
            }
        }}

def test_channels_create_invalid():
    '''
    Tests channels_create for invalid cases.
    '''
    # Reset all data and register User 1 and User 2
    workplace_reset()
    token1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')['token']

    # Check function return value
    assert channels_create(token1, 'TestChannel', True) == {'channel_id': 1}
    assert channels_create(token1, 'TopSecretChannel', False) == {'channel_id': 2}

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channels_create(INVALID, 'TestChannel', True)

    #InputError: channel name exceeds 20 characters
    with pytest.raises(InputError):
        channels_create(token1, 'TestChannel' * 21, True)
