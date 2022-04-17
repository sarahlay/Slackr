'''
Message Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
from datetime import datetime
import pytest
from message import message_send, message_edit, message_remove, message_pin, \
        message_unpin, message_react, message_unreact
from auth import auth_register
from channel import channel_join, channel_invite
from channels import channels_create
from data import get_data
from helper import get_channel_messages, get_message
from other import workplace_reset
from error import AccessError, InputError

INVALID = 1024

#######################################
#            MESSAGE SEND             #
#######################################

def test_message_send_valid():
    '''
    Tests message_send for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user2 = auth_register('johannathen@gmail.com', '1232dsa', 'J', 'T')

    # User 1- create a channel and invite User 2
    channel = channels_create(user1['token'], 'TestChannel', True)
    channel_invite(user1['token'], channel['channel_id'], user2['u_id'])

    # Check function return value for owner and member sending messages to channel
    assert message_send(user1['token'], channel['channel_id'], 'Hello') == {
        'message_id': 1
    }
    assert message_send(user2['token'], channel['channel_id'], 'This is a test message') == {
        'message_id': 2
    }

    # Check data structure
    assert get_channel_messages(channel['channel_id']) == [
        {
            'message_id': 2,
            'u_id': 2,
            'message': 'This is a test message',
            'time_created': int(datetime.now().timestamp()),
            'reacts': [{'u_ids': [], 'is_this_user_reacted': False, 'react_id': 1}],
            'is_pinned': False
        },
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'Hello',
            'time_created': int(datetime.now().timestamp()),
            'reacts': [{'u_ids': [], 'is_this_user_reacted': False, 'react_id': 1}],
            'is_pinned': False
        }
    ]

def test_message_send_invalid():
    '''
    Tests message_send for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user2 = auth_register('johannathen@gmail.com', '1232dsa', 'J', 'T')

    # User 1- create a channel
    channel = channels_create(user1['token'], 'TestChannel', True)

    # AccessError: invalid token
    with pytest.raises(AccessError):
        message_send(INVALID, channel['channel_id'], 'Hello')

    # AccessError: user is not a member
    with pytest.raises(AccessError):
        message_send(user2['token'], channel['channel_id'], 'Hello')

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        message_send(user1['token'], INVALID, 'Hello')

    # InputError: message exceeds 1000 characters
    with pytest.raises(InputError):
        message_send(user1['token'], channel['channel_id'], 'Hello' * 1000)


#######################################
#           MESSAGE REMOVE            #
#######################################

def test_message_remove_valid():
    '''
    Tests message_remove for valid cases.
    '''
    # Reset all data and register user
    workplace_reset()
    user1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user2 = auth_register('johannathen@gmail.com', '1232dsa', 'J', 'T')
    user3 = auth_register('sarahlay@gmail.com', '1232dsa', 'S', 'L')

    # User 2- create a channel and invite User 3
    channel = channels_create(user2['token'], 'TestChannel', True)
    channel_invite(user2['token'], channel['channel_id'], user3['u_id'])

    # User 3- send 3 messages into the channel
    message1 = message_send(user3['token'], channel['channel_id'], 'Hello')
    message2 = message_send(user3['token'], channel['channel_id'], 'This is a test message')
    message3 = message_send(user3['token'], channel['channel_id'], 'Message numero 3')

    # Check function return value for Slackr owner channel owner and message owner removing message
    assert message_remove(user1['token'], message1['message_id']) == {}
    assert message_remove(user2['token'], message2['message_id']) == {}
    assert message_remove(user3['token'], message3['message_id']) == {}

    # Check data structure
    assert get_channel_messages(channel['channel_id']) == []

def test_message_remove_invalid():
    '''
    Tests message_remove for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user2 = auth_register('johannathen@gmail.com', '1232dsa', 'J', 'T')

    # User 1- create a channel and send a message
    channel = channels_create(user1['token'], 'TestChannel', True)
    message1 = message_send(user1['token'], channel['channel_id'], 'Hello')

    # AccessError: invalid token
    with pytest.raises(AccessError):
        message_remove(INVALID, message1['message_id'])

    # AccessError: user is not the owner of Slackr, the channel or the message
    with pytest.raises(AccessError):
        message_remove(user2['token'], message1['message_id'])

    # InputError: message with message ID does not exist
    with pytest.raises(InputError):
        message_remove(user1['token'], INVALID)


