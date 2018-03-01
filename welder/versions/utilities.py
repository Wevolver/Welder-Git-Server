from django.conf import settings

from welder.versions import porcelain

import pygit2
import logging
import os

logger = logging.getLogger(__name__)

def fetch_repository(username, projectname):
    directory = porcelain.generate_directory(username)
    source_path = os.path.join(settings.REPO_DIRECTORY, directory, projectname)
    repo = pygit2.Repository(source_path)
    return repo

def split_commit_message(commit_message):
    splits = [50,
              (commit_message.index('\n') if '\n' in commit_message else float("inf")),
              (commit_message.index('.') if '.' in commit_message else float("inf"))]

    return [commit_message[:min(splits)], commit_message[min(splits):]]
