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
    nl_split = commit_message.split('\n', 1)
    p_split = commit_message.split('.', 1)
    index_split = [commit_message[:50], commit_message[51:]]

    if len(nl_split[0]) > 50 and len(p_split[0]) > 50:
        print(p_split)
        return index_split
    if len(nl_split[0]) > len(p_split[0]):
        return p_split;
    else:
        return nl_split;