# pycftools

This library provides access to all cftools api methods. It is a kind of wrapper for all methods.

https://developer.cftools.cloud/documentation/data-api

For each library method. A verbose docstring has been written.

## Installation

```
pip install pycftools
```



## Basic usage:

```python
import pycftools

cfapi = pycftools.CfToolsApi(app_id='',
                             app_secret='', game_identifier='',
                             ip='', game_port='',
                             server_id='',
                             server_banlist_id='')
```

## Constructor arguments

```python
Class CfToolsApi used to access various cftools api methods.
The main use, getting access to api.
The ability to automate some processes, and getting access to the application from outside.

:param app_id: Application Id from https://developer.cftools.cloud/applications
:type app_id: str
:param app_secret: Application secret from https://developer.cftools.cloud/applications
:type app_secret: str
:param game_identifier: Game_identifier is needed to create server id.
:type game_identifier: str
:param ip: Ipv4 is needed to create server id.
:type ip: str
:param game_port: Game_port is needed to create server id.
:type game_port: str
:param server_api_id: Server_api_id this is the global server identifier and it can be found in the server API settings.
:type server_api_id: str
:param server_banlist_id: Server_banlist_id is global banlist identifier, it can be found in ban-manager https://app.cftools.cloud/ban-manager - see for Banlist ID.
:type server_banlist_id: str
:param auth_token_filename: Auth_token_filename this is the filename var for auth token file.
:type auth_token_filename: str
:param pycftools_debug: This is the variable for enabling debug outputs from the program.
:type pycftools_debug: bool
:param timestamp_delta: This is the time offset delta when the token in the file needs to be updated. By default, the value is set to half a day - 43200. UNIXTIMESTAMP
:type timestamp_delta: int
```


# Methods

The library provides all the methods from the cftools documentation. 
Request parameters are completely identical to those presented in the documentation.

#### All methods of the class return response objects, this is done for the convenience of further control.
#### You need to work with them as with ordinary responses to requests. json(), text, status_code, etc...
## If you don't know how to work with response objects. Read the documentation for the requests module.

## Authentication

```python
cfapi = pycftools.CfToolsApi(--->... < ---)
# Before working with methods, you need to get a token
# The library itself will add the token to the session headers
# All you need to do is create an instance of the class with all the parameters.
```

## Auth

### After version 0.2.7, you no longer need to call this method yourself. 

### The library will do everything by itself when you call the method you need.

```python
check_register()

This method is needed to check if we have an up-to-date authorization token.
It checks if there is a file with a token inside.
If such is found, it checks the relevance of the token and loads if everything is correct.

Note:
    Saving a token to a file is the simplest thing that came to my mind.
    Perhaps there is some kind of security threat from this.
    Write to issues on github to discuss :)

    Saving the token to a file makes it possible not to request a new token -
    every time after the object is re-created.
    Moreover, there is a delay of 2 requests per minute.

:return: return True if all auth moments is OK. else False.
:rtype: bool
```

## Grant process and access permissions

```python
[GET] grants() 

Get list of all grants and their respective id's.

Note:
    MAX REQUESTS: 1/MINUTE

:return: List of all grants and their respective id's.
:rtype: Response
```

## Game-Server

```python
# The library itself creates the serverID (sha1 -> hexdigest) from the game id, ipv4, gameport

[GET] server_details()

Get server details by Server Id. Server id server id is specified in the class constructor.

:return: Server details by Server Id.
:rtype: Response
```

## Server

