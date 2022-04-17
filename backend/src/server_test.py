'''
Server Tests
By H09A-PADTHAI
Submitted 19 April 2020
'''
from werkzeug.exceptions import HTTPException
from datetime import timezone, datetime
import threading
import json
import urllib
import flask
from other import workplace_reset
import pytest

PORT = 8080 # PORT - CHANGE ME
BASE_URL = f'http://127.0.0.1:{PORT}'

#########################################
# 			Creating Fixtures 			#
#########################################

def reset_server():
    urllib.request.urlopen(f"{BASE_URL}/workspace/reset")

def fixture():
    data1 = json.dumps({
        'email' : 'aang@gmail.com',
        'password' : 'iloveair',
        'name_first' : 'aang',
        'name_last': 'airbender'
    }).encode('utf-8')

    data2 = json.dumps({
        'email' : 'katara@gmail.com',
        'password' : 'ILoveWater',
        'name_first' : 'Katara',
        'name_last': 'Waterbender'
    }).encode('utf-8')

    data3 = json.dumps({
        'email' : 'zuko@gmail.com',
        'password' : 'ILoveFire',
        'name_first' : 'Zuko',
        'name_last': 'Firebender'
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/auth/register",
        data=data1,
        headers={'Content-Type': 'application/json'})
    req2 = urllib.request.Request(f"{BASE_URL}/auth/register",
        data=data2,
        headers={'Content-Type': 'application/json'})
    req3 = urllib.request.Request(f"{BASE_URL}/auth/register",
        data=data3,
        headers={'Content-Type': 'application/json'})

    user1 = json.load(urllib.request.urlopen(req1))
    user2 = json.load(urllib.request.urlopen(req2))
    user3 = json.load(urllib.request.urlopen(req3))

    data1 = json.dumps({
        'token': user1['token'],
        'name': 'Public Channel',
        'is_public': True
    }).encode('utf-8')

    data2 = json.dumps({
        'token': user1['token'],
        'name': 'Private Channel',
        'is_public': False
    }).encode('utf-8')

    req1 = urllib.request.Request(f"{BASE_URL}/channels/create",
        data=data1,
        headers={'Content-Type': 'application/json'})
    req2 = urllib.request.Request(f"{BASE_URL}/channels/create",
        data=data2,
        headers={'Content-Type': 'application/json'})

    public = json.load(urllib.request.urlopen(req1))
    private = json.load(urllib.request.urlopen(req2))

    return [user1, user2, user3, public, private]

#########################################
# 			Testing: channel 	 		#
#########################################

# Owner inviting a user to a public channel
def test_channel_invite():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    # Public Channel
    data = json.dumps({
        'token': user1['token'],
        'channel_id': public['channel_id'],
        'u_id': user2['u_id']
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite",
        data=data,
        headers={'Content-Type': 'application/json'})
    payload = json.load(urllib.request.urlopen(req))

    assert payload == {}

    # Private Channel
    data = json.dumps({
        'token': user1['token'],
        'channel_id': private['channel_id'],
        'u_id': user2['u_id']
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite",
        data=data,
        headers={'Content-Type': 'application/json'})
    payload = json.load(urllib.request.urlopen(req))

    assert payload == {}

def test_channel_invite_invalid():
	reset_server()
	[user1, user2, user3, public, private] = fixture()

	# Public Channel
	data = json.dumps({
		'token': user1['token'],
		'channel_id': 3,
		'u_id': user2['u_id']
	}).encode('utf-8')
	req = urllib.request.Request(f"{BASE_URL}/channel/invite",
		data=data,
		headers={'Content-Type': 'application/json'})

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(req)

def test_channel_invite_unregistered_user():
	reset_server()
	[user1, user2, user3, public, private] = fixture()

	# Public Channel
	data = json.dumps({
		'token': 0,
		'channel_id': public['channel_id'],
		'u_id': user2['u_id']
	}).encode('utf-8')
	req = urllib.request.Request(f"{BASE_URL}/channel/invite",
		data=data,
		headers={'Content-Type': 'application/json'})

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(req)

def test_channel_invite_invalid_member():
    reset_server()
    [owner, member, non_member] = register_user1()

    data = json.dumps({
        'token': non_member['token'],
        'channel_id': 1,
        'u_id': member['u_id']
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/invite",
        data=data,
        headers={'Content-Type': 'application/json'})
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_details():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    # Public Channel
    req1 = urllib.request.urlopen(
        f"{BASE_URL}/channel/details?token={user1['token']}&channel_id={public['channel_id']}"
    )
    payload = json.load(req1)
    assert payload == {
        'name': 'Public Channel',
        'owner_members': [
            {
                'u_id': user1['u_id'] ,
                'name_first': 'aang',
                'name_last': 'airbender',
				'profile_img_url': None
            }
        ],
        'all_members': [
            {
                'u_id': user1['u_id'] ,
                'name_first': 'aang',
                'name_last': 'airbender',
				'profile_img_url': None
            }
        ],
    }

    # Private Channel
    req1 = urllib.request.urlopen(
        f"{BASE_URL}/channel/details?token={user1['token']}&channel_id={private['channel_id']}"
    )
    payload = json.load(req1)
    assert payload == {
        'name': 'Private Channel',
        'owner_members': [
            {
                'u_id': user1['u_id'] ,
                'name_first': 'aang',
                'name_last': 'airbender',
				'profile_img_url': None
            }
        ],
        'all_members': [
            {
                'u_id': user1['u_id'] ,
                'name_first': 'aang',
                'name_last': 'airbender',
				'profile_img_url': None
            }
        ],
    }

def test_channel_details_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()
    with pytest.raises(urllib.error.HTTPError):
        req1 = urllib.request.urlopen(
		f"{BASE_URL}/channel/details?token={owner['token']}&channel_id=3"
	)

def test_channel_details_invalid_user():
    reset_server()
    [owner, member, non_member] = register_user1()
    with pytest.raises(urllib.error.HTTPError):
        req1 = urllib.request.urlopen(
		f"{BASE_URL}/channel/details?token={non_member['token']}&channel_id=1"
	)

def test_channel_messages():
	reset_server()
	[user1, user2, user3, public, private] = fixture()

	# Public Channel

	# user 1 sending a message to public channel
	message = json.dumps({
		"token": user1['token'],
		"channel_id": public['channel_id'],
		"message": 'Wassup'
	}).encode('utf-8')
	timestamp = int(datetime.now().timestamp())
	req_msg = urllib.request.Request(
		f"{BASE_URL}/message/send", data=message, headers={'Content-Type': 'application/json'}
	)
	msg = json.load(urllib.request.urlopen(req_msg))

	# calling channel/messages
	req = urllib.request.urlopen(
		f"{BASE_URL}/channel/messages?token={user1['token']}&channel_id={public['channel_id']}&start=0"
	)
	payload = json.load(req)
	assert payload == {
		'messages': [
			{
				'message_id': msg['message_id'],
				'u_id': user1['u_id'],
				'message': 'Wassup',
				'time_created': timestamp,
				'reacts': [{
					'u_ids': [],
					'is_this_user_reacted': False,
					'react_id': 1
				}],
				'is_pinned': False
			}
		],
		'start': 0,
		'end': -1
	}

	# Private Channel

	# user 1 sending a message to public channel
	message = json.dumps({
		"token": user1['token'],
		"channel_id": private['channel_id'],
		"message": 'Wassup'
	}).encode('utf-8')
	timestamp = int(datetime.now().timestamp())
	req_msg = urllib.request.Request(f"{BASE_URL}/message/send",
		data=message,
		headers={'Content-Type': 'application/json'}
	)
	msg = json.load(urllib.request.urlopen(req_msg))

	# calling channel/messages
	req = urllib.request.urlopen(
		f"{BASE_URL}/channel/messages?token={user1['token']}&channel_id={private['channel_id']}&start=0"
	)
	payload = json.load(req)
	assert payload == {
		'messages': [
			{
				'message_id': msg['message_id'],
				'u_id': user1['u_id'],
				'message': 'Wassup',
				'time_created': timestamp,
				'reacts': [{
					'u_ids': [],
					'is_this_user_reacted': False,
					'react_id': 1
				}],
				'is_pinned': False
			}
		],
		'start': 0,
		'end': -1
	}
def test_channel_messages_invalid_channel():
    reset_server()
    [owner, member, non_member] = register_user1()

	# Public Channel

	# user 1 sending a message to public channel
    message = json.dumps({
        "token": owner['token'],
        "channel_id": 3,
        "message": 'Wassup'
    }).encode('utf-8')
    timestamp = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    req_msg = urllib.request.Request(
        f"{BASE_URL}/message/send", data=message, headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req_msg)

def test_channel_messages_invalid_count():
    reset_server()
    [owner, member, non_member] = register_user1()

    message = json.dumps({
        "token": owner['token'],
        "channel_id": 1,
        "message": 'Wassup'
    }).encode('utf-8')
    timestamp = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    req_msg = urllib.request.Request(
        f"{BASE_URL}/message/send", data=message, headers={'Content-Type': 'application/json'}
    )
    json.load(urllib.request.urlopen(req_msg))
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(f"{BASE_URL}/channel/messages?token={owner['token']}&channel_id=1&start=5")

def test_channel_messages_invalid_member():
    reset_server()
    [owner, member, non_member] = register_user1()

    message = json.dumps({
        "token": non_member['token'],
        "channel_id": 1,
        "message": 'Wassup'
    }).encode('utf-8')
    timestamp = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    req_msg = urllib.request.Request(
        f"{BASE_URL}/message/send", data=message, headers={'Content-Type': 'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req_msg)

def test_channel_leave():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    # Public Channel
    data = json.dumps({
        "token": user1['token'],
        "channel_id": public['channel_id']
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/leave",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}


    # Private Channel
    data = json.dumps({
        "token": user1['token'],
        "channel_id": private['channel_id']
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/leave",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

def test_channel_leave_invalid_channel():
	reset_server()
	[owner, member, non_member] = register_user1()
	data = json.dumps({
		"token": member['token'],
		"channel_id": 2
	}).encode('utf-8')
	req = urllib.request.Request(f"{BASE_URL}/channel/leave",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(req)

def test_channel_leave_invalid_member():
	reset_server()
	[owner, member, non_member] = register_user1()
	data = json.dumps({
		"token": non_member['token'],
		"channel_id": 1
	}).encode('utf-8')
	req = urllib.request.Request(f"{BASE_URL}/channel/leave",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(req)

def test_channel_join():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    # Public Channel
    data = json.dumps({
        "token": user2['token'],
        "channel_id": public['channel_id']
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

def test_channel_join_invalid_channel():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

	# Public Channel
    data = json.dumps({
        "token": user2['token'],
        "channel_id": 3
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join",
        data=data,
        headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_join_private_channel():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

	# Public Channel
    data = json.dumps({
        "token": user2['token'],
        "channel_id": 2
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/join",
        data=data,
        headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_addowner():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    # Public Channel
    data = json.dumps({
        'token': user1['token'],
        'channel_id': public['channel_id'],
        'u_id': user2['u_id']
    }).encode('utf-8')

    # Add as member
    req = urllib.request.Request(f"{BASE_URL}/channel/invite",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    json.load(urllib.request.urlopen(req))

    # Add as owner
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

    # Private Channel
    data = json.dumps({
        'token': user1['token'],
        'channel_id': private['channel_id'],
        'u_id': user2['u_id']
    }).encode('utf-8')
    # Add as member
    req = urllib.request.Request(f"{BASE_URL}/channel/invite",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    json.load(urllib.request.urlopen(req))

    # Add as owner
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

def test_channel_addowner_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()
    data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'u_id': owner['u_id']
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_addowner_invalid_channel():
    reset_server()
    [owner, member, non_member] = register_user1()
    data = json.dumps({
		'token': owner['token'],
		'channel_id': 3,
		'u_id': member['u_id']
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_addowner_invalid_owner():
    reset_server()
    [owner, member, non_member] = register_user1()
    data = json.dumps({
		'token': member['token'],
		'channel_id': 1,
		'u_id': member['u_id']
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_removeowner():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    # Public Channel
    data = json.dumps({
        'token': user1['token'],
        'channel_id': public['channel_id'],
        'u_id': user2['u_id']
    }).encode('utf-8')

    # Add as member
    req = urllib.request.Request(f"{BASE_URL}/channel/invite",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    json.load(urllib.request.urlopen(req))

    # Add as owner
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner",
        data=data,
        headers={'Content-Type': 'application/json'})
    json.load(urllib.request.urlopen(req))

    # Remove as owner
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

    # Private Channel
    data = json.dumps({
        'token': user1['token'],
        'channel_id': private['channel_id'],
        'u_id': user2['u_id']
    }).encode('utf-8')

    # Add as member
    req = urllib.request.Request(f"{BASE_URL}/channel/invite",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    json.load(urllib.request.urlopen(req))

    # Add as owner
    req = urllib.request.Request(f"{BASE_URL}/channel/addowner",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    json.load(urllib.request.urlopen(req))

    # Remove as owner
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

def test_channel_removeowner_invalid_channel():
    reset_server()
    [owner, member, non_member] = register_user1()
    data = json.dumps({
		'token': owner['token'],
		'channel_id': 3,
		'u_id': owner['u_id']
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_removeowner_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()
    data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'u_id': member['u_id']
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_channel_removeowner_not_owner():
    reset_server()
    [owner, member, non_member] = register_user1()
    data = json.dumps({
		'token': member['token'],
		'channel_id': 1,
		'u_id': owner['u_id']
	}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/channel/removeowner",
		data=data,
		headers={'Content-Type': 'application/json'}
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

#########################################
# 			Testing: auth 				#
#########################################
def test_auth_register():
    ## test wrong email
    reset_server()
    user_data = json.dumps({
        'email': 'Jan.edu.au',
        'password': '123456',
        'name_first': 'Jan',
        'name_last': 'Zhang'}).encode('utf-8')

    create_user = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(create_user)

##test wrong password
    user_data = json.dumps({
        'email': 'Jan@unsw.edu.au',
        'password': '12',
        'name_first': 'Jan',
        'name_last': 'Zhang'}).encode('utf-8')

    create_user = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(create_user)

##test wrong first name
    user_data = json.dumps({
        'email': 'Jan@unsw.edu.au',
        'password': '123456',
        'name_first': '',
        'name_last': 'Zhang'}).encode('utf-8')

    create_user = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(create_user)

##test wrong last name
    user_data = json.dumps({
        'email': 'Jan@unsw.edu.au',
        'password': '123456',
        'name_first': 'Jan',
        'name_last': ''}).encode('utf-8')

    create_user = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(create_user)


    # Create a user
    reset_server()
    user_data = json.dumps({
        'email': 'Jan@unsw.edu.au',
        'password': '123456',
        'name_first': 'Jan',
        'name_last': 'Zhang'}).encode('utf-8')
    create_user = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    payload = json.load(urllib.request.urlopen(create_user))

    # User's token
    token = payload['token']
    assert payload == {
        'u_id' : 1,
        'token': token
    }

##test repeat email
    user_data = json.dumps({
        'email': 'Jan@unsw.edu.au',
        'password': '123456',
        'name_first': 'Jane',
        'name_last': 'Zhang'}).encode('utf-8')

    create_user = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(create_user)

    ##test logout
    user_data = json.dumps({'token' : token}).encode('utf-8')

    user_logout = urllib.request.Request(
        f"{BASE_URL}/auth/logout",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    payload = json.load(urllib.request.urlopen(user_logout))
    assert payload['is_success'] == True

def test_auth_login():
    user_data = json.dumps({
        'email': 'Jan@unsw.edu.au',
        'password': '123456',
    }).encode('utf-8')

    login_user = urllib.request.Request(
        f"{BASE_URL}/auth/login",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    payload = json.load(urllib.request.urlopen(login_user))

    # User's token
    token = payload['token']
    assert payload == {
        'u_id' : 1,
        'token': token
    }

#########################################
# 			Testing: message 			#
#########################################

def register_user1(): 

	# Create a user
    reset_server()
    user_data = json.dumps({
        'email': 'martinle@unsw.edu.au',
        'password': 'abc123',
        'name_first': 'Martin',
        'name_last': 'Le'}).encode('utf-8')
    create_user_1 = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    owner = json.load(urllib.request.urlopen(create_user_1))

    user_data_2 = json.dumps({
        'email': 'randomUser@unsw.edu.au',
        'password': 'abc123',
        'name_first': 'Random',
        'name_last': 'User'}).encode('utf-8')
    create_user_2 = urllib.request.Request(
		f"{BASE_URL}/auth/register",
		data=user_data_2,
		headers={'Content-Type': 'application/json'},
		method='POST'
	)
    member = json.load(urllib.request.urlopen(create_user_2))

    user_data_3 = json.dumps({
        'email': 'nonMember@unsw.edu.au',
        'password': 'abc123',
        'name_first': 'Nota',
        'name_last': 'Member'}).encode('utf-8')
    create_user_3 = urllib.request.Request(
        f"{BASE_URL}/auth/register",
        data=user_data_3,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    non_member = json.load(urllib.request.urlopen(create_user_3))

	# Create a channel
    channel_data = json.dumps({
        'token': owner['token'],
        'name': 'COMP1531',
        'is_public': True
    }).encode('utf-8')
    create_channel = urllib.request.Request(
        f"{BASE_URL}/channels/create",
        data=channel_data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(create_channel))

	# Join a channel
    join_data = json.dumps({
        'token': member['token'],
        'channel_id': 1
    }).encode('utf-8')
    join_channel = urllib.request.Request(
        f"{BASE_URL}/channel/join",
        data=join_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(join_channel))

	# Return the user's token
    return [owner, member, non_member]

# Testing a valid server return with message_send_later
def test_send_message():
	reset_server()
	# Acquire token from user
	[owner, member, non_member] = register_user1()
	# send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))
	# check result
	assert payload['message_id'] == 1

# Testing a valid server return with message_send_later
def test_send_message_later():
# Testing a valid server return with message_send_later
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    time_sent = int(datetime.now().timestamp() + 3)

    # Send a message
    message_data = json.dumps({
        'token': user1['token'],
        'channel_id': 1,
        'message': "Hello",
        'time_sent': time_sent
    }).encode('utf-8')
    send_later = urllib.request.Request(
        f"{BASE_URL}/message/sendlater",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    threading.Thread(
        target=message_sendlater_thread,
        args=(3, send_later, 1))

def message_sendlater_thread(time, request, message_id):
    sleep(time)
    payload = json.load(urllib.request.urlopen(request))
    # Check result
    assert payload['message_id'] == message_id

# Testing a valid server return with message_react
def test_message_react():
	reset_server()
	[owner, member, non_member] = register_user1()

	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	react_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'react_id' : 1
	}).encode('utf-8')
	send_react = urllib.request.Request(
		f"{BASE_URL}/message/react",
		data=react_data,
		headers={'Content-Type':'application/json'}
	)

	payload = json.load(urllib.request.urlopen(send_react))
	assert payload == {}

# Testing a valid server return with message_unreact
def test_message_unreact():
	# Reset server
	reset_server()

	# Acquire token from user
	[owner, member, non_member] = register_user1()

	# Send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# React message
	react_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'react_id' : 1
	}).encode('utf-8')
	send_react = urllib.request.Request(
		f"{BASE_URL}/message/react",
		data=react_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send_react))

	# Unreact message
	unreact_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'react_id': 1
	}).encode('utf-8')
	send_unreact = urllib.request.Request(
		f"{BASE_URL}/message/unreact",
		data=unreact_data,
		headers={'Content-Type': 'application/json'
	})
	payload = json.load(urllib.request.urlopen(send_unreact))

	# Check result
	assert payload == {}

# Testing a valid server return with message_pin
def test_message_pin():
	# Reset server
	reset_server()

	# Acquire token from user
	[owner, member, non_member] = register_user1()

	# Send message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# Pin message
	pin_data = json.dumps({
		'token': owner['token'],
		'message_id': 1
	}).encode('utf-8')
	send_pin = urllib.request.Request(
		f"{BASE_URL}/message/pin",
		data=pin_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send_pin))

	# Check result
	assert payload == {}

# Testing a valid server return with message_unpin
def test_message_unpin():
	# Reset server
	reset_server()

	# Acquire user token
	[owner, member, non_member] = register_user1()

	# Send Message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# Pin message
	pin_data = json.dumps({
		'token': owner['token'],
		'message_id': 1
	}).encode('utf-8')
	send_pin = urllib.request.Request(
		f"{BASE_URL}/message/pin",
		data=pin_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send_pin))

	# Unpin message
	unpin_data = json.dumps({
		'token': owner['token'],
		'message_id': 1
	}).encode('utf-8')
	send_unpin = urllib.request.Request(
		f"{BASE_URL}/message/unpin",
		data=unpin_data,
		headers={'Content-Type': 'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send_unpin))

	# Check result
	assert payload == {}

# Testing a valid server return with message_remove
def test_message_remove():
	# Reset server
	reset_server()

	# Acquire user token
	[owner, member, non_member] = register_user1()

	# Send a messaage
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# Remove the sent message
	remove_data = json.dumps({
		'token': owner['token'],
		'message_id': 1
	}).encode('utf-8')
	send_remove = urllib.request.Request(
		f"{BASE_URL}/message/remove",
		data=remove_data,
		headers={'Content-Type': 'application/json'},
		method='DELETE'
	)
	payload = json.load(urllib.request.urlopen(send_remove))
	# Check result
	assert payload == {}

# Testing a valid server return with message_edit
def test_message_edit():
	# Reset the server
	reset_server()
	# Acquire user token
	[owner, member, non_member] = register_user1()

	# Send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# Edit the message
	edit_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'message': "Edited Message"
	}).encode('utf-8')
	send_edit = urllib.request.Request(
		f"{BASE_URL}/message/edit",
		data=edit_data,
		headers={'Content-Type': 'application/json'},
		method='PUT'
	)
	payload = json.load(urllib.request.urlopen(send_edit))
	# Check result
	assert payload == {}

def test_message_send_invalid():
	reset_server()
	# Acquire token from user
	[owner, member, non_member] = register_user1()
	# send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "a" * 1001
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	# check result
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send)

def test_message_send_invalid_user():
	reset_server()
	# Acquire token from user
	[owner, member, non_member] = register_user1()
	# send a message
	message_data = json.dumps({
		'token': non_member['token'],
		'channel_id': 1,
		'message': "a"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	# check result
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send)

def test_message_send_later_invalid():
	# Testing a valid server return with message_send_later
	reset_server()
	[user1, user2, user3, public, private] = fixture()

	time_sent = int(datetime.now().timestamp() - 3)

	# Send a message
	message_data = json.dumps({
		'token': user1['token'],
		'channel_id': 1,
		'message': "Hello",
		'time_sent': time_sent
	}).encode('utf-8')
	send_later = urllib.request.Request(
		f"{BASE_URL}/message/sendlater",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	threading.Thread(
		target=message_sendlater_thread,
		args=(-3, send_later, 1))

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_later)

def test_message_send_later_invalid_channel():
	# Testing a valid server return with message_send_later
	reset_server()
	[user1, user2, user3, public, private] = fixture()

	time_sent = int(datetime.now().timestamp() + 3)

	# Send a message
	message_data = json.dumps({
		'token': user1['token'],
		'channel_id': 50,
		'message': "Hello",
		'time_sent': time_sent
	}).encode('utf-8')
	send_later = urllib.request.Request(
		f"{BASE_URL}/message/sendlater",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	threading.Thread(
		target=message_sendlater_thread,
		args=(3, send_later, 50))

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_later)

def test_message_send_later_invalid_member():
	reset_server()
	[owner, member, non_member] = register_user1()

	time_sent = int(datetime.now().timestamp() + 3)

	# Send a message
	message_data = json.dumps({
		'token': non_member['token'],
		'channel_id': 50,
		'message': "Hello",
		'time_sent': time_sent
	}).encode('utf-8')
	send_later = urllib.request.Request(
		f"{BASE_URL}/message/sendlater",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	threading.Thread(
		target=message_sendlater_thread,
		args=(3, send_later, 50))

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_later)

def test_message_react_invalid():
	reset_server()
	[owner, member, non_member] = register_user1()

	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	react_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'react_id' : 2
	}).encode('utf-8')
	send_react = urllib.request.Request(
		f"{BASE_URL}/message/react",
		data=react_data,
		headers={'Content-Type':'application/json'}
	)

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_react)

def test_message_react_already_reacted():
	reset_server()
	[owner, member, non_member] = register_user1()

	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	react_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'react_id' : 1
	}).encode('utf-8')
	send_react = urllib.request.Request(
		f"{BASE_URL}/message/react",
		data=react_data,
		headers={'Content-Type':'application/json'}
	)
	json.load(urllib.request.urlopen(send_react))
	send_react_2 = urllib.request.Request(
		f"{BASE_URL}/message/react",
		data=react_data,
		headers={'Content-Type':'application/json'}
	)

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_react_2)

def test_message_react_no_message():
	reset_server()
	[owner, member, non_member] = register_user1()

	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	react_data = json.dumps({
		'token': owner['token'],
		'message_id': 2,
		'react_id' : 2
	}).encode('utf-8')
	send_react = urllib.request.Request(
		f"{BASE_URL}/message/react",
		data=react_data,
		headers={'Content-Type':'application/json'}
	)

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_react)

def test_message_unreact_invalid():
    # Reset server
	reset_server()

	# Acquire token from user
	[owner, member, non_member] = register_user1()

	# Send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# React message
	react_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'react_id' : 1
	}).encode('utf-8')
	send_react = urllib.request.Request(
		f"{BASE_URL}/message/react",
		data=react_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send_react))

	# Unreact message
	unreact_data = json.dumps({
		'token': owner['token'],
		'message_id': 1,
		'react_id': 2
	}).encode('utf-8')
	send_unreact = urllib.request.Request(
		f"{BASE_URL}/message/unreact",
		data=unreact_data,
		headers={'Content-Type': 'application/json'
	})
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_unreact)

def test_message_unreact_invalid_message():
    # Reset server
    reset_server()

    # Acquire token from user
    [owner, member, non_member] = register_user1()

    # Send a message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

    # React message
    react_data = json.dumps({
        'token': owner['token'],
        'message_id': 1,
        'react_id' : 1
    }).encode('utf-8')
    send_react = urllib.request.Request(
        f"{BASE_URL}/message/react",
        data=react_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send_react))

    # Unreact message
    unreact_data = json.dumps({
        'token': owner['token'],
        'message_id': 3,
        'react_id': 1
    }).encode('utf-8')
    send_unreact = urllib.request.Request(
        f"{BASE_URL}/message/unreact",
        data=unreact_data,
        headers={'Content-Type': 'application/json'
    })
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_unreact)

def test_message_unreact_unreacted():
    # Reset server
    reset_server()

    # Acquire token from user
    [owner, member, non_member] = register_user1()

    # Send a message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

    # Unreact message
    unreact_data = json.dumps({
        'token': owner['token'],
        'message_id': 1,
        'react_id': 1
    }).encode('utf-8')
    send_unreact = urllib.request.Request(
        f"{BASE_URL}/message/unreact",
        data=unreact_data,
        headers={'Content-Type': 'application/json'
    })
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_unreact)

def test_message_pin_invalid():
	# Reset server
    reset_server()

	# Acquire token from user
    [owner, member, non_member] = register_user1()

	# Send message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

	# Pin message
    pin_data = json.dumps({
        'token': owner['token'],
        'message_id': 2
    }).encode('utf-8')
    send_pin = urllib.request.Request(
        f"{BASE_URL}/message/pin",
        data=pin_data,
        headers={'Content-Type':'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_pin)

def test_message_pin_already_pinned():
		# Reset server
	reset_server()

	# Acquire token from user
	[owner, member, non_member] = register_user1()

	# Send message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# Pin message
	pin_data = json.dumps({
		'token': owner['token'],
		'message_id': 1
	}).encode('utf-8')
	send_pin = urllib.request.Request(
		f"{BASE_URL}/message/pin",
		data=pin_data,
		headers={'Content-Type':'application/json'}
	)
	json.load(urllib.request.urlopen(send_pin))
	send_pin_2 = urllib.request.Request(
		f"{BASE_URL}/message/pin",
		data=pin_data,
		headers={'Content-Type':'application/json'}
	)
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_pin_2)

def test_message_pin_invalid_member():
    reset_server()

	# Acquire token from user
    [owner, member, non_member] = register_user1()

	# Send message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

	# Pin message
    pin_data = json.dumps({
        'token': non_member['token'],
        'message_id': 1
    }).encode('utf-8')
    send_pin = urllib.request.Request(
        f"{BASE_URL}/message/pin",
        data=pin_data,
        headers={'Content-Type':'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_pin)

def test_message_pin_not_owner():
    reset_server()

	# Acquire token from user
    [owner, member, non_member] = register_user1()

	# Send message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

	# Pin message
    pin_data = json.dumps({
        'token': member['token'],
        'message_id': 1
    }).encode('utf-8')
    send_pin = urllib.request.Request(
        f"{BASE_URL}/message/pin",
        data=pin_data,
        headers={'Content-Type':'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_pin)

def test_message_unpin_invalid():
    reset_server()

    # Acquire user token
    [owner, member, non_member] = register_user1()

    # Send Message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

    # Pin message
    pin_data = json.dumps({
        'token': owner['token'],
        'message_id': 1
    }).encode('utf-8')
    send_pin = urllib.request.Request(
        f"{BASE_URL}/message/pin",
        data=pin_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send_pin))

    # Unpin message
    unpin_data = json.dumps({
        'token': owner['token'],
        'message_id': 2
    }).encode('utf-8')
    send_unpin = urllib.request.Request(
        f"{BASE_URL}/message/unpin",
        data=unpin_data,
        headers={'Content-Type': 'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_unpin)

def test_message_unpin_already_unpinned():
    reset_server()

	# Acquire user token
    [owner, member, non_member] = register_user1()

    # Send Message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

    # Pin message
    pin_data = json.dumps({
        'token': owner['token'],
        'message_id': 1
    }).encode('utf-8')
    send_pin = urllib.request.Request(
        f"{BASE_URL}/message/pin",
        data=pin_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send_pin))

    # Unpin message
    unpin_data = json.dumps({
        'token': owner['token'],
        'message_id': 1
    }).encode('utf-8')
    send_unpin_1 = urllib.request.Request(
        f"{BASE_URL}/message/unpin",
        data=unpin_data,
        headers={'Content-Type': 'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send_unpin_1))

    send_unpin_2 = urllib.request.Request(
        f"{BASE_URL}/message/unpin",
        data=unpin_data,
        headers={'Content-Type': 'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_unpin_2)

def test_message_unpin_invalid_member():
    reset_server()

    # Acquire user token
    [owner, member, non_member] = register_user1()

    # Send Message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

    # Pin message
    pin_data = json.dumps({
        'token': owner['token'],
        'message_id': 1
    }).encode('utf-8')
    send_pin = urllib.request.Request(
        f"{BASE_URL}/message/pin",
        data=pin_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send_pin))

    # Unpin message
    unpin_data = json.dumps({
        'token': non_member['token'],
        'message_id': 1
    }).encode('utf-8')
    send_unpin = urllib.request.Request(
        f"{BASE_URL}/message/unpin",
        data=unpin_data,
        headers={'Content-Type': 'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_unpin)

def test_message_unpin_not_owner():
    reset_server()

    # Acquire user token
    [owner, member, non_member] = register_user1()

    # Send Message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

    # Pin message
    pin_data = json.dumps({
        'token': owner['token'],
        'message_id': 1
    }).encode('utf-8')
    send_pin = urllib.request.Request(
        f"{BASE_URL}/message/pin",
        data=pin_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send_pin))

    # Unpin message
    unpin_data = json.dumps({
        'token': member['token'],
        'message_id': 2
    }).encode('utf-8')
    send_unpin = urllib.request.Request(
        f"{BASE_URL}/message/unpin",
        data=unpin_data,
        headers={'Content-Type': 'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(send_unpin)

def test_message_remove_invalid():
    # Reset server
	reset_server()

	# Acquire user token
	[owner, member, non_member] = register_user1()

	# Send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# Remove the sent message
	remove_data = json.dumps({
		'token': owner['token'],
		'message_id': 1
	}).encode('utf-8')
	send_remove_1 = urllib.request.Request(
		f"{BASE_URL}/message/remove",
		data=remove_data,
		headers={'Content-Type': 'application/json'},
		method='DELETE'
	)
	json.load(urllib.request.urlopen(send_remove_1))

	send_remove_2 = urllib.request.Request(
		f"{BASE_URL}/message/remove",
		data=remove_data,
		headers={'Content-Type': 'application/json'},
		method='DELETE'
	)
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_remove_2)

def test_message_remove_invalid_access():
    # Reset server
	reset_server()

	# Acquire user token
	[owner, member, non_member] = register_user1()

	# Send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	# Remove the sent message
	remove_data = json.dumps({
		'token': member['token'],
		'message_id': 1
	}).encode('utf-8')
	send_remove = urllib.request.Request(
		f"{BASE_URL}/message/remove",
		data=remove_data,
		headers={'Content-Type': 'application/json'},
		method='DELETE'
	)
	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(send_remove)

def test_message_edit_invalid_access():
    # Reset the server
    reset_server()
	# Acquire user token
    [owner, member, non_member] = register_user1()

	# Send a message
    message_data = json.dumps({
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello"
    }).encode('utf-8')
    send = urllib.request.Request(
        f"{BASE_URL}/message/send",
        data=message_data,
        headers={'Content-Type':'application/json'}
    )
    payload = json.load(urllib.request.urlopen(send))

	# Edit the message
    edit_data = json.dumps({
        'token': member['token'],
        'message_id': 1,
        'message': "Edited Message"
    }).encode('utf-8')
    send_edit = urllib.request.Request(
        f"{BASE_URL}/message/edit",
        data=edit_data,
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    with pytest.raises(urllib.error.HTTPError):
	    urllib.request.urlopen(send_edit)

#########################################
# 			Testing: search 			#
#########################################

def test_search():
	reset_server()

	# Acquire token from user
	[owner, member, non_member] = register_user1()

	# Send a message
	message_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
	send = urllib.request.Request(
		f"{BASE_URL}/message/send",
		data=message_data,
		headers={'Content-Type':'application/json'}
	)
	payload = json.load(urllib.request.urlopen(send))

	data = urllib.parse.urlencode({
		'token': owner['token'],
		'query_str': "hello"
	})

	search_request = urllib.request.urlopen(f"{BASE_URL}/search?{data}")
	payload = json.load(search_request)

	assert payload['messages'] == []

#########################################
# 			Testing: channels			#
#########################################

def test_channels(): 

	# Create a user
	reset_server()
	user_data = json.dumps({
		'email': 'Jan@unsw.edu.au',
		'password': '123456',
		'name_first': 'Jan',
		'name_last': 'Zhang'}).encode('utf-8')
	create_user = urllib.request.Request(
		f"{BASE_URL}/auth/register",
		data=user_data,
		headers={'Content-Type': 'application/json'},
		method='POST'
	)
	payload = json.load(urllib.request.urlopen(create_user))

	# User's token
	token = payload['token']

	# Create a channel
	# name is not correct
	channel_data = json.dumps({
		'token': token,
		'name': 'COMP1531COMP1531COMP1531COMP1531',
		'is_public': True
	}).encode('utf-8')
	create_channel = urllib.request.Request(
		f"{BASE_URL}/channels/create",
		data=channel_data,
		headers={'Content-Type': 'application/json'}
	)

	with pytest.raises(urllib.error.HTTPError):
		urllib.request.urlopen(create_user)

	channel_data = json.dumps({
		'token': token,
		'name': 'COMP1531',
		'is_public': True
	}).encode('utf-8')
	create_channel = urllib.request.Request(
		f"{BASE_URL}/channels/create",
		data=channel_data,
		headers={'Content-Type': 'application/json'}
	)

	payload = json.load(urllib.request.urlopen(create_channel))
	assert payload == {
		'channel_id' : 1
	}

	req = urllib.request.urlopen(f"{BASE_URL}/channels/list?token={token}")

	payload = json.load(req)

	assert payload ==  {'channels': [{'channel_id': 1, 'name': 'COMP1531'}]}

	channel_data = json.dumps({
		'token': token,
		'name': 'COMP3411',
		'is_public': True
	}).encode('utf-8')
	create_channel = urllib.request.Request(
		f"{BASE_URL}/channels/create",
		data=channel_data,
		headers={'Content-Type': 'application/json'}
	)

	payload = json.load(urllib.request.urlopen(create_channel))

	channel_data = json.dumps({
		'token': token,
		'name': 'COMP1521',
		'is_public': False
	}).encode('utf-8')
	create_channel = urllib.request.Request(
		f"{BASE_URL}/channels/create",
		data=channel_data,
		headers={'Content-Type': 'application/json'}
	)

	payload = json.load(urllib.request.urlopen(create_channel))

	req = urllib.request.urlopen(f"{BASE_URL}/channels/listall?token={token}")

	payload = json.load(req)

	assert payload ==  {
		'channels': [{
			'channel_id': 1, 
			'name': 'COMP1531'
		},{
			'channel_id': 2, 
			'name': 'COMP3411'
		},{
			'channel_id': 3,
			'name': 'COMP1521'
		}]
	}

###############################
# Testing Main Function: User #
###############################
'''
def test_user_profile_valid():

    reset_server()
    [owner, member, non_member] = register_user1()
    profile_data = json.dumps({
		'token': owner['token'],
		'u_id': '1'
	}).encode('utf-8')
    get_profile = urllib.request.Request(
		f"{BASE_URL}/user/profile",
		data=profile_data,
		headers={'Content-Type':'application/json'},
		method='GET'
	)
    payload = json.load(urllib.request.urlopen(get_profile))
    assert payload['name_first'] == 'Martin'
'''
def test_user_profile_invalid_user():
    reset_server()
    [owner, member, non_member] = register_user1()

    profile_data = json.dumps({
        'token': owner['token'],
        'u_id': 10
    }).encode('utf-8')
    get_profile = urllib.request.Request(
        f"{BASE_URL}/user/profile",
        data=profile_data,
        headers={'Content-Type':'application/json'}
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(get_profile)

def test_user_profile_setname_valid():
    reset_server()
    [owner, member, non_member] = register_user1()

    name_data = json.dumps({
		'token': member['token'],
		'name_first': 'New',
		'name_last': 'Name'
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/setname",
		data=name_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

def test_user_profile_setname_namefirst_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()

    name_data = json.dumps({
		'token': owner['token'],
		'name_first': 'a'*100,
		'name_last': 'Le'
    }).encode('utf-8')
    get_name = urllib.request.Request(
		f"{BASE_URL}/user/profile/setname",
		data=name_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(get_name)
def test_user_profile_setname_namelast_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()

    name_data = json.dumps({
		'token': owner['token'],
		'name_first': 'Martin',
		'name_last': 'a'*100
    }).encode('utf-8')
    get_name = urllib.request.Request(
		f"{BASE_URL}/user/profile/setname",
		data=name_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
    )
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(get_name)

def test_user_profile_setemail_valid():
    reset_server()
    [owner, member, non_member] = register_user1()

    email_data = json.dumps({
		'token': member['token'],
		'email': 'ml@gmail.com'
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/setemail",
		data=email_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}
def test_user_profile_setemail_email_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()

    email_data = json.dumps({
		'token': member['token'],
		'email': 'ml@gmail'
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/setemail",
		data=email_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
def test_user_profile_setemail_used():
    reset_server()
    [owner, member, non_member] = register_user1()

    email_data = json.dumps({
		'token': member['token'],
		'email': 'randomUser@unsw.edu.au'
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/setemail",
		data=email_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)
def test_user_profile_sethandle_valid():
    reset_server()
    [owner, member, non_member] = register_user1()

    handle_data = json.dumps({
		'token': member['token'],
		'handle_str': 'ILoveComp'
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/sethandle",
		data=handle_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}
def test_user_profile_sethandle_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()

    handle_data = json.dumps({
		'token': member['token'],
		'handle_str': 'a'*30
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/sethandle",
		data=handle_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    with pytest.raises(urllib.error.HTTPError):
        json.load(urllib.request.urlopen(req))
def test_user_profile_sethandle_used():
    reset_server()
    [owner, member, non_member] = register_user1()

    handle_data = json.dumps({
		'token': owner['token'],
		'handle_str': 'iLoveComp'
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/sethandle",
		data=handle_data,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    json.load(urllib.request.urlopen(req))

    handle_data2 = json.dumps({
		'token': member['token'],
		'handle_str': 'iLoveComp'
	}).encode('utf-8')
    req2 = urllib.request.Request(
		f"{BASE_URL}/user/profile/sethandle",
		data=handle_data2,
		headers={'Content-Type':'application/json'},
		method='PUT'
	)
    with pytest.raises(urllib.error.HTTPError):
        json.load(urllib.request.urlopen(req2))

def test_user_profile_uploadphoto_valid():
    reset_server()
    [owner, member, non_member] = register_user1()

    pic_data = json.dumps({
		'token': owner['token'],
		'img_url': 'https://api.time.com/wp-content/uploads/2015/01/harry-potter-illustrations-04.jpg',
		'x_start': 0,
		'y_start': 200,
		'x_end' : 1800,
		'y_end' : 2000
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/uploadphoto",
		data=pic_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    payload = json.load(urllib.request.urlopen(req))
    assert payload == {}

def tests_user_profile_uploadphoto_invalid():
    reset_server()
    [owner, member, non_member] = register_user1()

    pic_data = json.dumps({
		'token': owner['token'],
		'img_url': 'https://api.time.com/wp-content/uploads/2020/01/harry-potter-illustrations-04.jpg',
		'x_start': 0,
		'y_start': 200,
		'x_end' : 1800,
		'y_end' : 2000
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/uploadphoto",
		data=pic_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        json.load(urllib.request.urlopen(req))

def test_user_profile_uploadphoto_invalid_dimensions():
    reset_server()
    [owner, member, non_member] = register_user1()

    pic_data = json.dumps({
		'token': owner['token'],
		'img_url': 'https://api.time.com/wp-content/uploads/2015/01/harry-potter-illustrations-04.jpg',
		'x_start': 10000,
		'y_start': 10000,
		'x_end' : 200,
		'y_end' : 300
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/uploadphoto",
		data=pic_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        json.load(urllib.request.urlopen(req))

def test_user_profile_uploadphoto_invalid_type():
    reset_server()
    [owner, member, non_member] = register_user1()

    pic_data = json.dumps({
		'token': owner['token'],
		'img_url': 'https://vignette.wikia.nocookie.net/parsel/images/6/65/Severus_Snape.png',
		'x_start': 0,
		'y_start': 200,
		'x_end' : 1800,
		'y_end' : 2000
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/user/profile/uploadphoto",
		data=pic_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        json.load(urllib.request.urlopen(req))

###################################
# Testing Main Function: StandUp #
###################################
def test_standup_start_valid():
    reset_server()
    [owner, member, non_member] = register_user1()

    standup_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'length': 300
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    payload = json.load(urllib.request.urlopen(req))
    assert payload['time_finish'] != None

def test_standup_start_invalid_channel():
    reset_server()
    [owner, member, non_member] = register_user1()

    standup_data = json.dumps({
		'token': owner['token'],
		'channel_id': 5,
		'length': 300
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req)

def test_standup_start_already_active():
    reset_server()
    [owner, member, non_member] = register_user1()

    standup1_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'length': 300
	}).encode('utf-8')
    req1 = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup1_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    urllib.request.urlopen(req1)

    standup2_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'length': 300
	}).encode('utf-8')
    req2 = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup2_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)
'''
def test_standup_active_valid():
    reset_server()
    [user1, user2, user3, public, private] = fixture()
    channel_id = public['channel_id']
    standup1_data = json.dumps({
		'token': user1['token'],
		'channel_id': channel_id,
		'length': 300
	}).encode('utf-8')
    req1 = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup1_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    json.load(urllib.request.urlopen(req1))

    data1 = json.dumps({
		'token': user1['token'],
		'channel_id': channel_id
	}).encode('utf-8')
    check_active = urllib.request.Request(
		f"{BASE_URL}/standup/active",
		data=data1,
		headers={'Content-Type':'application/json'},
		method='GET'
	)
    json.load(urllib.request.urlopen(check_active))
    #assert payload['is_active'] == True
'''
def test_standup_active_invalid_channel():
    reset_server()
    [user1, user2, user3, public, private] = fixture()

    standup1_data = json.dumps({
		'token': user1['token'],
		'channel_id': public['channel_id'],
		'length': 300
	}).encode('utf-8')
    req1 = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup1_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    json.load(urllib.request.urlopen(req1))

    active_data = json.dumps({
		'token': user1['token'],
		'channel_id': 4
	}).encode('utf-8')
    check_active = urllib.request.Request(
		f"{BASE_URL}/standup/active",
		data=active_data,
		headers={'Content-Type':'application/json'},
		method='GET'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(check_active)
def test_startup_send_valid():
    reset_server()
    [owner, member, non_member] = register_user1()

    standup_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'length': 300
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    json.load(urllib.request.urlopen(req))

    send_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'message': "Hello"
	}).encode('utf-8')
    req2 = urllib.request.Request(
		f"{BASE_URL}/standup/send",
		data=send_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    payload = json.load(urllib.request.urlopen(req2))
    assert payload == {}

def test_standup_send_invalid_channel():
    reset_server()
    [owner, member, non_member] = register_user1()

    standup_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'length': 300
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    json.load(urllib.request.urlopen(req))

    send_data = json.dumps({
		'token': owner['token'],
		'channel_id': 5,
		'message': "Hello"
	}).encode('utf-8')
    req2 = urllib.request.Request(
		f"{BASE_URL}/standup/send",
		data=send_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_standup_send_invalid_message():
    reset_server()
    [owner, member, non_member] = register_user1()

    standup_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'length': 300
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    json.load(urllib.request.urlopen(req))

    send_data = json.dumps({
		'token': owner['token'],
		'channel_id': 5,
		'message': "a" * 1001
	}).encode('utf-8')
    req2 = urllib.request.Request(
		f"{BASE_URL}/standup/send",
		data=send_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)

def test_standup_send_not_in_channel():
    reset_server()
    [owner, member, non_member] = register_user1()

    standup_data = json.dumps({
		'token': owner['token'],
		'channel_id': 1,
		'length': 300
	}).encode('utf-8')
    req = urllib.request.Request(
		f"{BASE_URL}/standup/start",
		data=standup_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    json.load(urllib.request.urlopen(req))

    send_data = json.dumps({
		'token': non_member['token'],
		'channel_id': 1,
		'message': "a" * 1001
	}).encode('utf-8')
    req2 = urllib.request.Request(
		f"{BASE_URL}/standup/send",
		data=send_data,
		headers={'Content-Type':'application/json'},
		method='POST'
	)
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(req2)
