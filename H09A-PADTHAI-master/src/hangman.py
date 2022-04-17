'''
Hangman functions
By H09A-PADTHAI
Submitted 19 April 2020
'''
import random
from helper import validate_token, validate_channel, validate_member, validate_guess, \
    hangman_send, reset_hangman, get_channel_hangman
from error import AccessError, InputError

def hangman(token, channel_id):
    '''
    Starts a new game of hangman in the specified channel.

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID

    Returns:
        {message_id} (dict of str: int): dictionary containing the message ID (int) of the message
            sent in the channel to show the game's progress
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)

    hangman_game = reset_hangman(channel_id)

    # Pick random word from library
    library = [line.strip() for line in open('/usr/share/dict/cracklib-small')][20:]
    hangman_game['word'] = random.choice(library).lower()

    # Ensure word is more than 5 characters
    while len(hangman_game['word']) <= 5:
        hangman_game['word'] = random.choice(library).lower()

    # Set hidden word
    for _ in range(len(hangman_game['word'])):
        hangman_game['display'].append('_')

    return hangman_send(token, channel_id)

def guess(token, channel_id, new_guess):
    '''
    Checks if the guessed letter is in the word and reveals the letter if it is, otherwise proceeds
    to "hang the man".

    Parameters:
        token (str): user's authorisation key
        channel_id (str): channel ID
        new_guess (str): the new guess

    Returns:
        {message_id} (dict of str: int): dictionary containing the message ID (int) of the message
            sent in the channel to show the game's progress
    '''
    # Convert inputs into appropriate type
    channel_id = int(channel_id)

    u_id = validate_token(token)
    validate_channel(channel_id)
    validate_member(u_id, channel_id)

    hangman_game = get_channel_hangman(channel_id)

    # Check hangman game is running
    if not hangman_game['word']:
        raise AccessError(description='Start hangman to play!')

    # Checking that hangman game isnt already won
    if hangman_game['message'] == 'YOU WON!' or hangman_game['message'] == 'GAME OVER!':
        raise InputError(description='Hangman game has finished, start a new game')

    # Changing hangman message
    hangman_game['message'] = 'Guess a letter!'

    # Check letter hasn't already been guessed
    new_guess = validate_guess(new_guess)
    if new_guess in hangman_game['guesses']:
        raise InputError(description='Letter has already been guessed')

    # Append new guess to guesses
    hangman_game['guesses'] += new_guess

    # Check letter is in word
    if new_guess not in hangman_game['word']:
        hangman_game['strikes'] += 1

    # Change display if in word
    else:
        for idx, letter in enumerate(hangman_game['word']):
            if new_guess == letter:
                hangman_game['display'][idx] = new_guess

    # Whole word is guessed
    if ''.join(hangman_game['display']) == hangman_game['word']:
        hangman_game['message'] = 'YOU WON!'

    # Show word if game is over
    if hangman_game['strikes'] == 9:
        hangman_game['display'] = hangman_game['word']
        hangman_game['message'] = 'GAME OVER!'

    return hangman_send(token, channel_id)
