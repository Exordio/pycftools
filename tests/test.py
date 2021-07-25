import unittest
import pickle
import re
from .pycftools import CfToolsApi


class FullModuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_cfapi = CfToolsApi(app_id='',
                                     app_secret='=', game_identifier='',
                                     ip='', game_port='',
                                     server_id='',
                                     server_banlist_id='')

    def test_cftools_server_id_hashing(self):
        self.assertTrue(re.match("\A(([0-9a-f]{40})|([0-9a-f]{6,8}))",
                                 self.test_cfapi._create_server_id_hash('1', '222.222.228.222', '2302')))

    def test_cftools_register_test(self):
        self.assertTrue(self.test_cfapi.cftools_api_check_register())

    def test_cftools_write_to_file_Test(self):
        with open('token.raw', 'rb') as test_file:
            dtest = pickle.load(test_file)
        self.assertIn('token', dtest)







