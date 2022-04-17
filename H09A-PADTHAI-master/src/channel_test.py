'''
Channel Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
from datetime import datetime
import pytest
from error import AccessError, InputError
from channel import channel_addowner, channel_details, channel_invite, channel_join, \
    channel_leave, channel_messages, channel_removeowner
from auth import auth_register
from channels import channels_create
from helper import get_user, get_channel_members, get_channel_owners
from message import message_send
from other import workplace_reset

INVALID = 1024

#######################################
#            CHANNEL INVITE           #
#######################################

def test_channel_invite_valid():
    '''
    Tests channel_invite for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Create channels
    public = channels_create(user1['token'], 'Public Channel', True)
    private = channels_create(user1['token'], 'Private Channel', False)

    # Check return value of function
    assert channel_invite(user1['token'], public['channel_id'], user2['u_id']) == {}
    assert channel_invite(user1['token'], private['channel_id'], user2['u_id']) == {}

    # Check data structure
    assert get_channel_members(public['channel_id']) == [
        {'u_id': 1, 'name_first': 'Aang', 'name_last': 'Airbender', 'profile_img_url': None},
        {'u_id': 2, 'name_first': 'Katara', 'name_last': 'Waterbender', 'profile_img_url': None}
    ]
    assert get_channel_owners(public['channel_id']) == [
        {'u_id': 1, 'name_first': 'Aang', 'name_last': 'Airbender', 'profile_img_url': None}
    ]

def test_channel_invite_invalid():
    '''
    Tests channel_invite for invalid cases
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')
    user3 = auth_register('zuko@gmail.com', 'ILoveFire', 'Zuko', 'Firebender')

    # Create channels
    public = channels_create(user1['token'], 'Public Channel', True)

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channel_invite(INVALID, public['channel_id'], user2['u_id'])

    # AccessError: authorised user is not a member of the channel
    with pytest.raises(AccessError):
        channel_invite(user2['token'], public['channel_id'], user3['u_id'])

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        channel_invite(user1['token'], INVALID, user2['u_id'])

    # InputError: user with given user ID does not exist
    with pytest.raises(InputError):
        channel_invite(user1['token'], public['channel_id'], INVALID)


#######################################
#           CHANNEL DETAILS           #
#######################################

def test_channel_details_valid():
    '''
    Tests channel_details for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Get users' details
    user_data1 = get_user('u_id', user1['u_id'])
    user_data2 = get_user('u_id', user2['u_id'])

    # Create channels
    public = channels_create(user1['token'], 'Public Channel', True)

    # Check owner can view details of channel
    assert channel_details(user1['token'], public['channel_id']) == {
        'name': 'Public Channel',
        'owner_members': [
            {
                'u_id': user_data1['u_id'],
                'name_first': user_data1['name_first'],
                'name_last': user_data1['name_last'],
                'profile_img_url': user_data1['profile_img_url'],
            }
        ],
        'all_members': [
            {
                'u_id': user_data1['u_id'],
                'name_first': user_data1['name_first'],
                'name_last': user_data1['name_last'],
                'profile_img_url': user_data1['profile_img_url']
            }
        ],
    }

    # Invite new member to channel
    channel_invite(user1['token'], public['channel_id'], user2['u_id'])

    # Check member can view details of channel
    assert channel_details(user2['token'], public['channel_id']) == {
        'name': 'Public Channel',
        'owner_members': [
            {
                'u_id': user_data1['u_id'],
                'name_first': user_data1['name_first'],
                'name_last': user_data1['name_last'],
                'profile_img_url': user_data1['profile_img_url']
            }
        ],
        'all_members': [
            {
                'u_id': user_data1['u_id'],
                'name_first': user_data1['name_first'],
                'name_last': user_data1['name_last'],
                'profile_img_url': user_data1['profile_img_url']
            },
            {
                'u_id': user_data2['u_id'],
                'name_first': user_data2['name_first'],
                'name_last': user_data2['name_last'],
                'profile_img_url': user_data2['profile_img_url']
            }
        ],
    }

def test_channel_details_invalid():
    '''
    Tests channel_details for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Create channels
    public = channels_create(user1['token'], 'Public Channel', True)

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channel_details(INVALID, public['channel_id'])

    # AccessError: authorised user is not a member of the channel
    with pytest.raises(AccessError):
        channel_details(user2['token'], public['channel_id'])

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        channel_details(user1['token'], INVALID)


#######################################
#          CHANNEL MESSAGES           #
#######################################

def test_channel_messages_valid():
    '''
    Tests channel_messages for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Create channel
    private = channels_create(user1['token'], 'Private Channel', False)

    # Invite new member to channel
    channel_invite(user1['token'], private['channel_id'], user2['u_id'])

    # Send a message into the channel
    message = message_send(user1['token'], private['channel_id'], 'Irohs tea shop')
    timestamp = int(datetime.now().timestamp())

    assert channel_messages(user1['token'], private['channel_id'], 0) == {
        'messages': [
            {
                'message_id': message['message_id'],
                'u_id': user1['u_id'],
                'message': 'Irohs tea shop',
                'time_created': timestamp,
                'reacts': [{
                    'u_ids': [],
                    'is_this_user_reacted': False,
                    'react_id': 1
                }],
                'is_pinned': False,
            }
        ],
        'start': 0,
        'end': -1
    }

