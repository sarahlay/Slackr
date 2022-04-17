'''
User Functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
import os
import sys
import uuid
from urllib import request
from PIL import Image
from flask import Flask, url_for
from helper import validate_token, validate_user, validate_name_size, validate_handle_size, \
    validate_email_form, get_user, get_profile, is_used, check_valid_url, check_coords, \
    check_image_type, get_channel_members, get_channel_owners
from error import InputError

def user_profile(token, u_id):
    '''
    Returns the profile of a user, including their email, first name, last name,
    and handle.

    Parameters:
        token (str): user's authorisation key
        u_id (str): user ID of user whose profile is to be returned

    Returns:
        (dict of str: dict): dictionary of dictionary of user's profile
    '''
    # Convert inputs into appropriate type
    u_id = int(u_id)

    # Check for errors
    validate_token(token)
    validate_user(u_id)

    # Return user profile
    user = get_user('u_id', u_id)

    return {'user': get_profile(user)}

def user_profile_setname(token, name_first, name_last):
    '''
    Updates the authorised user's first and last name.

    Parameters:
        token (str): user's authorisation key
        name_first (str): new first name
        name_last (str): new last name

    Returns:
        (dict): empty dictionary
    '''
    # Check for errors
    u_id = validate_token(token)
    validate_name_size(name_first)
    validate_name_size(name_last)

    # Change user's name
    user = get_user('u_id', u_id)
    user['name_first'] = name_first
    user['name_last'] = name_last

    return {}

def user_profile_setemail(token, email):
    '''
    Update the authorised user's email address.

    Parameters:
        token (str): user's authorisation key
        email (str): new email

    Returns:
        (dict): empty dictionaryNone
    '''
    # Check for errors
    u_id = validate_token(token)
    validate_email_form(email)

    # InputError: email address is already being used by another user
    if is_used('email', email):
        raise InputError(description="Email is being used by another user")

    # Change user's email
    user = get_user('u_id', u_id)
    user['email'] = email

    return {}


def user_profile_sethandle(token, handle_str):
    '''
    Update the authorised user's handle.

    Parameters:
        token (str): user's authorisation key
        handle_str (str): new handle

    Returns:
        (dict): empty dictionary
    '''
    # Check for errors
    u_id = validate_token(token)
    validate_handle_size(handle_str)

    # InputError: handle is already used by another user
    if is_used('handle_str', handle_str):
        raise InputError(description="Handle is being used by another user")

    # Change user's handle
    user = get_user('u_id', u_id)
    user['handle_str'] = handle_str

    return {}

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Updates the authorised user's profile photo.

    Parameters:
        token (str): user's authorisation key
        img_url (str): URL of the image
        x_start (int): the starting x-coordinate to crop the photo
        y_start (int): the starting y-coordinate to crop the photo
        x_end (int): the ending x-coordinate to crop the photo
        y_end (int): the ending y-coordinate to crop the photo

    Returns:
        (dict): empty dictionary
    '''
    x_start, y_start, x_end, y_end = int(x_start), int(y_start), int(x_end), int(y_end)
    u_id = validate_token(token)
    user = get_user('u_id', u_id)

    check_valid_url(img_url)
    check_coords(x_start, y_start, x_end, y_end)
    check_image_type(img_url)

    random_url = uuid.uuid4()
    name = f"{random_url.hex}.jpg"

    app = Flask(__name__)
    port = ((sys.argv[1]) if len(sys.argv) == 2 else 8080)
    app.config['SERVER_NAME'] = port
    url = url_for('static', filename=name, _external=True)

   # Retrieve and crop image
    image_request = request.urlopen(img_url)
    profile_photo = Image.open(image_request)
    cropped_photo = profile_photo.crop((x_start, y_start, x_end, y_end))

    # Save image locally
    image_location_name = f"./static/{name}"
    cropped_photo.save(os.path.abspath(image_location_name))
    user['profile_img_url'] = url

    # Save image in channel
    for channel in user['channel_membership']:
        channel_id = channel['channel_id']
        channel_members = get_channel_members(channel_id)
        member = next(i for i in channel_members if i['u_id'] == u_id)
        member['profile_img_url'] = url


    for channel in user['channel_ownership']:
        channel_id = channel['channel_id']
        channel_owners = get_channel_owners(channel_id)
        owner = next(i for i in channel_owners if i['u_id'] == u_id)
        owner['profile_img_url'] = url

    return {}
