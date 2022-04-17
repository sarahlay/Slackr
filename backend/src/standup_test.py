'''
Standup Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
from datetime import datetime
from time import sleep
import threading
import pytest
from standup import standup_start, standup_active, standup_send
from auth import auth_register
from channels import channels_create
from channel import channel_invite
from other import workplace_reset
from helper import get_standup, get_user
from data import get_data
from error import InputError, AccessError

#####################
# Creating Fixtures #
#####################

def register_user():
    '''
    Creating a fixture to register a user
    '''
    user1 = auth_register('hpotter@hogwarts.com', 'Chosen1', 'Harry', 'Potter')
    return user1

def create_channel(user):
    '''
    Creating a fixture to create public channels
    '''
    # Create channels
    public = channels_create(user['token'], 'Public Channel', True)
    return public

# Constants
INVALID = 1024

########################################
# Testing Core Function: standup_start #
########################################

def test_standup_start_valid():
    '''
    Testing standup_start for valid cases
    '''
    workplace_reset()
    user1 = register_user()
    private = channels_create(user1['token'], 'Private Channel', False)

    assert standup_start(user1['token'], private['channel_id'], 200) == {
        'time_finish' : int(datetime.now().timestamp() + 200)
    }


def test_standup_start_invalid_channel_id():
    '''
    Testing standup_start for an InputError given an invalid channel_id
    '''
    workplace_reset()
    user1 = register_user()

    with pytest.raises(InputError):
        standup_start(user1['token'], INVALID, 200)


def test_standup_start_active_standup():
    '''
    Testing standup_start for an InputError given a channel with
    an active standup running
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    with pytest.raises(InputError):
        standup_start(user1['token'], public['channel_id'], 700)


def test_standup_start_invalid_member():
    '''
    Testing standup_start for an AccessError given an invalid user_id
    '''
    workplace_reset()
    user1 = register_user()
    user2 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')
    public = create_channel(user1)

    with pytest.raises(AccessError):
        standup_start(user2['token'], public['channel_id'], 700)


def test_standup_start_invalid_token():
    '''
    Testing standup_start for an AccessError given an invalid token
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    with pytest.raises(AccessError):
        standup_start(INVALID, public['channel_id'], 200)


#########################################
# Testing Core Function: standup_active #
#########################################

def test_standup_active_valid_not_active():
    '''
    Testing standup_active for valid case of non active standup
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)
    private = channels_create(user1['token'], 'Private Channel', False)

    assert standup_active(user1['token'], public['channel_id']) == {
        'is_active' : False,
        'time_finish' : None
    }

    assert standup_active(user1['token'], private['channel_id']) == {
        'is_active' : False,
        'time_finish' : None
    }


def test_standup_active_valid_active():
    '''
    Testing standup_active for an valid case of an active standup
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    assert standup_active(user1['token'], public['channel_id']) == {
        'is_active' : True,
        'time_finish' : int(datetime.now().timestamp() + 200)
    }


def test_standup_active_invalid_channel_id():
    '''
    Testing standup_active for an InputError given an invalid channel_id
    '''
    workplace_reset()
    user1 = register_user()

    with pytest.raises(InputError):
        standup_active(user1['token'], INVALID)


def test_standup_active_invalid_member():
    '''
    Testing standup_active for an AccessError given an invalid user_id
    '''
    workplace_reset()
    user1 = register_user()
    user2 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    with pytest.raises(AccessError):
        standup_active(user2['token'], public['channel_id'])


def test_standup_active_invalid_token():
    '''
    Testing standup_active for an AccessError given an invalid token
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    with pytest.raises(AccessError):
        standup_active(INVALID, public['channel_id'])


#######################################
# Testing Core Function: standup_send #
#######################################
def message_check_thread(token, channel_id, checked_message, time):
    '''
    Function thats enables a check on delayed messages
    '''
    sleep(time)
    assert standup_active(token, channel_id) == {
        'is_active': False,
        'time_finish': None
    }

    # Check messages data structure
    messages = get_data()['messages'][channel_id]
    message = next(i for i in messages if i['message_id'] == 1)
    assert message['message'] == checked_message

def test_standup_send_valid():
    '''
    Testing standup_send for valid cases
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 2)
    standup_send(user1['token'], public['channel_id'], 'My scar hurts!')
    standup = get_standup(public['channel_id'])

    user = get_user('u_id', user1['u_id'])
    checked_message = f"{user['handle_str']}: My scar hurts!\n"

    # Check standup data structure
    assert standup['messages'] == checked_message

    threading.Thread(
        target=message_check_thread,
        args=(user1['token'], public['channel_id'], checked_message, 2),
        daemon=True
    ).start()


def test_standup_send_more_messages():
    '''
    Testing standup_send for valid cases with 2 messages from different users
    '''
    workplace_reset()
    user1 = register_user()
    user2 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')
    public = create_channel(user1)
    channel_invite(user1['token'], public['channel_id'], user2['u_id'])

    # Starting standup and sending messages
    standup_start(user1['token'], public['channel_id'], 2)
    standup_send(user1['token'], public['channel_id'], 'My scar hurts!')
    standup_send(user2['token'], public['channel_id'], 'Lemon drop.')

    standup = get_standup(public['channel_id'])
    profile1 = get_user('u_id', user1['u_id'])
    profile2 = get_user('u_id', user2['u_id'])
    checked_message =\
        f"{profile1['handle_str']}: My scar hurts!\n"\
        f"{profile2['handle_str']}: Lemon drop.\n"\


    # Check standup data structure
    assert standup['messages'] == checked_message

    threading.Thread(
        target=message_check_thread,
        args=(user1['token'], public['channel_id'], checked_message, 2),
        daemon=True
    ).start()


def test_standup_send_invalid_channel_id():
    '''
    Testing standup_send for an InputError given an invalid channel_id
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    with pytest.raises(InputError):
        standup_send(user1['token'], INVALID, 'My scar hurts!')


def test_standup_send_invalid_not_active():
    '''
    Testing standup_send for an InputError given a channel with
    a non-active standup
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    with pytest.raises(InputError):
        standup_send(user1['token'], public['channel_id'], 'My scar hurts!')


def test_standup_send_invalid_message():
    '''
    Testing standup_send for an InputError
    given a message that exceeds 1000 characters
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    with pytest.raises(InputError):
        standup_send(user1['token'], public['channel_id'], 'My scar hurts!' * 1000)


def test_standup_send_invalid_member():
    '''
    Testing standup_send for an AccessError given an token for a non-member
    '''
    workplace_reset()
    user1 = register_user()
    user2 = auth_register('adumbledore@hogwarts.com', 'Fawkes', 'Albus', 'Dumbledore')
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    with pytest.raises(AccessError):
        standup_send(user2['token'], public['channel_id'], 'My scar hurts!')


def test_standup_send_invalid_token():
    '''
    Testing standup_send for an AccessError given an invalid token
    '''
    workplace_reset()
    user1 = register_user()
    public = create_channel(user1)

    standup_start(user1['token'], public['channel_id'], 200)
    with pytest.raises(AccessError):
        standup_send(INVALID, public['channel_id'], 'My scar hurts!')
