import requests
import hashlib


class CfToolsApi(object):
    def __init__(self, app_id, app_secret, game_identifier, ip, game_port, server_api_id, server_banlist_id):
        self.__application_id = app_id
        self.__application_secret = app_secret
        self.__api_cftools_server_id_hash = self.__create_server_id_hash(game_identifier, ip, game_port)
        self.__api_cftools_server_api_id = server_api_id
        # Links
        self.__api_cftools_public_api_url = 'https://data.cftools.cloud'

        self.__api_cftools_authentication_url = ''.join([self.__api_cftools_public_api_url, '/v1/auth/register'])

        self.__api_cftools_get_grants_url = ''.join([self.__api_cftools_public_api_url, '/v1/@app/grants'])

        self.__api_cftools_api_get_server_details_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/gameserver/{self.__api_cftools_server_id_hash}'])

        self.__api_cftools_get_server_info_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/info'])

        self.__api_cftools_get_server_statistics_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/statistics'])

        self.__api_cftools_get_server_player_list_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/GSM/list'])

        self.__api_cftools_post_server_kick_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/kick'])

        self.__api_cftools_post_server_private_message_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/message-private'])

        self.__api_cftools_post_server_public_message_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/message-server'])

        self.__api_cftools_post_server_row_rcon_command_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/raw'])

        self.__api_cftools_post_server_teleport_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v0/server/{self.__api_cftools_server_api_id}/gameLabs/teleport'])

        self.__api_cftools_post_server_spawn_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v0/server/{self.__api_cftools_server_api_id}/gameLabs/spawn'])

        self.__api_cftools_server_queue_priority_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/queuepriority'])

        self.__api_cftools_server_whitelist_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/whitelist'])

        self.__api_cftools_server_leaderboard_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/leaderboard'])

        self.__api_cftools_server_player_stats_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/server/{self.__api_cftools_server_api_id}/player'])

        self.__api_cftools_server_banlist_url = ''.join(
            [self.__api_cftools_public_api_url, f'/v1/banlist/{server_banlist_id}/bans'])

        self.__api_cftools_server_lookup_url = ''.join([self.__api_cftools_public_api_url, '/v1/users/lookup'])

        self.__api_cftools_session = requests.Session()
        self.__api_cftools_bearer_token = None
        self.__api_cftools_headers = {}

    def cftools_api_register(self):
        print('Cf tools auth...')
        payload = {
            'application_id': self.__application_id,
            'secret': self.__application_secret
        }
        reg_data = self.__api_cftools_session.post(self.__api_cftools_authentication_url, data=payload)
        if reg_data.status_code == 200:
            self.__api_cftools_bearer_token = reg_data.json()['token']
            self.__api_cftools_headers['Authorization'] = f'Bearer {self.__api_cftools_bearer_token}'
            print('Auth token received. ')
            return True
        else:
            print(f'Auth token not received. status {reg_data.status_code}')
            return False

    def cftools_api_get_grants(self):
        print('Getting grants...')
        grants = self.__api_cftools_session.get(self.__api_cftools_get_grants_url, headers=self.__api_cftools_headers)
        print(grants.text)

    def cftools_api_get_server_details(self):
        server_details = self.__api_cftools_session.get(self.__api_cftools_api_get_server_details_url,
                                                        headers=self.__api_cftools_headers)
        print(server_details.text)

    def cftools_api_get_server_info(self):
        server_info = self.__api_cftools_session.get(self.__api_cftools_get_server_info_url,
                                                     headers=self.__api_cftools_headers)
        print(server_info.text)

    def cftools_api_get_server_statistics(self):
        server_info = self.__api_cftools_session.get(self.__api_cftools_get_server_statistics_url,
                                                     headers=self.__api_cftools_headers)
        print(server_info.text)

    def cftools_api_get_server_list(self):
        server_player_list = self.__api_cftools_session.get(self.__api_cftools_get_server_player_list_url,
                                                            headers=self.__api_cftools_headers)
        print(server_player_list.text)

    def cftools_api_server_kick(self, gs_id, resaon):
        payload = {
            'gamesession_id': gs_id,
            'reason': resaon
        }
        server_player_kick = self.__api_cftools_session.post(self.__api_cftools_post_server_kick_url, data=payload,
                                                             headers=self.__api_cftools_headers)
        print(server_player_kick.status_code)

    def cftools_api_server_private_message(self, gs_id, content):
        payload = {
            'gamesession_id': gs_id,
            'content': content
        }
        server_private_message = self.__api_cftools_session.post(self.__api_cftools_post_server_private_message_url,
                                                                 data=payload, headers=self.__api_cftools_headers)
        print(server_private_message.status_code)

    def cftools_api_server_public_message(self, content):
        payload = {
            'content': content
        }
        server_public_message = self.__api_cftools_session.post(self.__api_cftools_post_server_public_message_url,
                                                                data=payload, headers=self.__api_cftools_headers)
        print(server_public_message.status_code)

    def cftools_api_server_row_rcon_command(self, command):
        payload = {
            'command': command
        }
        server_row_rcon_command = self.__api_cftools_session.post(self.__api_cftools_post_server_row_rcon_command_url,
                                                                  data=payload, headers=self.__api_cftools_headers)
        print(server_row_rcon_command.status_code)

    def cftools_api_server_teleport(self, gs_id, coords):
        payload = {
            'gamesession_id': gs_id,
            'coords': coords
        }
        server_teleport = self.__api_cftools_session.post(self.__api_cftools_post_server_teleport_url,
                                                          data=payload, headers=self.__api_cftools_headers)
        print(server_teleport.status_code)

    def cftools_api_server_spawn(self, gs_id, obj_name, quantity):
        payload = {
            'gamesession_id': gs_id,
            'object': obj_name,
            'quantity': quantity
        }
        server_spawn = self.__api_cftools_session.post(self.__api_cftools_post_server_spawn_url, data=payload,
                                                       headers=self.__api_cftools_headers)
        print(server_spawn.status_code)

    def cftools_api_server_queue_priority_list(self, cftools_id, comment):
        payload = {
            'cftools_id': cftools_id,
            'comment': comment
        }
        server_queue_priority_list = self.__api_cftools_session.get(self.__api_cftools_server_queue_priority_url,
                                                                    params=payload,
                                                                    headers=self.__api_cftools_headers)
        print(server_queue_priority_list.text)

    def cftools_api_server_queue_priority_entry(self, cftools_id, expires_at, comment):
        payload = {
            'cftools_id': cftools_id,
            'expires_at': expires_at,
            'comment': comment
        }
        server_queue_priority_entry = self.__api_cftools_session.post(self.__api_cftools_server_queue_priority_url,
                                                                      data=payload,
                                                                      headers=self.__api_cftools_headers)
        print(server_queue_priority_entry.status_code)

    def cftools_api_server_queue_priority_delete_entry(self, cftools_id):
        payload = {
            'cftools_id': cftools_id
        }
        server_queue_priority_delete = self.__api_cftools_session.delete(self.__api_cftools_server_queue_priority_url,
                                                                         data=payload,
                                                                         headers=self.__api_cftools_headers)
        print(server_queue_priority_delete.status_code)

    def cftools_api_server_whitelist(self, cftools_id, comment):
        payload = {
            'cftools_id': cftools_id,
            'comment': comment
        }
        server_whitelist = self.__api_cftools_session.get(self.__api_cftools_server_whitelist_url,
                                                          params=payload,
                                                          headers=self.__api_cftools_headers)
        print(server_whitelist.text)

    def cftools_api_server_whitelist_entry(self, cftools_id, expires_at, comment):
        payload = {
            'cftools_id': cftools_id,
            'expires_at': expires_at,
            'comment': comment
        }
        server_whitelist_entry = self.__api_cftools_session.post(self.__api_cftools_server_whitelist_url, data=payload,
                                                                 headers=self.__api_cftools_headers)
        print(server_whitelist_entry.status_code)

    def cftools_api_server_whitelist_delete_entry(self, cftools_id):
        payload = {
            'cftools_id': cftools_id
        }
        server_whitelist_delete_entry = self.__api_cftools_session.delete(self.__api_cftools_server_whitelist_url,
                                                                          data=payload,
                                                                          headers=self.__api_cftools_headers)
        print(server_whitelist_delete_entry.status_code)

    def cftools_api_server_leaderboard(self, stat, order, limit):
        # stat : one of [kills, deaths, suicides, playtime, longest_kill, longest_shot, kdratio]
        # order : 1 (Ascending) or -1 (Descending)
        # limit : An integer between 1 and 100; Defaults to 10
        # 7reqs/minute
        payload = {
            'stat': stat,
            'order': order,
            'limit': limit
        }
        server_leaderboard = self.__api_cftools_session.get(self.__api_cftools_server_leaderboard_url, params=payload,
                                                            headers=self.__api_cftools_headers)
        print(server_leaderboard.text)

    def cftools_api_server_player_stats(self, cftools_id):
        payload = {
            'cftools_id': cftools_id
        }
        server_player_stats = self.__api_cftools_session.get(self.__api_cftools_server_player_stats_url, params=payload,
                                                             headers=self.__api_cftools_headers)
        print(server_player_stats.text)

    # TODO Не понятно почему ничего не возвращает.
    def cftools_api_server_banlist(self):
        server_banlist = self.__api_cftools_session.get(self.__api_cftools_server_banlist_url,
                                                        headers=self.__api_cftools_headers)
        print(server_banlist.text)

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
        server_ban = self.__api_cftools_session.post(self.__api_cftools_server_banlist_url, data=payload,
                                                     headers=self.__api_cftools_headers)
        print(server_ban.status_code)

    def cftools_api_server_lookup(self, identifier):
        payload = {
            'identifier': identifier
        }
        server_lookup = self.__api_cftools_session.get(self.__api_cftools_server_lookup_url, params=payload,
                                                       headers=self.__api_cftools_headers)
        print(server_lookup.text)

    def cftools_api_server_unban(self, ban_id):
        payload = {
            'ban_id': ban_id
        }
        server_unban = self.__api_cftools_session.delete(self.__api_cftools_server_banlist_url, data=payload,
                                                         headers=self.__api_cftools_headers)
        print(server_unban.status_code)

    @staticmethod
    def __create_server_id_hash(game_identifier, ip, game_port):
        server_id_substring = ''.join([game_identifier, ip, game_port])
        return hashlib.sha1(str.encode(server_id_substring)).hexdigest()