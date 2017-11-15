import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def fetch_repository(username, projectname):
    directory = porcelain.generate_directory(user)
    source_path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
    repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
