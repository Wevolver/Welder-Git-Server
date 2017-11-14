from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_TIME, GIT_SORT_REVERSE
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseBadRequest
from django.http import StreamingHttpResponse
from django.conf import settings

from welder.permissions import decorators as permissions
from welder.analytics import decorators as mixpanel
from welder.notifications import decorators as notification
from welder.uploads import decorators as uploads
from welder.versions.git import GitResponse
from welder.versions import porcelain

from wsgiref.util import FileWrapper
from io import BytesIO
from time import time
from enum import Enum
import mimetypes
import itertools
import tokenlib
import logging
import tarfile
import base64
import pygit2
import shutil
import json
import os

logger = logging.getLogger(__name__)

class Actions(Enum):
    advertisement = 'advertisement'
    result = 'result'

@require_http_methods(["POST"])
@permissions.requires_permission_to("create")
@mixpanel.track
def create_project(request, user, project_name, permissions_token, tracking=None):
    """ Creates a bare repository (project) based on the user name
        and project name in the URL.

        It generates a unique path based on the user name and
        project, creates a default documentation and commits it.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        HttpResponse: A message indicating the success or failure of the create
    """

    directory = porcelain.generate_directory(user)
    path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)

    if not os.path.exists(os.path.join(settings.REPO_DIRECTORY, directory)):
        os.makedirs(os.path.join(settings.REPO_DIRECTORY, directory))

    try:
        repo = pygit2.init_repository(path, True)
        tree = repo.TreeBuilder()
        message = "Automated Initial Commit"
        author = pygit2.Signature('Wevolver', 'Wevolver')
        comitter = pygit2.Signature('Wevolver', 'Wevolver')
        privacy = request.GET.get('privacy')
        public, private = "0", "2"
        if privacy == private:
            with open('welder/versions/privatestarter.md','r') as documentation:
                documentation = documentation.read().format(project_name)
        else:
            with open('welder/versions/starter.md','r') as documentation:
                documentation = documentation.read().format(project_name)
        blob = repo.create_blob(documentation)
        tree.insert('documentation.md', blob, pygit2.GIT_FILEMODE_BLOB)
        sha = repo.create_commit('HEAD', author, comitter, message, tree.write(), [])
        response = HttpResponse("Created at ./repos/{}/{}".format(user, project_name))
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("looks like you already have a project with this name!")
    return response

@require_http_methods(["POST"])
@permissions.requires_permission_to("create")
@mixpanel.track
def create_branch(request, user, project_name, permissions_token, tracking=None):

    try:
        post = request.POST
        directory = porcelain.generate_directory(user)
        source_path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))

        branch = post['branch_name']
        commit = repo[repo.head.target]

        reference = repo.branches.create(branch, commit)

        response = HttpResponse("Created branch {} on ./repos/{}/{}".format(branch, user, project_name))

    except KeyError as e:
        response = HttpResponseBadRequest("The requested path doesn't exist!")
    except AttributeError as e:
        response = HttpResponseBadRequest("The request is missing a path parameter")
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("looks like you already have a project with this name!")
    return response

@require_http_methods(["POST"])
@permissions.requires_permission_to("create")
@mixpanel.track
def fork_project(request, user, project_name, permissions_token, tracking=None):
    """ Creates a bare repository (project) based on the user name
        and project name in the URL.

        It generates a unique path based on the user name and
        project, creates a default documentation and commits it.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        HttpResponse: A message indicating the success or failure of the create
    """
    try:
        post = request.POST
        directory = porcelain.generate_directory(user)
        source_path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)

        current_user = post['cloning_user'].lstrip('/').rstrip('/')
        directory = porcelain.generate_directory(current_user)
        destination_path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
        if not os.path.exists(os.path.join(settings.REPO_DIRECTORY, directory)):
            os.makedirs(os.path.join(settings.REPO_DIRECTORY, directory))

        shutil.copytree(source_path, destination_path)
        response = HttpResponse("Cloned at ./repos/{}/{}".format(user, project_name))
    except json.decoder.JSONDecodeError as e:
        response = HttpResponseBadRequest("The requested path parameter doesn't exist!")
    except KeyError as e:
        response = HttpResponseBadRequest("The requested path doesn't exist!")
    except AttributeError as e:
        response = HttpResponseBadRequest("The request is missing a path parameter")
    except FileExistsError as e:
        response = HttpResponseBadRequest("looks like you already have a project with this name!")
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("looks like you already have a project with this name!")
    return response