#######################################
#             MESSAGE EDIT            #
#######################################

def test_message_edit_valid():
    '''
    Tests message_edit for valid cases.
    '''
    # Reset all data and register user
    workplace_reset()
    user1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user2 = auth_register('johannathen@gmail.com', '1232dsa', 'J', 'T')
    user3 = auth_register('sarahlay@gmail.com', '1232dsa', 'S', 'L')

    # User 2- create a channel and invite User 3
    channel = channels_create(user2['token'], 'TestChannel', True)
    channel_invite(user2['token'], channel['channel_id'], user3['u_id'])

    # User 3- send 3 messages into the channel
    message1 = message_send(user3['token'], channel['channel_id'], 'Hello')
    message2 = message_send(user3['token'], channel['channel_id'], 'This is a test message')
    message3 = message_send(user3['token'], channel['channel_id'], 'Message numero 3')

    # Check function return value for Slackr owner channel owner and message owner editing message
    assert message_edit(user1['token'], message1['message_id'], 'COMP1531') == {}
    assert message_edit(user2['token'], message2['message_id'], 'H09APADTHAI') == {}
    assert message_edit(user3['token'], message3['message_id'], 'YAY') == {}

def test_message_edit_invalid():
    '''
    Tests message_edit for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user2 = auth_register('johannathen@gmail.com', '1232dsa', 'J', 'T')

    # User 1- create a channel and send a message
    channel = channels_create(user1['token'], 'TestChannel', True)
    message1 = message_send(user1['token'], channel['channel_id'], 'Hello')

    # AccessError: invalid token
    with pytest.raises(AccessError):
        message_edit(INVALID, message1['message_id'], 'COMP1531')

    # AccessError: user is not the owner of Slackr, the channel or the message
    with pytest.raises(AccessError):
        message_edit(user2['token'], message1['message_id'], 'COMP1531')

    # InputError: message with message ID does not exist
    with pytest.raises(InputError):
        message_edit(user1['token'], INVALID, 'COMP1531')

    # InputError: editted message exceeds 1000 characters
    with pytest.raises(InputError):
        message_edit(user1['token'], message1['message_id'], 'COMP1531' * 1000)


############################################
# Testing Core Function: Reacting Messages #
############################################

def test_message_react():
    '''
    Tests message_react for valid cases
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    assert message_react(user['token'], message_sent['message_id'], 1) == {}

def test_message_react_invalid_react():
    '''
    Tests message_react to raise an InputError given an invalid react_id
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_react(user['token'], message_sent['message_id'], 2)

def test_message_react_message_check():
    '''
    Tests message_react to raise an InputError given an invalid message_id
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_react(user['token'], 2, 1)

##############################################
# Testing Core Function: Unreacting Messages #
##############################################
def test_message_unreact():
    '''
    Tests message_unreact for valid cases
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    message_react(user['token'], message_sent['message_id'], 1)
    assert message_unreact(user['token'], message_sent['message_id'], 1) == {}

def test_message_unreact_already_unreacted():
    '''
    Tests message_unreact for an InputError given a message that has no existing react
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_unreact(user['token'], message_sent['message_id'], 1)

def test_message_unreact_invalid_react():
    '''
    Tests message_unreact for an InputError given an invalid react_id
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_react(user['token'], message_sent['message_id'], 2)

def test_message_unreact_invalid_message():
    '''
    Tests message_unreact for an InputError given an invalid message_id
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    channel_join(user['token'], channel1['channel_id'])
    message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_react(user['token'], 2, 1)

#######################################
# Testing Core Function: Pin Messages #
#######################################

def test_message_pin():
    '''
    Tests message_pin for valid cases
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    channel_join(user['token'], channel1['channel_id'])
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    message_pin(user['token'], message_sent['message_id'])
    assert get_message(message_sent['message_id'])['is_pinned']

    pinned = False
    for pinned in get_data()['messages'].items():
        if message_sent['message_id'] == 'message_id' and 'is_pinned' == True:
            pinned = True
    assert pinned

def test_message_pin_pinned():
    '''
    Tests message_pin for an InputError given a message with an existing pin
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    message_pin(user['token'], message_sent['message_id'])
    with pytest.raises(InputError):
        message_pin(user['token'], message_sent['message_id'])

