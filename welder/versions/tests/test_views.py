from pygit2 import Repository, GIT_FILEMODE_BLOB, GIT_FILEMODE_TREE, Signature, IndexEntry
from django.test.utils import override_settings
from welder.versions.porcelain import generate_directory
from django.conf import settings
from django.test import TestCase
from django.test import Client
from functools import wraps
from time import time
import logging
import shutil
import base64
import json
import time
import os
import os

cwd = os.getcwd()
logger = logging.getLogger(__name__)
logging.disable(logging.CRITICAL)
settings.DEBUG = True


class VersionsViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.app = 'testing'
        cls.username = 'wevolver'
        cls.user = 'wevolver'

    @classmethod
    def tearDownClass(cls):
        path = generate_directory('wevolver')
        path = os.path.join(settings.REPO_DIRECTORY, path, cls.app)
        if os.path.exists(path):
            shutil.rmtree(path)

    def setUp(self):
        response = self.client.post('/{}/{}/create'.format(self.username, self.app), { 'user_id': self.user})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Created at ./repos/{}/{}'.format(self.username, self.app).encode() in response.content)

    def tearDown(self):
        response = self.client.post('/{}/{}/delete'.format(self.username, self.app), { 'user_id': self.user})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Deleted at ./repos/{}/{}'.format(self.username, self.app).encode() in response.content)

    def test_path_generation(self):
        path = generate_directory('wevolver')
        path_duplicate = generate_directory('wevolver')
        alternate_path = generate_directory('testuser')
        self.assertEqual(path, path_duplicate)
        self.assertNotEqual(path, alternate_path)
        self.assertEqual(len(path.split('/')), 5)

    def test_created_bare(self):
        path = generate_directory(self.username)
        path = os.path.join(settings.REPO_DIRECTORY, path, self.app)
        repo = Repository(path)
        self.assertTrue(repo.is_bare)

    def test_add_files(self):
        with open(cwd + '/requirements.txt') as fp:
            response = self.client.post('/{}/{}/upload?user_id={}&path={}'.format(self.username, self.app, self.user, "test.json"), {'file': fp, 'path': 'test.json'})
        self.assertTrue(b'Files uploaded' in response.content)

    def test_list_files(self):
        with open(cwd + '/requirements.txt') as fp:
            self.client.post('/{}/{}/upload?path='.format(self.username, self.app, self.user), {'env': fp})
        response = self.client.get('/{}/{}?path='.format(self.username, self.app))
        self.assertEqual('requirements.txt', json.loads(response.content)['tree']['data'][1]['name'])

    def test_read_file(self):
        response = self.client.get('/{}/{}/readfile?path=documentation.md'.format(self.username, self.app))
        with open(cwd + '/welder/versions/starter.md','r') as readme:
            readme = readme.read().format(self.app)
        content = list(response.streaming_content)[0].decode("utf-8")
        self.assertEqual(readme, content)

    def test_permissions(self):
        pass
