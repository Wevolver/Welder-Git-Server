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

def parse_file_tree(repo, tree, folder_path):
    """ Parses the repository's tree structure into JSON.

    Args:
        tree (Tree): The most recent commit tree.

    Returns:
        dict: A list of all blobs and trees in the provided tree.
    """
    data = []
    for node in tree:
        full_path = folder_path + [str(node.name)]
        tree_object = {
            'name': str(node.name),
            'type': str(node.type),
            'oid': str(node.id),
            'size': repo[node.id].size if node.type == 'blob' else 0,
            'folder_path': '/'.join(full_path)
        }

        pointer_marker = 'version https://git-lfs.github.com/spec/v1'
        try:
            split_pointer = repo[node.id].data[:200].decode().splitlines()
            if split_pointer[0] == pointer_marker:
                pointer_object = {}
                for line in split_pointer:
                    key_value = line.split(' ')
                    pointer_object[key_value[0]] = key_value[1]
                tree_object['lfs'] = pointer_object['oid']
                tree_object['size'] = pointer_object['size']
        except Exception as e:
            print(e)

        data.append(tree_object)
    return { 'data': data }
    # return {'data': [{'name': str(node.name), 'type': str(node.type), 'oid': str(node.id), 'size': repo[node.id].size if node.type == 'blob' else 0} for node in tree]}


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
    print(locations)
    for index, location in enumerate(locations):
        try:
            next_object = current_object.__getitem__(location)
        except KeyError as e:
            locations.pop()
            return current_object, None, locations
        temp_object = current_object
        current_object = repo.get(next_object.id)
        if type(current_object) == pygit2.Blob:
            blob = current_object
            current_object = temp_object
            locations.pop()
    return current_object, blob, locations


def add_blobs_to_tree(repo, branch, blobs):
    """ Adds blobs to a tree.

        Create an index file from a specific branch tree.
        Add the blobs to it, the path must be the full path from root to the name of the blob.
        Write the index file to a new tree and return.

    Args:
        repo (Repository): The user's repository.
        branch: The name of the branch we want to commit to.
        blobs: New blobs to be added.

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

def remove_files_by_path(repo, branch, files):

    tree = repo.revparse_single(branch).tree
    index = repo.index
    index.read_tree(tree)
    for entry in index:
        print(entry.path, entry.hex)

    for filepath in files:
        index.remove(filepath) 

    return index.write_tree()

def commit_tree(repo, branch, newTree, name='Wevolver', email='git@wevolver.com', message='None'):
    """ Commits tree to a repository.

    Args:
        repo (Repository): The user's repository.
        newTree (Tree): Tree with new objects.
    """
    author_signature = pygit2.Signature(name, email, int(time()), 0)
    committer_signature = pygit2.Signature(name, email, int(time()), 0)
    branch_obj = repo.branches.get(branch)
    commit = repo.create_commit(branch_obj.name, author_signature, committer_signature, message, newTree, [branch_obj.target])

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
