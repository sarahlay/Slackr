# Assumptions
###### By H09A-PADTHAI
###### Submitted 19 April 2020

These assumptions were written in conjunction with the task outline. Assumptions made for the exceptions that were stated in the task outline are not included. Only assumptions made for other exceptions that have been implemented are included in this file.

##	GENERAL ASSUMPTIONS

* A user must be logged in to use any function on Slackr, except for registration.
* Once created, channels cannot be changed between public or private access by any user.
* **A user must be at least a member of a channel to:
	* view, react, pin, edit or send a message
	* start a standup, check if a standup is active, or send standup messages
	* start a game of hangman and make guesses**


## AUTH FUNCTIONS

### auth_register
* The user is automatically logged in upon registration.
* New users must use an unregistered email.
* Users may have the same first and last name, and password.
 

## CHANNEL FUNCTIONS
### channel_invite
* A user that is invited to a channel immediately becomes a member of the channel.

### channel_join
* A user that joins a (public) channel becomes a member of that channel.

### channel_addowner
* A user must be a member of the channel to get promoted to owner.

### channel_removeowner
* Owners can demote themselves to member status.
* A channel can exist with no owners. (The last owner can demote themself.)


## CHANNELS FUNCTIONS

### channels_listall
* Users can view the details of all public channels and channels that they are a member/owner of.
* Owners of Slackr can view details of all channels.

### channels_create
* The user who creates a channel becomes an owner of that channel.


## HANGMAN FUNCTIONS

### hangman
* A game of hangman cannot be started in a channel if it has a currently active standup.

### guess
* A user cannot make a guess if the channel has a currently active standup.
* Users can only guess one letter at a time.

## MESSAGE FUNCTIONS

### message_remove
* When a message is removed, the message ID is deleted (i.e. becomes invalid for further use).

### message_edit
* When a message is edited, the message retains its original message ID.


## USER FUNCTIONS

### user_profile
* Any user can view another user's profile, unless the user has been removed.


## OTHER FUNCTIONS

### admin_userpermission_change
* A user cannot change their own permission.

### admin_user_remove
* When a user is removed, only their profile is removed.
* All existing messages sent and channels created by a removed user remain functional.
* Any reacts to other users' messages by the removed user will no longer appear.

### search
* Messages that have been removed cannot be searched.

### users_all
* Details of removed users do not appear in the list returned.