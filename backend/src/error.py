'''
Error.py
By H09A-PADTHAI
Submitted 19 April 2020
'''
from werkzeug.exceptions import HTTPException

class AccessError(HTTPException):
    '''
    Define a class for AccessError
    '''
    code = 400
    message = 'No message specified'

class InputError(HTTPException):
    '''
    Define a class for InputError
    '''
    code = 400
    message = 'No message specified'
