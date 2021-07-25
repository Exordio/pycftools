import datetime
import requests
import hashlib
import pickle
import os


class CfToolsApi(object):
    def __init__(self, app_id, app_secret, game_identifier, ip, game_port, server_id, server_banlist_id,
                 auth_token_filename='token.raw', pycftools_debug=False):
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
        :param server_id: Server_api_id this is the global server identifier and it can be found in the server API settings.
        :type server_id: str
        :param server_banlist_id: Server_banlist_id is global banlist identifier, it can be found in ban-manager https://app.cftools.cloud/ban-manager - see for Banlist ID.
        :type server_banlist_id: str
        :param auth_token_filename: Auth_token_filename this is the filename var for auth token file.
        :type auth_token_filename: str
        :param pycftools_debug: This is the variable for enabling debug outputs from the program.
        :type pycftools_debug: bool
        """

        self.__pycftools_debug = pycftools_debug
        self.__application_id = app_id
        self.__application_secret = app_secret
        self.__api_cftools_server_id_hash = self.__create_server_id_hash(game_identifier, ip, game_port)
        self.__api_cftools_server_id = server_id
        # General public api url
        self.__api_cftools_public_api_url = 'https://data.cftools.cloud'

        self.__api_cftools_authentication_url = ''.join([self.__api_cftools_public_api_url, '/v1/auth/register'])

        self.__api_cftools_get_grants_url = ''.join([self.__api_cftools_public_api_url, '/v1/@app/grants'])

        self.__api_cftools_api_get_server_details_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/gameserver/{self.__api_cftools_server_id_hash}'])

        self.__api_cftools_get_server_info_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/info'])

        self.__api_cftools_get_server_statistics_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/statistics'])

        self.__api_cftools_get_server_player_list_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/GSM/list'])

        self.__api_cftools_post_server_kick_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/kick'])

        self.__api_cftools_post_server_private_message_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/message-private'])

        self.__api_cftools_post_server_public_message_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/message-server'])

        self.__api_cftools_post_server_row_rcon_command_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/raw'])

        self.__api_cftools_post_server_teleport_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v0/server/{self.__api_cftools_server_id}/gameLabs/teleport'])

        self.__api_cftools_post_server_spawn_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v0/server/{self.__api_cftools_server_id}/gameLabs/spawn'])

        self.__api_cftools_server_queue_priority_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/queuepriority'])

        self.__api_cftools_server_whitelist_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/whitelist'])

        self.__api_cftools_server_leaderboard_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/leaderboard'])

        self.__api_cftools_server_player_stats_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_id}/player'])

        self.__api_cftools_server_banlist_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/banlist/{server_banlist_id}/bans'])

        self.__api_cftools_server_lookup_url = ''.join([self.__api_cftools_public_api_url, '/v1/users/lookup'])

        self.__api_cftools_session = requests.Session()
        self.__api_cftools_bearer_token = None
        self.__api_cftools_headers = {}

        self.__cftools_token_file = auth_token_filename

    # ---------------- Save/load tokens part ----------------
    def cftools_api_check_register(self):
        print('Cf tools auth...')
        if os.path.exists(self.__cftools_token_file):
            print('Token file found') if self.__pycftools_debug else None
            self.cftools_load_auth_bearer_token()
        else:
            print('File with token not finded, creating new.') if self.__pycftools_debug else None
            self.cftools_save_auth_bearer_token(self.cftools_api_get_auth_bearer_token())
            self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'

        print('Token loaded')
        return True

    def cftools_save_auth_bearer_token(self, token):
        with open(self.__cftools_token_file, 'wb') as conf_file:
            to_save_data = {
                'token': token,
                'timestamp': datetime.datetime.now().timestamp()
            }
            pickle.dump(to_save_data, conf_file)

    def cftools_check_token_timestamp(self, timestamp):
        if (timestamp + 43200) <= datetime.datetime.now().timestamp():
            print('Auth token is outdated, need to get a new one') if self.__pycftools_debug else None
            return True
        else:
            print('Auth token is not outdated') if self.__pycftools_debug else None
            return False

    def cftools_load_auth_bearer_token(self):
        with open(self.__cftools_token_file, 'rb') as conf_file:
            try:
                to_load_data = pickle.load(conf_file)
                if self.cftools_check_token_timestamp(to_load_data['timestamp']):
                    self.cftools_save_auth_bearer_token(self.cftools_api_get_auth_bearer_token())
                    self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'
                else:
                    self.__api_cftools_headers['Authorization'] = f'''Bearer {to_load_data['token']}'''
            except EOFError:
                self.cftools_save_auth_bearer_token(self.cftools_api_get_auth_bearer_token())
                self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'

    def cftools_api_get_auth_bearer_token(self):
        payload = {
            'application_id': self.__application_id,
            'secret': self.__application_secret
        }
        reg_data = self.__api_cftools_session.post(self.__api_cftools_authentication_url, data=payload)
        if reg_data.status_code == 200:
            self.__api_cftools_bearer_token = reg_data.json()['token']
            print('Auth token received.') if self.__pycftools_debug else None
            return self.__api_cftools_bearer_token
        else:
            print(f'Auth error reg_data status code : {reg_data.status_code}')
            assert False

    # ---------------- Save/load tokens part END ----------------

    def cftools_api_get_grants(self):
        print('Getting grants...') if self.__pycftools_debug else None
        grants = self.__api_cftools_session.get(self.__api_cftools_get_grants_url, headers=self.__api_cftools_headers)
        return grants

    def cftools_api_get_server_details(self):
        return self.__api_cftools_session.get(self.__api_cftools_api_get_server_details_url,
                                              headers=self.__api_cftools_headers)

    def cftools_api_get_server_info(self):
        return self.__api_cftools_session.get(self.__api_cftools_get_server_info_url,
                                              headers=self.__api_cftools_headers)

    def cftools_api_get_server_statistics(self):
        return self.__api_cftools_session.get(self.__api_cftools_get_server_statistics_url,
                                              headers=self.__api_cftools_headers)

    def cftools_api_get_server_list(self):
        return self.__api_cftools_session.get(self.__api_cftools_get_server_player_list_url,
                                              headers=self.__api_cftools_headers)

    def cftools_api_server_kick(self, gs_id, resaon):
        payload = {
            'gamesession_id': gs_id,
            'reason': resaon
        }
        return self.__api_cftools_session.post(self.__api_cftools_post_server_kick_url, data=payload,
                                               headers=self.__api_cftools_headers)

    def cftools_api_server_private_message(self, gs_id, content):
        payload = {
            'gamesession_id': gs_id,
            'content': content
        }
        return self.__api_cftools_session.post(self.__api_cftools_post_server_private_message_url,
                                               data=payload, headers=self.__api_cftools_headers)

    def cftools_api_server_public_message(self, content):
        payload = {'content': content}
        return self.__api_cftools_session.post(self.__api_cftools_post_server_public_message_url,
                                               data=payload, headers=self.__api_cftools_headers)

    def cftools_api_server_row_rcon_command(self, command):
        payload = {'command': command}
        return self.__api_cftools_session.post(self.__api_cftools_post_server_row_rcon_command_url,
                                               data=payload, headers=self.__api_cftools_headers)

    def cftools_api_server_teleport(self, gs_id, coords):
        payload = {
            'gamesession_id': gs_id,
            'coords': coords
        }
        return self.__api_cftools_session.post(self.__api_cftools_post_server_teleport_url,
                                               data=payload, headers=self.__api_cftools_headers)

    def cftools_api_server_spawn(self, gs_id, obj_name, quantity):
        payload = {
            'gamesession_id': gs_id,
            'object': obj_name,
            'quantity': quantity
        }
        return self.__api_cftools_session.post(self.__api_cftools_post_server_spawn_url, data=payload,
                                               headers=self.__api_cftools_headers)

    def cftools_api_server_queue_priority_list(self, cftools_id, comment):
        payload = {
            'cftools_id': cftools_id,
            'comment': comment
        }
        return self.__api_cftools_session.get(self.__api_cftools_server_queue_priority_url,
                                              params=payload,
                                              headers=self.__api_cftools_headers)

    def cftools_api_server_queue_priority_entry(self, cftools_id, expires_at, comment):
        payload = {
            'cftools_id': cftools_id,
            'expires_at': expires_at,
            'comment': comment
        }
        return self.__api_cftools_session.post(self.__api_cftools_server_queue_priority_url,
                                               data=payload,
                                               headers=self.__api_cftools_headers)

    def cftools_api_server_queue_priority_delete_entry(self, cftools_id):
        payload = {'cftools_id': cftools_id}
        return self.__api_cftools_session.delete(self.__api_cftools_server_queue_priority_url,
                                                 data=payload,
                                                 headers=self.__api_cftools_headers)

    def cftools_api_server_whitelist(self, cftools_id, comment):
        payload = {
            'cftools_id': cftools_id,
            'comment': comment
        }
        return self.__api_cftools_session.get(self.__api_cftools_server_whitelist_url,
                                              params=payload,
                                              headers=self.__api_cftools_headers)

    def cftools_api_server_whitelist_entry(self, cftools_id, expires_at, comment):
        payload = {
            'cftools_id': cftools_id,
            'expires_at': expires_at,
            'comment': comment
        }
        return self.__api_cftools_session.post(self.__api_cftools_server_whitelist_url, data=payload,
                                               headers=self.__api_cftools_headers)

    def cftools_api_server_whitelist_delete_entry(self, cftools_id):
        payload = {'cftools_id': cftools_id}
        return self.__api_cftools_session.delete(self.__api_cftools_server_whitelist_url,
                                                 data=payload,
                                                 headers=self.__api_cftools_headers)

    def cftools_api_server_leaderboard(self, stat, order, limit):
        payload = {
            'stat': stat,
            'order': order,
            'limit': limit
        }
        return self.__api_cftools_session.get(self.__api_cftools_server_leaderboard_url, params=payload,
                                              headers=self.__api_cftools_headers)

    def cftools_api_server_player_stats(self, cftools_id):
        payload = {'cftools_id': cftools_id}
        return self.__api_cftools_session.get(self.__api_cftools_server_player_stats_url, params=payload,
                                              headers=self.__api_cftools_headers)

    def cftools_api_server_banlist(self):
        return self.__api_cftools_session.get(self.__api_cftools_server_banlist_url,
                                              headers=self.__api_cftools_headers)

    def cftools_api_server_ban(self, frmt, identifier, expires_at, reason):
        # format : cftools_id or ipv4
        # identifier : A CFTools account id or an IPv4; IPv4 may contain wildcard substitutes in form of an asteriks
        # expires_at : Expiration datetime object or null; Null is a permanent entry
        # reason : A ban reason
        payload = {
            'format': frmt,
            'identifier': identifier,
            'expires_at': expires_at,
            'reason': reason
        }
        return self.__api_cftools_session.post(self.__api_cftools_server_banlist_url, data=payload,
                                               headers=self.__api_cftools_headers)

    def cftools_api_server_unban(self, ban_id):
        payload = {'ban_id': ban_id}
        return self.__api_cftools_session.delete(self.__api_cftools_server_banlist_url, data=payload,
                                                 headers=self.__api_cftools_headers)

    def cftools_api_server_lookup(self, identifier):
        payload = {'identifier': identifier}
        return self.__api_cftools_session.get(self.__api_cftools_server_lookup_url, params=payload,
                                              headers=self.__api_cftools_headers)

    @staticmethod
    def __create_server_id_hash(game_identifier, ip, game_port):
        server_id_substring = ''.join([game_identifier, ip, game_port])
        return hashlib.sha1(str.encode(server_id_substring)).hexdigest()