def test_message_pin_invalid_msgid():
    '''
    Tests message_pin for an InputError given an invalid message_id
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_pin(user['token'], 2)

def test_message_pin_not_owner():
    '''
    Tests message_pin for an AccessError given a non-owner's token
    '''
    workplace_reset()
    owner = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user = auth_register('user@gmail.com', 'fnsdf231', 'R', 'U')
    channel1 = channels_create(owner['token'], 'COMP1531_GROUP', True)
    channel_join(user['token'], channel1['channel_id'])
    message_sent = message_send(owner['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(AccessError):
        message_pin(user['token'], message_sent['message_id'])

def test_message_pin_not_member():
    '''
    Tests message_pin for an AccessError given a non-member's token
    '''
    workplace_reset()
    owner = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user = auth_register('user@gmail.com', 'fnsdf231', 'R', 'U')
    channel1 = channels_create(owner['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(owner['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(AccessError):
        message_pin(user['token'], message_sent['message_id'])

#########################################
# Testing Core Function: Unpin Messages #
#########################################

def test_message_unpin():
    '''
    Tests message_unpin for valid cases
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    message_pin(user['token'], message_sent['message_id'])
    message_unpin(user['token'], message_sent['message_id'])

    unpinned = False
    for unpinned in get_data()['messages'].items():
        if message_sent['message_id'] == 'message_id' and 'is_pinned' == False:
            unpinned = True
    assert unpinned

def test_message_unpin_unpinned():
    '''
    Tests message_unpin for an InputError given a message that has no existing pin
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_unpin(user['token'], message_sent['message_id'])

def test_message_unpin_invalid_msgid():
    '''
    Tests message_unpin for an InputError given an invalid message_id
    '''
    workplace_reset()
    user = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    channel1 = channels_create(user['token'], 'COMP1531_GROUP', True)
    message_send(user['token'], channel1['channel_id'], 'Hello')
    with pytest.raises(InputError):
        message_unpin(user['token'], 2)

def test_message_unpin_not_owner():
    '''
    Tests message_unpin for an AccessError given the token of a non-owner
    '''
    workplace_reset()
    owner = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user = auth_register('user@gmail.com', 'fnsdf231', 'R', 'U')
    channel1 = channels_create(owner['token'], 'COMP1531_GROUP', True)
    channel_join(user['token'], channel1['channel_id'])
    message_sent = message_send(owner['token'], channel1['channel_id'], 'Hello')
    message_pin(owner['token'], message_sent['message_id'])
    with pytest.raises(AccessError):
        message_unpin(user['token'], message_sent['message_id'])

def test_message_unpin_not_member():
    '''
    Tests message_unpin for an AccessError given the token of a non-member
    '''
    workplace_reset()
    owner = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    user = auth_register('user@gmail.com', 'fnsdf231', 'R', 'U')
    channel1 = channels_create(owner['token'], 'COMP1531_GROUP', True)
    message_sent = message_send(owner['token'], channel1['channel_id'], 'Hello')
    message_pin(owner['token'], message_sent['message_id'])
    with pytest.raises(AccessError):
        message_unpin(user['token'], message_sent['message_id'])
######################
# Verification Tests #
######################

def test_message_access_check():
    """
    Tests message_edit & message_remove for AccessError given a non-authorised user's token
    """
    workplace_reset()
    # Create two users, one an admin and the other a non-admin
    admin = auth_register('martinle@gmail.com', '1232dsa', 'M', 'L')
    non_admin = auth_register('randomUser@gmail.com', 'fs-23jasa', 'R', 'U')

    # Have the admin create a channel and send a message
    channel1 = channels_create(admin['token'], 'COMP1531_GROUP', True)
    message1 = message_send(admin['token'], channel1['channel_id'], 'Hello, my name is Martin')

    # A non-admin user joins channel and attempts to edit a message
    channel_join(non_admin['token'], channel1['channel_id'])
    message2 = 'Hello, my name is Random User'

    with pytest.raises(AccessError):
        assert message_edit(non_admin['token'], message1['message_id'], message2)

    with pytest.raises(AccessError):
        assert message_remove(non_admin['token'], message1['message_id'])