@require_http_methods(["POST"])
@permissions.requires_permission_to("write")
@mixpanel.track
def rename_project(request, user, project_name, permissions_token, tracking=None):
    """ Renames a project

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        HttpResponse: A message indicating the success or failure of the rename
    """
    try:
        post = request.POST
        directory = porcelain.generate_directory(user)
        new_name = post['new_name'].lstrip('/').rstrip('/')

        source_path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
        destination_path = os.path.join(settings.REPO_DIRECTORY, directory, new_name)

        os.rename(source_path, destination_path)
        response = HttpResponse("Renamed at ./repos/{}/{}".format(user, new_name))

    except KeyError as e:
        response = HttpResponseBadRequest("The request doesn't include a new_name parameter")
    except OSError as e:
        response = HttpResponseBadRequest("You already have a project with this name")
    except FileNotFoundError as e:
        response = HttpResponseBadRequest("You don't have a project with this name")
    return response

@require_http_methods(["POST"])
@permissions.requires_permission_to('write')
@mixpanel.track
def delete_project(request, user, project_name, permissions_token, tracking=None):
    """ Finds the repository specified in the URL and deletes from the file system.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        HttpResponse: A message indicating the success or failure of the delete
    """

    try:
        directory = porcelain.generate_directory(user)
        path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
        shutil.rmtree(path)
        response = HttpResponse("Deleted at ./repos/{}/{}".format(user, project_name))
    except FileNotFoundError as e:
        response = HttpResponseBadRequest("Not a repository.")
    response['Permissions'] = permissions_token
    return response

@require_http_methods(["POST"])
@permissions.requires_permission_to("create")
@mixpanel.track
def delete_branch(request, user, project_name, permissions_token, tracking=None):

    try:
        post = request.POST
        directory = porcelain.generate_directory(user)
        source_path = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        branch = request.GET['branch']
        repo.branches.delete(branch)
        response = HttpResponse("Deleted branch {} on ./repos/{}/{}".format(branch, user, project_name))

    except KeyError as e:
        response = HttpResponseBadRequest("The requested path doesn't exist!")
    except AttributeError as e:
        response = HttpResponseBadRequest("The request is missing a path parameter")
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("looks like you already have a project with this name!")
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def read_file(request, user, project_name, permissions_token, tracking=None):
    """ Finds a file in the path of the repository specified by the URL
        and returns the blob.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        StreamingHttpResponse: The file's raw data.
    """
    try:
        path = request.GET.get('path').lstrip('/').rstrip('/')
        oid = request.GET.get('oid')
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        download = request.GET.get('download')
        directory = porcelain.generate_directory(user)
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        parsed_file = None
        data = None
        type_blob = 3
        if oid:
            git_blob = repo.read(oid)
            if git_blob[0] is type_blob:
                data = git_blob[1]
        else:
            root_tree = repo.revparse_single(branch).tree
            git_tree, git_blob = porcelain.walk_tree(repo, root_tree, path)
            if type(git_blob) == pygit2.Blob:
                data = git_blob.data

        parsed_file = str(base64.b64encode(data), 'utf-8')
        chunk_size = 8192
        filelike = FileWrapper(BytesIO(data), chunk_size)
        response = StreamingHttpResponse(filelike, content_type=mimetypes.guess_type(path)[0])
        response['Content-Length'] = len(data)
        response['Permissions'] = permissions_token
        if download:
            response['Content-Disposition'] = "attachment; filename=%s" % path
    except KeyError as e:
        response = HttpResponseBadRequest("The requested path doesn't exist!")
    except TypeError as e:
        response = HttpResponseBadRequest("The file doesn't exist!")
    except AttributeError as e:
        response = HttpResponseBadRequest("The request is missing a path parameter")
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("Not a git repository.")
    return response