```python
[GET] server_info()
Get general information about the registered server.
:return: Information about the registered server
:rtype: Response

[GET] server_statistics()
Get server statistics.

:return: Server statistics.
:rtype: Response

[GET] server_player_list()
Get full player list.

:return: Full player list.
:rtype: Response

[POST] server_kick(gs_id, reason) # gamesession_id, reason. -> str
Kick a player.

:param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
:type gs_id: str
:param resaon: Reason 1-128 len max.
:type resaon: str
:return: Returns 204 on success.
:rtype: Response

[POST] server_private_message(gs_id, content) # gamesession_id, content. -> str
Send a private message to a player.

:param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
:type gs_id: str
:param content: Message content length: 1-256.
:type content: str
:return: Returns 204 on success.
:rtype: Response

[POST] server_public_message(content) # content -> str
Send a public message to the server.

:param content: Message content length: 1-256.
:type content: str
:return: Returns 204 on success.
:rtype: Response

[POST] server_row_rcon_command(command) # command -> str
Send a raw RCon command to the server.

:param command: Command length: 1-256.
:type command: str
:return: Returns 204 on success.
:rtype: Response

[POST] server_teleport(gs_id, coords) # gamesession_id -> str, coords -> [X,Y] -> list
Teleport a player GameLabs required Not all games supported.

:param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
:type gs_id: str
:param coords: Coordinates list{2}: [X, Y]
:type coords: list
:return: Returns 204 on success.
:rtype: Response

[POST] server_spawn(gs_id, obj_name, quantity) # gamesession_id, obj_name -> str, quantity -> int
Spawn an object for player GameLabs required Not all games supported.

:param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
:type gs_id: str
:param obj_name: Object string.
:type obj_name: str
:param quantity: Quantity 1-9999 High quantities will lag a server.
:type quantity: int
:return: Returns 204 on success.
:rtype: Response

[GET] server_queue_priority_list(cftools_id, comment)
Get a list of all queue priority entries Streamed response.

:param cftools_id: CFTools ID
:type cftools_id: str
:param comment: Comment string.
:type comment: str
:return: List of all queue priority entries.
:rtype: Response

[POST] server_queue_priority_entry(cftools_id, expires_at, comment)
Create a new queue priority entry.

:param cftools_id: A CFTools account id.
:type cftools_id: str
:param expires_at: Expiration datetime object or null; Null is a permanent entry.
:type expires_at: str
:param comment: A note or comment.
:type comment: str
:return: Returns 204 on success.
:rtype: Response

[DELETE] queue_priority_delete_entry(cftools_id)
Delete an existing queue priority entry.

:param cftools_id: A CFTools account id.
:type cftools_id: str
:return: Returns 204 on success.
:rtype: Response

[GET] server_whitelist(cftools_id, comment)
Get a list of all whitelist entries Streamed response.

:param cftools_id: CFTools ID
:type cftools_id: str
:param comment: Comment string.
:type comment: str
:return: List of all whitelist entries.
:rtype: Response

[POST] server_whitelist_entry(cftools_id, expires_at, comment)
Create a new whitelist entry.

:param cftools_id: A CFTools account id.
:type cftools_id: str
:param expires_at: Expiration datetime object or null; Null is a permanent entry.
:type expires_at: str
:param comment: A note or comment.
:type comment: str
:return: Returns 204 on success.
:rtype: Response

[DELETE] server_whitelist_delete_entry(cftools_id)
Delete an existing whitelist entry.

:param cftools_id: A CFTools account id.
:type cftools_id: str
:return: Returns 204 on success.
:rtype: Response

[GET] server_leaderboard(stat, order, limit)
Request the generation of a leaderboard based on internally kept player stats.
This may fail if no stats are present.

Note:
    MAX REQUESTS: 7/MINUTE

:param stat: One of kills deaths suicides playtime longest_kill longest_shot kdratio
:type stat: str
:param order: 1 (Ascending) or -1 (Descending)
:type order: int
:param limit: An integer between 1 and 100; Defaults to 10
:type limit: int
:return: Leaderboard based on internally kept player stats.
:rtype: Response

[GET] server_player_stats(cftools_id)
Individual stats of a player for a server.

Note:
    MAX REQUESTS: 10/MINUTE

:param cftools_id: A CFTools account id.
:type cftools_id: str
:return: Individual stats of a player.
:rtype: Response

```

## Banlist

```python
[GET] server_banlist(flt) 
Get a list of all bans. Streamed response.

:param flt: Either an IPv4 or a CFTools account id
:type flt: str
:return: List of all bans.
:rtype: Response

[POST] server_ban(frmt, identifier, expires_at, reason)
Issue a new ban. Triggers an in-game kick.

:param frmt: cftools_id or ipv4.
:type frmt: str
:param identifier: A CFTools account id or an IPv4; IPv4 may contain wildcard substitutes in form of an asteriks.
:type identifier: str
:param expires_at: Expiration datetime object or null; Null is a permanent entry.
:type expires_at: str
:param reason: A ban reason,
:type reason: str
:return: Returns 204 on success.
:rtype: Response

[DELETE] server_unban(ban_id)
Revoke an existing ban.

:param ban_id: The ban id of an existing ban
:type ban_id: str
:return: Returns 204 on success.
:rtype: Response
```

## Users

```python
[GET] server_lookup_user(identifier)
Search CFTools Cloud database for a user.

:param identifier: Either a Steam64, BattlEye GUID or Bohemia Interactive UID
:type identifier: str
:return: Json response with information about user.
:rtype: Response
```

### If u needed to close session

```python
cfapi.close()
Method to close a session.
```


