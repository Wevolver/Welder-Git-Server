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


def walk_tree(repo, full_path):
    """ Given a path in returns the object.

        If the object is a blob it returns the previous object as the tree else blob is None.

    Args:
        repo (Repository): The user's repository.
        full_path (string): The full path to the object.

    Returns:
        current_object: The last tree in the path.
        blob: The requested blob if there is one.
    """
    current_object = repo.revparse_single('master').tree
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

def add_blobs_to_tree(previous_commit_tree, repo, blobs, path):
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
    current_tree = previous_commit_tree
    trees = []

    if path[0] != '':
        for location in path:
            try:
                next_tree_entry = current_tree.__getitem__(location)
                current_tree = repo.get(next_tree_entry.id)
            except:
                current_tree = False
            trees.append(current_tree)

        is_tree = trees[-1]
        current_tree_builder = repo.TreeBuilder(trees[-1]) if is_tree else repo.TreeBuilder()
        for blob, name in blobs:
            current_tree_builder.insert(name, blob, pygit2.GIT_FILEMODE_BLOB)

        for index in range(len(path) - 1, 0, -1):
            previous_tree_builder = current_tree_builder
            is_tree = trees[index - 1]
            current_tree_builder = repo.TreeBuilder(is_tree) if is_tree else repo.TreeBuilder()
            current_tree_builder.insert(path[index], previous_tree_builder.write(), pygit2.GIT_FILEMODE_TREE)

        previous_commit_tree_builder = repo.TreeBuilder(previous_commit_tree)
        previous_commit_tree_builder.insert(path[0], current_tree_builder.write(), pygit2.GIT_FILEMODE_TREE)
        return previous_commit_tree_builder.write()
    else:
        previous_commit_tree_builder = repo.TreeBuilder(previous_commit_tree)
        for blob, name in blobs:
            previous_commit_tree_builder.insert(name, blob, pygit2.GIT_FILEMODE_BLOB)
        return previous_commit_tree_builder.write()

def commit_blob(repo, blob, path, name='readme.md'):
    """ Adds a blob to a tree and commits it to a repository.
        
    Args:
        repo (Repository): The user's repository.
        blob (Blob): The file object.
        path (string): The full path to the object.
        name (string): Filename of the blob.
    """

    previous_commit_tree = repo.revparse_single('master').tree
    newTree = add_blobs_to_tree(previous_commit_tree, repo, [(blob, name)], path)
    if newTree:
        commit_tree(repo, newTree)

def commit_tree(repo, newTree):
    """ Commits tree to a repository.
        
    Args:
        repo (Repository): The user's repository.
        newTree (Tree): Tree with new objects.
    """
    signature = pygit2.Signature('Tester', 'test@example.com', int(time()), 0)
    commit = repo.create_commit(repo.head.name, signature, signature, 'Test commit with pygit2', newTree, [repo.head.peel().id])

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
