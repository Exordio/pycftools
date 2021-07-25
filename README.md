# pycftools

This library provides access to all cftools api methods. It is a kind of wrapper for all methods.

https://developer.cftools.cloud/documentation/data-api

## Installation

```
pip istall pycftools
```

## Dependencies


Basic usage:

```python
import pycftools

cfapi = pycftools.CfToolsApi(app_id='',
                             app_secret='=', game_identifier='',
                             ip='', game_port='',
                             server_id='',
                             server_banlist_id='')

# Before working with methods, you need to get a token
# The library itself will add the token to the session headers
# All you need to do is create an instance of the class with all the parameters.
# And run the registration method.
if cfapi.cftools_api_check_register():
    print('OK')
    cfapi.cftools_api_get_grants()
else:
    print('Something not OK')


```

## Constructor arguments

```

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
:param server_id: Server_api_id this is the global server identifier and it can be found in the server API settings.
:type server_id: str
:param server_banlist_id: Server_banlist_id is global banlist identifier, it can be found in ban-manager https://app.cftools.cloud/ban-manager - see for Banlist ID.
:type server_banlist_id: str
:param auth_token_filename: Auth_token_filename this is the filename var for auth token file.
:type auth_token_filename: str
:param pycftools_debug: This is the variable for enabling debug outputs from the program.
:type pycftools_debug: bool

```


# Methods

The library provides all the methods from the cftools documentation. 
Request parameters are completely identical to those presented in the documentation.

### All methods of the class return response objects, this is done for the convenience of further control.
### You need to work with them as with ordinary responses to requests. json(), text, status_code, etc...
## If you don't know how to work with response objects. Read the documentation for the requests module.

## Authentication

```python
cfapi = pycftools.CfToolsApi(--->...<---)
# Before working with methods, you need to get a token
# The library itself will add the token to the session headers
# All you need to do is create an instance of the class with all the parameters.
# And run the registration method.
cfapi.cftools_api_check_register()
# After receiving the token, you get access to all methods
```

## Grant process and access permissions

```python
[GET] cftools_api_get_grants() 
```

## Game-Server

```python
# The library itself creates the serverID (sha1 -> hexdigest) from the game id, ipv4, gameport

[GET] cftools_api_get_server_details() 
```

## Server

```python
[GET] cftools_api_get_server_info()
[GET] cftools_api_get_server_statistics()
[GET] cftools_api_get_server_list()
[POST] cftools_api_server_kick(gs_id, reason) # gamesession_id, reason. -> str
[POST] cftools_api_server_private_message(gs_id, content) # gamesession_id, content. -> str
[POST] cftools_api_server_public_message(content) # content -> str
[POST] cftools_api_server_row_rcon_command(command) # command -> str
[POST] cftools_api_server_teleport(gs_id, coords) # gamesession_id -> str, coords -> [X,Y] -> list
[POST] cftools_api_server_spawn(gs_id, obj_name, quantity) # gamesession_id, obj_name -> str, quantity -> int

# SEE CFTOOLS DOCS TO MORE INFORMATION ABOUT PARAMS
[GET] cftools_api_server_queue_priority_list(cftools_id, comment)
[POST] cftools_api_server_queue_priority_entry(cftools_id, expires_at, comment)
[DELETE] cftools_api_server_queue_priority_delete_entry(cftools_id)

[GET] cftools_api_server_whitelist(cftools_id, comment)
[POST] cftools_api_server_whitelist_entry(cftools_id, expires_at, comment)
[DELETE] cftools_api_server_whitelist_delete_entry(cftools_id)

[GET] cftools_api_server_leaderboard(stat, order, limit)
[GET] cftools_api_server_player_stats(cftools_id)
```

## Banlist

```python
[GET] cftools_api_server_banlist() 
[POST] cftools_api_server_ban(frmt, identifier, expires_at, reason)
[DELETE] cftools_api_server_unban(ban_id)
```

## Users

```python
[GET] cftools_api_server_lookup(identifier)
```

### If u needed to close session

```python
cfapi.close()
```


