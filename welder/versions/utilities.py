import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def fetch_repository(username, projectname):
    directory = porcelain.generate_directory(username)
    source_path = os.path.join(settings.REPO_DIRECTORY, directory, projectname)
    repo = pygit2.Repository(source_path)
    return repo