def test_channel_messages_valid_complex():
    '''
    Tests channel messages for the valid case of the owner sending 51 messages to a channel.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')

    # Create channel
    public = channels_create(user1['token'], 'Public Channel', True)

    # Send messages into the channel and store in a list
    messages = []
    i = 0
    while i < 51:
        message = message_send(user1['token'], public['channel_id'], 'cool')
        messages.insert(0, {
            'message_id': message['message_id'],
            'u_id': user1['u_id'],
            'message': 'cool',
            'time_created': int(datetime.now().timestamp()),
            'reacts': [{
                'u_ids': [],
                'is_this_user_reacted': False,
                'react_id': 1
            }],
            'is_pinned': False,
        })

        i += 1

    # Check return value of the function
    assert channel_messages(user1['token'], public['channel_id'], 0) == {
        'messages': messages,
        'start': 0,
        'end': 50
    }

def test_channel_messages_invalid():
    '''
    Tests channel_messages for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Create channel
    public = channels_create(user1['token'], 'Public Channel', True)

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channel_messages(INVALID, public['channel_id'], 0)

    # AccessError: authorised user is not a member of the channel
    with pytest.raises(AccessError):
        channel_messages(user2['token'], public['channel_id'], 0)

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        channel_messages(user1['token'], INVALID, 0)

    # InputError: start index exceeds total number of messages
    with pytest.raises(InputError):
        channel_messages(user1['token'], public['channel_id'], INVALID)


#######################################
#            CHANNEL LEAVE            #
#######################################

def test_channel_leave_valid():
    '''
    Tests channel_leave for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')

    # Create new channel
    public = channels_create(user1['token'], 'Public Channel', True)

    # Check function return value
    assert channel_leave(user1['token'], public['channel_id']) == {}

    # Check data structure
    assert get_channel_members(public['channel_id']) == []
    assert get_channel_owners(public['channel_id']) == []

def test_channel_leave_invalid():
    '''
    Tests channel_leave for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Create new channel
    public = channels_create(user1['token'], 'Public Channel', True)

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channel_leave(INVALID, public['channel_id'])

    # AccessError: user is not a member of the channel
    with pytest.raises(AccessError):
        channel_leave(user2['token'], public['channel_id'])

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        channel_leave(user1['token'], INVALID)


#######################################
#            CHANNEL JOIN             #
#######################################

def test_channel_join_valid():
    '''
    Tests channel_join for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Create new channel
    public = channels_create(user1['token'], 'Public Channel', True)

    # Check function return value
    assert channel_join(user2['token'], public['channel_id']) == {}

    # Check data structure
    assert get_channel_members(public['channel_id']) == [
        {'u_id': 1, 'name_first': 'Aang', 'name_last': 'Airbender', 'profile_img_url': None},
        {'u_id': 2, 'name_first': 'Katara', 'name_last': 'Waterbender', 'profile_img_url': None}
        ]
    assert get_channel_owners(public['channel_id']) == [
        {'u_id': 1, 'name_first': 'Aang', 'name_last': 'Airbender', 'profile_img_url': None}
        ]

def test_channel_join_invalid():
    '''
    Tests channel_join for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')

    # Create new channel
    public = channels_create(user1['token'], 'Public Channel', True)
    private = channels_create(user1['token'], 'Private Channel', False)

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channel_join(INVALID, public['channel_id'])

    # AccessError: channel is private
    with pytest.raises(AccessError):
        channel_join(user2['token'], private['channel_id'])

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        channel_join(user2['token'], INVALID)


#######################################
#          CHANNEL ADDOWNER           #
#######################################

