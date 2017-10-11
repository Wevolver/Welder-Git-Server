from time import time
import requests
import hashlib
import pygit2
import os

def generate_directory(username):
    """ Generates a unique directory structure for the project based on the user name.

    https://github.com/blog/117-scaling-lesson-23742

    Args:
        username (string): The user's name slug
    Returns:
        Path (str): The unique path as a string
    """
    hash = hashlib.md5();
    hash.update(username.encode('utf-8'))
    hash = hash.hexdigest()
    a, b, c, d, *rest= hash[0], hash[1:3], hash[3:5], hash[5:7]
    return os.path.join(a, b, c, d, username)

def parse_file_tree(tree):
    """ Parses the repository's tree structure into JSON.

    Args:
        tree (Tree): The most recent commit tree.

    Returns:
        dict: A list of all blobs and trees in the provided tree.
    """

    return {'data': [{'name': str(node.name), 'type': str(node.type), 'oid': str(node.id)} for node in tree]}


def walk_tree(repo, root_tree, full_path):
    """ Given a path in returns the object.

        If the object is a blob it returns the previous object as the tree else blob is None.

    Args:
        repo (Repository): The user's repository.
        full_path (string): The full path to the object.

    Returns:
        current_object: The last tree in the path.
        blob: The requested blob if there is one.
    """
    current_object = root_tree
    locations = full_path.split('/')
    if locations[0] == "":
        locations = []
    blob = None
    for location in locations:
        try:
            next_object = current_object.__getitem__(location)
        except KeyError as e:
            return None, None
        temp_object = current_object
        current_object = repo.get(next_object.id)
        if type(current_object) == pygit2.Blob:
            blob = current_object
            current_object = temp_object
    return current_object, blob


def add_blob_to_tree(repo, branch, blobs):
    """ Adds blobs to a tree at a given path.

        Traverse the repository to find the given path to a blob.
        If the path to the blob does not exist it creates the necessary trees.
        Then add blob to the last tree.
        Then in reverse order trees are inserted into their parent up to the root.
        Insert the new tree into the previous one to make a new snapshot.

    Args:
        previous_commit_tree: The tree object of the last commit.
        repo (Repository): The user's repository.
        blobs: New blobs to be added to a specific path.
        path (string): The full path to the object.

    Returns:
        tree: New tree with the blobs added.
    """

    tree = repo.revparse_single(branch).tree
    index = repo.index
    index.read_tree(tree)

    for blob, path in blobs:
        entry = pygit2.IndexEntry(path, blob, pygit2.GIT_FILEMODE_BLOB)
        index.add(entry)

    return index.write_tree()

def commit_tree(repo, newTree, name='Wevolver', email='git@wevolver.com', message='None'):
    """ Commits tree to a repository.

    Args:
        repo (Repository): The user's repository.
        newTree (Tree): Tree with new objects.
    """
    author_signature = pygit2.Signature(name, email, int(time()), 0)
    committer_signature = pygit2.Signature(name, email, int(time()), 0)
    commit = repo.create_commit(repo.head.name, author_signature, committer_signature, message, newTree, [repo.head.peel().id])

def flatten(tree, repo):
    """ Translates a tree structure into a single level array.

    Args:
        repo (Repository): The user's repository.
        tree (Tree): Tree to be flattened.

    Returns:
        list: flattened tree
    """
    flattened = []
    for entry in tree:
        if entry.type == 'tree':
            flattened.extend(flatten(repo[entry.id], repo))
        else:
            flattened.append(entry)
    return flattened