@require_http_methods(["POST"])
@permissions.requires_permission_to("write")
@uploads.add_handlers
@notification.notify("committed to")
@mixpanel.track
def receive_files(request, user, project_name, permissions_token=None, tracking=None):
    """ Receives and commits an array of files to a specific path in the repository.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: An object
    """
    try:
        directory = porcelain.generate_directory(user)
        email = request.POST.get('email', 'git@wevolver.com')
        message = request.POST.get('commit_message', 'received new files')
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        if request.FILES:
            blobs = []
            for key, file in request.FILES.items():
                blob = repo.create_blob(file.read())
                # content_type_extra contains the full path of the file
                # with respect to the root of the tree.
                # This is inserted in the custom upload handler.
                blobs.append((blob, file.content_type_extra))

            new_commit_tree = porcelain.add_blobs_to_tree(repo, branch, blobs)
            porcelain.commit_tree(repo, branch, new_commit_tree, user, email, message)
            response = JsonResponse({'message': 'Files uploaded'})
        else:
            response = JsonResponse({'message': 'No files received'})
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("The repository for this project could not be found.")
    except error:
        print('error')
    return response

@require_http_methods(["POST"])
@permissions.requires_permission_to("write")
@uploads.add_handlers
@notification.notify("committed to")
@mixpanel.track
def delete_files(request, user, project_name, permissions_token=None, tracking=None):
    try:
        directory = porcelain.generate_directory(user)
        email = request.POST.get('email', 'git@wevolver.com')
        message = request.POST.get('commit_message', 'received new files')
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        files = request.POST.get('files', None)
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        if files:
            new_commit_tree = porcelain.remove_files_by_path(repo, branch, files.split(','))
            porcelain.commit_tree(repo, branch, new_commit_tree, user, email, message)
            response = JsonResponse({'message': 'Files Deleted'})
        else:
            response = JsonResponse({'message': 'No Files Deleted'})
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("The repository for this project could not be found.")
    response['Permissions'] = permissions_token
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def list_bom(request, user, project_name, permissions_token, tracking=None):
    """ Collects all the bom.csv files in a repository and return their sum.

        Flattens the repository's tree into an array. Then filters the array for 'bom.csv',
        concatenates them and returns unique lines.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        HttpResponse: The full Bill of Materials (BOM)
    """

    try:
        directory = porcelain.generate_directory(user)
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        tree = (repo.revparse_single(branch).tree)
        blobs = porcelain.flatten(tree, repo)
        data = ''
        for b in [blob for blob in blobs if blob.name == 'bom.csv']:
            data += str(repo[b.id].data, 'utf-8')
        response = HttpResponse(data)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest('not a repository')
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def list_branches(request, user, project_name, permissions_token):
    """ Collects and returns all the names of the branches from the repository.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: The list of branches
    """
    try:
        directory = porcelain.generate_directory(user)
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        branches = {'branches': [repo for repo in repo.branches]}
        response = JsonResponse(branches)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest('not a repository')
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def list_branches_ahead_behind(request, user, project_name, permissions_token, tracking=None):
    """ Returns the number of commits each branch is ahead or behind master

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: The list of branches and their status
    """
    try:
        directory = porcelain.generate_directory(user)
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        branches = {}
        for branch in repo.branches:
            branches[branch] = {"ahead": 0, "behind": 0}
            ahead, behind = repo.ahead_behind(repo.lookup_branch(branch).target.hex, repo.lookup_branch('master').target.hex)
            branches[branch]['ahead'] = ahead
            branches[branch]['behind'] = behind
        response = JsonResponse(branches)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest('not a repository')
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def download_archive(request, user, project_name, permissions_token, tracking=None):
    """ Grabs and returns a user's repository as a tarball.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.

    Returns:
        JsonResponse: An object with the requested user's repository as a tarball.
    """
    branch = request.GET.get('branch', 'master')
    filename = project_name + '.tar'
    response = HttpResponse(content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    directory = porcelain.generate_directory(user)

    try:
        with tarfile.open(fileobj=response, mode='w') as archive:
            repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
            repo.write_archive(repo.revparse_single(branch).id, archive)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("Not a repository")
    return response

@require_http_methods(["GET"])
@permissions.requires_git_permission_to('read')
def info_refs(request, user, project_name, tracking=None):
    """ Initiates a handshake for a smart HTTP connection

    https://git-scm.com/book/en/v2/Git-Internals-Transfer-Protocols

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.

    Returns:
        GitResponse: A HttpResponse with the proper headers and payload needed by git.
    """

    directory = porcelain.generate_directory(user)
    requested_repo = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
    response = GitResponse(service=request.GET['service'], action=Actions.advertisement.value,
                           repository=requested_repo, data=None)
    return response.get_http_info_refs()

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def list_bom(request, user, project_name, permissions_token, tracking=None):
    """ Collects all the bom.csv files in a repository and return their sum.

        Flattens the repository's tree into an array. Then filters the array for 'bom.csv',
        concatenates them and returns unique lines.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        HttpResponse: The full Bill of Materials (BOM)
    """

    try:
        directory = porcelain.generate_directory(user)
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        tree = (repo.revparse_single(branch).tree)
        blobs = porcelain.flatten(tree, repo)
        data = ''
        for b in [blob for blob in blobs if blob.name == 'bom.csv']:
            data += str(repo[b.id].data, 'utf-8')
        response = HttpResponse(data)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest('not a repository')
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def list_branches(request, user, project_name, permissions_token):
    """ Collects and returns all the names of the branches from the repository.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: The list of branches
    """
    try:
        directory = porcelain.generate_directory(user)
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        branches = {'branches': [repo for repo in repo.branches]}
        response = JsonResponse(branches)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest('not a repository')
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def list_branches_ahead_behind(request, user, project_name, permissions_token, tracking=None):
    """ Returns the number of commits each branch is ahead or behind master

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: The list of branches and their status
    """
    try:
        directory = porcelain.generate_directory(user)
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        branches = {}
        for branch in repo.branches:
            branches[branch] = {"ahead": 0, "behind": 0}
            branch_latest_commit_oid = repo.lookup_branch(branch).target;
            ahead, behind = repo.ahead_behind(branch_latest_commit_oid.hex, repo.lookup_branch('master').target.hex)
            branches[branch]['ahead'] = ahead
            branches[branch]['behind'] = behind
            branches[branch]['commit_time'] = repo.get(branch_latest_commit_oid).commit_time
        response = JsonResponse(branches)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest('not a repository')
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def download_archive(request, user, project_name, permissions_token, tracking=None):
    """ Grabs and returns a user's repository as a tarball.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.

    Returns:
        JsonResponse: An object with the requested user's repository as a tarball.
    """
    branch = request.GET.get('branch', 'master')
    filename = project_name + '.tar'
    response = HttpResponse(content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    directory = porcelain.generate_directory(user)

    try:
        with tarfile.open(fileobj=response, mode='w') as archive:
            repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
            repo.write_archive(repo.revparse_single(branch).id, archive)
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("Not a repository")
    return response

@require_http_methods(["GET"])
@mixpanel.track
@permissions.requires_git_permission_to('read')
def info_refs(request, user, project_name, permissions_token=None,  tracking=None):
    """ Initiates a handshake for a smart HTTP connection

    https://git-scm.com/book/en/v2/Git-Internals-Transfer-Protocols

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.

    Returns:
        GitResponse: A HttpResponse with the proper headers and payload needed by git.
    """

    directory = porcelain.generate_directory(user)
    requested_repo = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
    response = GitResponse(service=request.GET['service'], action=Actions.advertisement.value,
                           repository=requested_repo, data=None)
    return response.get_http_info_refs()

@permissions.requires_git_permission_to('read')
@mixpanel.track
def upload_pack(request, user, project_name, tracking=None):
    """ Calls service_rpc assuming the user is authenticated and has read permissions """

    return service_rpc(user, project_name, request.path_info.split('/')[-1], request.body)

@permissions.requires_git_permission_to('write')
@mixpanel.track
@notification.notify("committed to")
def receive_pack(request, user, project_name, permissions_token=None, tracking=None):
    """ Calls service_rpc assuming the user is authenticated and has write permissions """

    return service_rpc(user, project_name, request.path_info.split('/')[-1], request.body)

@mixpanel.track
def service_rpc(user, project_name, request_service, request_body, permissions_token=None, tracking=None):
    """ Calls the Git commands to pull or push data from the server depending on the received service.

    https://git-scm.com/book/en/v2/Git-Internals-Transfer-Protocols

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.

    Returns:
        GitResponse: An HttpResponse that indicates success or failure and may include the requested packfile
    """

    directory = porcelain.generate_directory(user)
    request_repo = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
    response = GitResponse(service=request_service, action=Actions.result.value,
                           repository=request_repo, data=request_body)
    return response.get_http_service_rpc()

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def read_tree(request, user, project_name, permissions_token, tracking=None):
    """ Grabs and returns a single file or a tree from a user's repository

        The requested tree is first parsed into JSON.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: An object with the requested tree as JSON
    """
    try:
        path = request.GET.get('path').rstrip('/').lstrip('/')
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        directory = porcelain.generate_directory(user)
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        root_tree = repo.revparse_single(branch).tree
        git_tree, git_blob = porcelain.walk_tree(repo, root_tree, path)
        parsed_tree = None
        if type(git_tree) == pygit2.Tree:
            parsed_tree = porcelain.parse_file_tree(git_tree)
        response = JsonResponse({'tree': parsed_tree})
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("Not a git repository")
    except AttributeError as e:
        response = HttpResponseBadRequest("No path parameter")
    response['Permissions'] = permissions_token
    return response

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def read_history(request, user, project_name, permissions_token, tracking=None):
    """ Grabs and returns the history of a single file.

       The commit history of the branch is parsed and the file of
       interest is found on each commit tree.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: The history of the file at this path.
    """
    try:
        path = request.GET.get('path').rstrip('/').lstrip('/')
        history_type = request.GET.get('type')
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        directory = porcelain.generate_directory(user)
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        root_tree = repo.revparse_single(branch).tree

        git_tree, git_blob = porcelain.walk_tree(repo, root_tree, path)

        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 0))
        start_index = page_size * page
        history = []
        for commit in itertools.islice(repo.walk(repo.revparse_single(branch).id, GIT_SORT_TIME), start_index,  start_index + page_size ):
            try:
                title, description = commit.message.split('\n\n', 1)
            except:
                title, description = commit.message, None
            if history_type == 'file':
                git_tree, git_blob = porcelain.walk_tree(repo, commit.tree, path)
                if type(git_blob) == pygit2.Blob:
                    if not any(item.get('id', None) == git_blob.id.__str__() for item in history):
                        history.append({
                            'id': git_blob.id.__str__(),
                            'commit_time': commit.commit_time,
                            'commit_description': description,
                            'commit_title': title
                        })
            elif history_type == 'commits':
                history.append({
                    'author': commit.author.email,
                    'committer': commit.committer.email,
                    'commit_description': description,
                    'commit_title': title,
                    'commit_time': commit.commit_time,
                    'commit_id': commit.id.__str__()
                })
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("Not a git repository")
    except AttributeError as e:
        response = HttpResponseBadRequest("No path parameter")
    return JsonResponse({'history': history})

@require_http_methods(["GET"])
@permissions.requires_permission_to('read')
@mixpanel.track
def read_tree(request, user, project_name, permissions_token, tracking=None):
    """ Grabs and returns a single file or a tree from a user's repository

        The requested tree is first parsed into JSON.

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.
        permissions_token (string): JWT token signed by Wevolver.

    Returns:
        JsonResponse: An object with the requested tree as JSON
    """
    try:
        path = request.GET.get('path').rstrip('/').lstrip('/')
        branch = request.GET.get('branch') if request.GET.get('branch') else 'master'
        directory = porcelain.generate_directory(user)
        repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
        root_tree = repo.revparse_single(branch).tree
        git_tree, git_blob = porcelain.walk_tree(repo, root_tree, path)
        parsed_tree = None
        if type(git_tree) == pygit2.Tree:
            parsed_tree = porcelain.parse_file_tree(git_tree)
        response = JsonResponse({'tree': parsed_tree})
    except pygit2.GitError as e:
        response = HttpResponseBadRequest("Not a git repository")
    except AttributeError as e:
        response = HttpResponseBadRequest("No path parameter")
    response['Permissions'] = permissions_token
    return response
