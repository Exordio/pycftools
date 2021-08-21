from functools import wraps

import datetime
import requests
import hashlib
import pickle
import os


class CfToolsApi(object):
    def __init__(self, app_id, app_secret, game_identifier, ip, game_port, server_api_id, server_banlist_id,
                 auth_token_filename='token.raw', pycftools_debug=False, timestamp_delta=43200):
        """
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
        """

        self.__pycftools_debug = pycftools_debug
        self.__application_id = app_id
        self.__application_secret = app_secret
        self.__server_id_hash = self._create_server_id_hash(game_identifier, ip, game_port)
        self.__server_api_id = server_api_id

        # General public api url
        self.__public_api_url = 'https://data.cftools.cloud'

        # ---------------- Api urls ----------------

        self.__authentication_url = ''.join([self.__public_api_url, '/v1/auth/register'])
        self.__grants_url = ''.join([self.__public_api_url, '/v1/@app/grants'])
        self.__server_details_url = ''.join(
            [self.__public_api_url, f'/v1/gameserver/{self.__server_id_hash}'])
        self.__server_info_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/info'])
        self.__server_statistics_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/statistics'])
        self.__server_player_list_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/GSM/list'])
        self.__server_kick_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/kick'])
        self.__server_private_message_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/message-private'])
        self.__server_public_message_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/message-server'])
        self.__server_row_rcon_command_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/raw'])
        self.__server_teleport_url = ''.join(
            [self.__public_api_url, f'/v0/server/{self.__server_api_id}/gameLabs/teleport'])
        self.__server_spawn_url = ''.join(
            [self.__public_api_url, f'/v0/server/{self.__server_api_id}/gameLabs/spawn'])
        self.__server_queue_priority_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/queuepriority'])
        self.__server_whitelist_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/whitelist'])
        self.__server_leaderboard_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/leaderboard'])
        self.__server_player_stats_url = ''.join(
            [self.__public_api_url, f'/v1/server/{self.__server_api_id}/player'])
        self.__server_banlist_url = ''.join(
            [self.__public_api_url, f'/v1/banlist/{server_banlist_id}/bans'])
        self.__server_lookup_url = ''.join([self.__public_api_url, '/v1/users/lookup'])

        # ---------------- Api urls End ----------------

        self.__api_cftools_session = requests.Session()
        self.__api_cftools_bearer_token = None

        self.__api_cftools_headers = {}
        self.__cftools_token_file = auth_token_filename
        self.__timestamp_delta = timestamp_delta

        self.__token_timestamp = None
        self.__first_load = True

    # ---------------- Save/load tokens ----------------

    def check_register(wmethod):
        """
        This method is needed to check if we have an up-to-date authorization token.
        It checks if there is a file with a token inside.
        If such is found, it checks the relevance of the token and loads if everything is correct.
        Else asks for a new one, and automatically sets / saves.

        Note:
            Saving a token to a file is the simplest thing that came to my mind.
            Perhaps there is some kind of security threat from this.
            Write to issues on github to discuss :)

            Saving the token to a file makes it possible not to request a new token -
            every time after the object is re-created.
            Moreover, there is a delay of 2 requests per minute.

            this. - in this context is self.
            I use this method as a wrapper for other methods where the authorization token must be up to date.


        :return: return True if all auth moments is OK. else False.
        :rtype: bool
        """

        @wraps(wmethod)
        def wrapper(*args, **kwargs):
            self = args[0]
            print(f'|| {datetime.datetime.now()} || Cf tools auth...') if self.__pycftools_debug else None
            try:
                if self.__first_load:
                    if os.path.exists(self.__cftools_token_file):
                        print(f'|| {datetime.datetime.now()} || Token file found') if self.__pycftools_debug else None
                        self.__load_auth_bearer_token()
                    else:
                        print(
                            f'|| {datetime.datetime.now()} || File with token not finded, creating new.') if self.__pycftools_debug else None
                        self.__save_auth_bearer_token(self.__get_auth_bearer_token())
                        self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'
                        self.__token_timestamp = datetime.datetime.now().timestamp()
                    self.__first_load = False
                else:
                    print(f'|| {datetime.datetime.now()} || Load token from mem') if self.__pycftools_debug else None
                    if self.__check_token_timestamp(self.__token_timestamp):
                        self.__save_auth_bearer_token(self.__get_auth_bearer_token())
                        self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'
                        self.__token_timestamp = datetime.datetime.now().timestamp()

                print(f'|| {datetime.datetime.now()} || Token loaded') if self.__pycftools_debug else None
                return wmethod(*args, **kwargs)
            except Exception as err:
                print(err)

        return wrapper

    def __save_auth_bearer_token(self, token):
        """
        Method to save token to file.

        :param token: Auth bearer token.
        :type token: str
        """
        with open(self.__cftools_token_file, 'wb') as conf_file:
            to_save_data = {
                'token': token,
                'timestamp': datetime.datetime.now().timestamp()
            }
            pickle.dump(to_save_data, conf_file)

    def __check_token_timestamp(self, timestamp):
        """
        :param timestamp: Unix timestamp from file. It shows the creation date of the token.
        :type timestamp: float
        :return: return True if token is outdated, else if token is not outdated - return False
        :rtype: bool
        """
        if (timestamp + self.__timestamp_delta) <= datetime.datetime.now().timestamp():
            print(f'|| {datetime.datetime.now()} || Auth token is outdated') if self.__pycftools_debug else None
            return True
        else:
            print(f'|| {datetime.datetime.now()} || Auth token is not outdated') if self.__pycftools_debug else None
            return False

    def __load_auth_bearer_token(self):
        """
        Method to load dict with token from file.
        """
        with open(self.__cftools_token_file, 'rb') as conf_file:
            try:
                to_load_data = pickle.load(conf_file)
                if self.__check_token_timestamp(to_load_data['timestamp']):
                    self.__save_auth_bearer_token(self.__get_auth_bearer_token())
                    self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'
                    self.__token_timestamp = datetime.datetime.now().timestamp()
                else:
                    self.__api_cftools_headers['Authorization'] = f'''Bearer {to_load_data['token']}'''
                    self.__token_timestamp = to_load_data['timestamp']

                print(
                    f'|| {datetime.datetime.now()} || Setting api headers {self.__api_cftools_headers}') if self.__pycftools_debug else None
            except EOFError:
                self.__save_auth_bearer_token(self.__get_auth_bearer_token())
                self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'
                self.__token_timestamp = datetime.datetime.now().timestamp()

    def __get_auth_bearer_token(self):
        """
        Some routes require authentication in the form of Bearer tokens in the request headers.

        Note:
            MAX REQUESTS: 2/MINUTE

        :return: Bearer token.
        :rtype: str
        """
        payload = {
            # Your application id.
            'application_id': self.__application_id,
            # Your application secret.
            'secret': self.__application_secret
        }
        reg_data = self.__api_cftools_session.post(self.__authentication_url, data=payload)
        if reg_data.status_code == 200:
            self.__api_cftools_bearer_token = reg_data.json()['token']
            print(f'|| {datetime.datetime.now()} || Auth token received. - ~ {self.__api_cftools_bearer_token}') if self.__pycftools_debug else None
            return self.__api_cftools_bearer_token
        else:
            print(f'|| {datetime.datetime.now()} || Auth error reg_data status code : {reg_data.status_code}')
            assert False

    # ---------------- Save/load tokens End ----------------

    # ---------------- Grant process and access permissions ----------------

    # When trying to access restricted routes or data, an API application must be granted access by the resource owner.
    # This permission can be granted by sending the resource owner the "Grant URL"
    # You can find on your application dashboard.

    @check_register
    def grants(self):
        """
        Get list of all grants and their respective id's.

        Note:
            MAX REQUESTS: 1/MINUTE

        :return: List of all grants and their respective id's.
        :rtype: Response
        """
        return self.__api_cftools_session.get(self.__grants_url, headers=self.__api_cftools_headers)

    @check_register
    def server_details(self):
        """
        Get server details by Server Id. Server id server id is specified in the class constructor.

        :return: Server details by Server Id.
        :rtype: Response
        """
        return self.__api_cftools_session.get(self.__server_details_url,
                                              headers=self.__api_cftools_headers)

    # ---------------- Server ----------------

    # All subsequent routes require a Server API Id and an active application grant.

    @check_register
    def server_info(self):
        """
        Get general information about the registered server.

        :return: Information about the registered server
        :rtype: Response
        """
        return self.__api_cftools_session.get(self.__server_info_url,
                                              headers=self.__api_cftools_headers)

    @check_register
    def server_statistics(self):
        """
        Get server statistics.

        :return: Server statistics.
        :rtype: Response
        """
        return self.__api_cftools_session.get(self.__server_statistics_url,
                                              headers=self.__api_cftools_headers)

    @check_register
    def server_player_list(self):
        """
        Get full player list.

        :return: Full player list.
        :rtype: Response
        """
        return self.__api_cftools_session.get(self.__server_player_list_url,
                                              headers=self.__api_cftools_headers)

    @check_register
    def server_kick(self, gs_id, reason):
        """
        Kick a player.

        :param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
        :type gs_id: str
        :param reason: Reason 1-128 len max.
        :type reason: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {
            'gamesession_id': gs_id,
            'reason': reason
        }
        return self.__api_cftools_session.post(self.__server_kick_url, data=payload,
                                               headers=self.__api_cftools_headers)

    @check_register
    def server_private_message(self, gs_id, content):
        """
        Send a private message to a player.

        :param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
        :type gs_id: str
        :param content: Message content length: 1-256.
        :type content: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {
            'gamesession_id': gs_id,
            'content': content
        }
        return self.__api_cftools_session.post(self.__server_private_message_url,
                                               data=payload, headers=self.__api_cftools_headers)

    @check_register
    def server_public_message(self, content):
        """
        Send a public message to the server.

        :param content: Message content length: 1-256.
        :type content: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {'content': content}
        return self.__api_cftools_session.post(self.__server_public_message_url,
                                               data=payload, headers=self.__api_cftools_headers)

    @check_register
    def server_row_rcon_command(self, command):
        """
        Send a raw RCon command to the server.

        :param command: Command length: 1-256.
        :type command: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {'command': command}
        return self.__api_cftools_session.post(self.__server_row_rcon_command_url,
                                               data=payload, headers=self.__api_cftools_headers)

    @check_register
    def server_teleport(self, gs_id, coords):
        """
        Teleport a player GameLabs required Not all games supported.

        :param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
        :type gs_id: str
        :param coords: Coordinates list{2}: [X, Y]
        :type coords: list
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {
            'gamesession_id': gs_id,
            'coords': coords
        }
        return self.__api_cftools_session.post(self.__server_teleport_url,
                                               data=payload, headers=self.__api_cftools_headers)

    @check_register
    def server_spawn(self, gs_id, obj_name, quantity):
        """
        Spawn an object for player GameLabs required Not all games supported.

        :param gs_id: An active gamesession_id (See cftools_api_get_server_list() for details)
        :type gs_id: str
        :param obj_name: Object string.
        :type obj_name: str
        :param quantity: Quantity 1-9999 High quantities will lag a server.
        :type quantity: int
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {
            'gamesession_id': gs_id,
            'object': obj_name,
            'quantity': quantity
        }
        return self.__api_cftools_session.post(self.__server_spawn_url, data=payload,
                                               headers=self.__api_cftools_headers)

    @check_register
    def server_queue_priority_list(self, cftools_id, comment):
        """
        Get a list of all queue priority entries Streamed response.

        :param cftools_id: CFTools ID
        :type cftools_id: str
        :param comment: Comment string.
        :type comment: str
        :return: List of all queue priority entries.
        :rtype: Response
        """
        payload = {
            'cftools_id': cftools_id,
            'comment': comment
        }
        return self.__api_cftools_session.get(self.__server_queue_priority_url,
                                              params=payload,
                                              headers=self.__api_cftools_headers)

    @check_register
    def server_queue_priority_entry(self, cftools_id, expires_at, comment):
        """
        Create a new queue priority entry.

        :param cftools_id: A CFTools account id.
        :type cftools_id: str
        :param expires_at: Expiration datetime object or null; Null is a permanent entry.
        :type expires_at: str
        :param comment: A note or comment.
        :type comment: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {
            'cftools_id': cftools_id,
            'expires_at': expires_at,
            'comment': comment
        }
        return self.__api_cftools_session.post(self.__server_queue_priority_url,
                                               data=payload,
                                               headers=self.__api_cftools_headers)

    @check_register
    def queue_priority_delete_entry(self, cftools_id):
        """
        Delete an existing queue priority entry.

        :param cftools_id: A CFTools account id.
        :type cftools_id: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {'cftools_id': cftools_id}
        return self.__api_cftools_session.delete(self.__server_queue_priority_url,
                                                 data=payload,
                                                 headers=self.__api_cftools_headers)

    @check_register
    def server_whitelist(self, cftools_id, comment):
        """
        Get a list of all whitelist entries Streamed response.

        :param cftools_id: CFTools ID
        :type cftools_id: str
        :param comment: Comment string.
        :type comment: str
        :return: List of all whitelist entries.
        :rtype: Response
        """
        payload = {
            'cftools_id': cftools_id,
            'comment': comment
        }
        return self.__api_cftools_session.get(self.__server_whitelist_url,
                                              params=payload,
                                              headers=self.__api_cftools_headers)

    @check_register
    def server_whitelist_entry(self, cftools_id, expires_at, comment):
        """
        Create a new whitelist entry.

        :param cftools_id: A CFTools account id.
        :type cftools_id: str
        :param expires_at: Expiration datetime object or null; Null is a permanent entry.
        :type expires_at: str
        :param comment: A note or comment.
        :type comment: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {
            'cftools_id': cftools_id,
            'expires_at': expires_at,
            'comment': comment
        }
        return self.__api_cftools_session.post(self.__server_whitelist_url, data=payload,
                                               headers=self.__api_cftools_headers)

    @check_register
    def server_whitelist_delete_entry(self, cftools_id):
        """
        Delete an existing whitelist entry.

        :param cftools_id: A CFTools account id.
        :type cftools_id: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {'cftools_id': cftools_id}
        return self.__api_cftools_session.delete(self.__server_whitelist_url,
                                                 data=payload,
                                                 headers=self.__api_cftools_headers)

    @check_register
    def server_leaderboard(self, stat, order, limit):
        """
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
        """
        payload = {
            'stat': stat,
            'order': order,
            'limit': limit
        }
        return self.__api_cftools_session.get(self.__server_leaderboard_url, params=payload,
                                              headers=self.__api_cftools_headers)

    @check_register
    def server_player_stats(self, cftools_id):
        """
        Individual stats of a player for a server.

        Note:
            MAX REQUESTS: 10/MINUTE

        :param cftools_id: A CFTools account id.
        :type cftools_id: str
        :return: Individual stats of a player.
        :rtype: Response
        """
        payload = {'cftools_id': cftools_id}
        return self.__api_cftools_session.get(self.__server_player_stats_url, params=payload,
                                              headers=self.__api_cftools_headers)

    # ---------------- Banlist ----------------

    # All subsequent routes require a Banlist Id and an active application grant.

    @check_register
    def server_banlist(self, flt):
        """
        Get a list of all bans. Streamed response.

        :param flt: Either an IPv4 or a CFTools account id
        :type flt: str
        :return: List of all bans.
        :rtype: Response
        """
        payload = {'filter': flt}
        return self.__api_cftools_session.get(self.__server_banlist_url, params=payload,
                                              headers=self.__api_cftools_headers)

    @check_register
    def server_ban(self, frmt, identifier, expires_at, reason):
        """
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
        """
        payload = {
            'format': frmt,
            'identifier': identifier,
            'expires_at': expires_at,
            'reason': reason
        }
        return self.__api_cftools_session.post(self.__server_banlist_url, data=payload,
                                               headers=self.__api_cftools_headers)

    @check_register
    def server_unban(self, ban_id):
        """
        Revoke an existing ban.

        :param ban_id: The ban id of an existing ban
        :type ban_id: str
        :return: Returns 204 on success.
        :rtype: Response
        """
        payload = {'ban_id': ban_id}
        return self.__api_cftools_session.delete(self.__server_banlist_url, data=payload,
                                                 headers=self.__api_cftools_headers)

    # ---------------- Users ----------------

    @check_register
    def server_lookup_user(self, identifier):
        """
        Search CFTools Cloud database for a user.

        :param identifier: Either a Steam64, BattlEye GUID or Bohemia Interactive UID
        :type identifier: str
        :return: Json response with information about user.
        :rtype: Response
        """
        payload = {'identifier': identifier}
        return self.__api_cftools_session.get(self.__server_lookup_url, params=payload,
                                              headers=self.__api_cftools_headers)

    # ---------------- Server id ----------------

    @staticmethod
    def _create_server_id_hash(game_identifier, ip, game_port):
        """
        CFTools Cloud's Steamrelay service automatically queries all game servers for specific games
        in a 30 to 60 second interval. To retrieve information about game servers you need to generate
        a Data API specific server resource id, referenced to as server_id in the following.

        The server_id generates from following datasets:
        1. IPv4 of the game server
        2. Gameport of the game server
        3. Game identifier

        For Dayz identifier is 1.

        Once you have gathered this information, build a string with these parameters in the following order:
        {game_identifier}{ipv4}{game_port}
        Do not use any spacers or other additional symbols.

        After you have this string use a sha1 hashing function on it.
        The digest in hexademical form can then be used as server_id.

        :param game_identifier: is a game id in cftools cloud.
        :type game_identifier: str
        :param ip: ipv4 address of server.
        :type ip: str
        :param game_port: server port.
        :type game_port: str
        :return: sha1 hash string.
        :rtype: str
        """
        server_id_substring = ''.join([game_identifier, ip, game_port])
        return hashlib.sha1(str.encode(server_id_substring)).hexdigest()

    def close(self):
        """
        Method to close a session.
        """
        self.__api_cftools_session.close()