def test_channel_addowner_valid():
    '''
    Tests channel_addowner for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')
    user3 = auth_register('zuko@gmail.com', 'ILoveFire', 'Zuko', 'Firebender')
    user4 = auth_register('toph@gmail.com', 'ILoveEarth', 'Toph', 'Earthbender')

    # Create new channel
    public = channels_create(user2['token'], 'Public Channel', True)

    # Add new members to channel
    channel_join(user3['token'], public['channel_id'])
    channel_join(user4['token'], public['channel_id'])

    # Check function return value for channel owner promoting a member
    assert channel_addowner(user2['token'], public['channel_id'], user3['u_id']) == {}

    # Check data structure
    assert get_channel_owners(public['channel_id']) == [
        {'u_id': 2, 'name_first': 'Katara', 'name_last': 'Waterbender', 'profile_img_url': None},
        {'u_id': 3, 'name_first': 'Zuko', 'name_last': 'Firebender', 'profile_img_url': None}
    ]

    # Check function return value for Slackr owner promoting a member
    assert channel_addowner(user1['token'], public['channel_id'], user4['u_id']) == {}

    # Check data structure
    assert get_channel_owners(public['channel_id']) == [
        {'u_id': 2, 'name_first': 'Katara', 'name_last': 'Waterbender', 'profile_img_url': None},
        {'u_id': 3, 'name_first': 'Zuko', 'name_last': 'Firebender', 'profile_img_url': None},
        {'u_id': 4, 'name_first': 'Toph', 'name_last': 'Earthbender', 'profile_img_url': None}
    ]

def test_channel_addowner_invalid():
    '''
    Tests channel_addowner for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')
    user3 = auth_register('zuko@gmail.com', 'ILoveFire', 'Zuko', 'Firebender')

    # Create new channel
    public = channels_create(user2['token'], 'Public Channel', True)

    # Add a new member to the channel
    channel_join(user3['token'], public['channel_id'])

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channel_addowner(INVALID, public['channel_id'], user1['u_id'])

    # AccessError: user is not an owner of Slackr or the channel
    with pytest.raises(AccessError):
        channel_addowner(user3['token'], public['channel_id'], user1['u_id'])

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        channel_addowner(user2['token'], INVALID, user1['u_id'])

    # InputError: user with user ID does not exist
    with pytest.raises(InputError):
        channel_addowner(user2['token'], public['channel_id'], INVALID)

    # InputError: user with user ID is already an owner of the channel
    with pytest.raises(InputError):
        channel_addowner(user1['token'], public['channel_id'], user2['u_id'])


#######################################
#         CHANNEL REMOVEOWNER         #
#######################################

def test_channel_removeowner_valid():
    '''
    Tests channel_removeowner for valid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')
    user3 = auth_register('zuko@gmail.com', 'ILoveFire', 'Zuko', 'Firebender')
    user4 = auth_register('toph@gmail.com', 'ILoveEarth', 'Toph', 'Earthbender')

    # Create new channel
    public = channels_create(user2['token'], 'Public Channel', True)

    # Add new members to channel
    channel_join(user3['token'], public['channel_id'])
    channel_join(user4['token'], public['channel_id'])

    # Promote members to owners of the channel
    channel_addowner(user2['token'], public['channel_id'], user3['u_id'])
    channel_addowner(user1['token'], public['channel_id'], user4['u_id'])

    # Check function return value for channel owner demoting another owner
    assert channel_removeowner(user2['token'], public['channel_id'], user4['u_id']) == {}

    # Check data structure
    assert get_channel_owners(public['channel_id']) == [
        {'u_id': 2, 'name_first': 'Katara', 'name_last': 'Waterbender', 'profile_img_url': None},
        {'u_id': 3, 'name_first': 'Zuko', 'name_last': 'Firebender', 'profile_img_url': None}
        ]

    # Check function return value for Slackr owner demoting a member
    assert channel_removeowner(user1['token'], public['channel_id'], user3['u_id']) == {}

    # Check data structure
    assert get_channel_owners(public['channel_id']) == [
        {'u_id': 2, 'name_first': 'Katara', 'name_last': 'Waterbender', 'profile_img_url': None}
        ]

    # Check function return value for channel owner demoting themself
    assert channel_removeowner(user2['token'], public['channel_id'], user2['u_id']) == {}

    # Check data structure
    assert get_channel_owners(public['channel_id']) == []

def test_channel_removeowner_invalid():
    '''
    Tests channel_removeowner for invalid cases.
    '''
    # Reset all data and register users
    workplace_reset()
    user1 = auth_register('aang@gmail.com', 'ILoveAir', 'Aang', 'Airbender')
    user2 = auth_register('katara@gmail.com', 'ILoveWater', 'Katara', 'Waterbender')
    user3 = auth_register('zuko@gmail.com', 'ILoveFire', 'Zuko', 'Firebender')

    # Create new channel
    public = channels_create(user2['token'], 'Public Channel', True)

    # Add a new member to the channel
    channel_join(user3['token'], public['channel_id'])

    # AccessError: invalid token
    with pytest.raises(AccessError):
        channel_removeowner(INVALID, public['channel_id'], user1['u_id'])

    # AccessError: user is not an owner of Slackr or the channel
    with pytest.raises(AccessError):
        channel_removeowner(user3['token'], public['channel_id'], user1['u_id'])

    # InputError: channel with channel ID does not exist
    with pytest.raises(InputError):
        channel_removeowner(user2['token'], INVALID, user1['u_id'])

    # InputError: user with user ID does not exist
    with pytest.raises(InputError):
        channel_removeowner(user2['token'], public['channel_id'], INVALID)
