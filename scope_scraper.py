import itertools

import requests
from github import Github
import json
import atexit
import os
import sqlite3
from time import sleep

debug = True

if not debug:
    PROJECT_OWNER = "abcdefgcwtools"
    REPO_NAME = "cwtools-ck3-config"
    URL_BASE = "https://api.github.com"
else:
    PROJECT_OWNER = "Zonr0"
    REPO_NAME = "FakeRepo"
    URL_BASE = "https://api.github.com"

CK3_PATH = os.environ["CK3_PATH"]
CWT_PATH = os.environ["CK3_PATH"]



def split_folders(path):
    path = os.path.normpath(path)
    return path.split(os.sep)


def enumerate_files(path, folder_exclude_filter=None, file_ext_exclude_filter=None, file_name_exclude_filter=None):
    # We could do this much much more efficiently, but this is a single use tool and its not worth the engineering
    # effort to be super elegant here. Thus, we remove many common things we don't want through hard coded multiple
    # passes.
    top_levels = ('common', 'game')
    working_list = list()
    folders = list()
    for root, dirs, files in os.walk(path, topdown=True):
        for folder in dirs:
            for f in folder_exclude_filter:
                # Feels weird to do this in the loop, but taken almost exactly from docs.
                if f in folder:
                    pass
                    # dirs.remove(folder)
            preceding_folders = list()
            preceding_folder = "not a thing"
            levels_back = 1
            while preceding_folder not in top_levels:
                preceding_folder = split_folders(root)[-levels_back]
                if preceding_folder not in top_levels:
                    preceding_folders.insert(0, preceding_folder)
                levels_back += 1

            preceding_folders.append(folder)
            print(preceding_folders)
            folders.append(preceding_folders)

            # print(os.path.join(*preceding_folders,folder))
            for file in files:
                working_list.append((root, folder, file))

    # print(folders)
    return folders

    # Get back the path: path.split(os.sep)) os.path.join(*(folder_list))


def create_heiarchy(folders):
    """Creates a janky home-grown tree cobbled together from dictionaries.
        :param folders: A list of ordered sublists of folders that make up a directory path"""
    heiarch = dict()
    for f in folders:
        working_dictionary = heiarch
        for g in f:
            if g not in working_dictionary:
                working_dictionary[g] = dict()
            working_dictionary = working_dictionary[g]
    return heiarch


def define_issue(key, heiarchy):
    """Defines the title and body of the github issue
        :param key: The top level key that forms the basis of the issue
        :param heiarchy: The larger heiarchy tree"""
    title = f"First pass implementation for {key} folder contents"
    subfolder_follow_up = "."
    if heiarchy[key]:
        subfolder_follow_up = " and the below listed sub-folders."
    body = f"Provide first pass implementation for the **{key}** folder{subfolder_follow_up}\n"
    if heiarchy[key]:
        for sub_key in heiarchy[key].keys():
            body += f"- [ ] {sub_key}\n"
            # Its not particularly elegant to hard code the depth by just repeating code, but we're not trying to
            # solve the general case here. We know the deepest nested structure we will find, and if PDX adds another
            # level at some point, its easy enough to just copy and paste.
            if heiarchy[key][sub_key]:
                for sub_sub_key in heiarchy[key][sub_key].keys():
                    body += f"\t- [ ] {sub_sub_key}\n"
                    if heiarchy[key][sub_key][sub_sub_key]:
                        for sub_sub_sub_key in heiarchy[key][sub_key][sub_sub_sub_key].keys():
                            body += f"\t\t- [ ] {sub_sub_sub_key}\n"

    body += \
"""\nFirst pass implementation means that all (valid) keys used in vanilla files either:
- Have full working implementations OR
- Have working placeholder implementations (eg. simple scalars) with status documented on the tracker OR
- Have false positives in a placeholder or incomplete implementation that properly covers the majority of use cases. OR
- Have false positives or are unimplementable due to bugs or missing features in cwtools core
        
Additionally, before this issue can be closed, please make sure of the following:
- All significant TODO items are documented in the issue tracker
- Documentation strings are either present or documented as missing in the tracker
        
That being said, these are just the criteria for this issue and scope item to be considered finished. In these early days, every new definition is incredibly helpful for end users trying to use cwtools! PRs with partial implementations are more than welcome!\n
"""

    body += "\n**This is an auto-generated issue.** It may make sense to close this ticket, combine it with others, " \
            "or split it into smaller chunks."
    return { 'title' : title,
             'body' : body }

if __name__ == '__main__':
    g = Github(os.environ['GH_API_KEY'])
    repo = g.get_repo(f"{PROJECT_OWNER}/{REPO_NAME}")
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        print(issue)
    folders = []
    for sub_path in ('common', 'history'):
        folders.extend(enumerate_files(os.path.join(CWT_PATH, sub_path),
                                       folder_exclude_filter=('localization', 'gfx', 'tools', 'gui'),
                                       file_ext_exclude_filter=('.gui', '.font', 'yml', '.shortcuts'),
                                       file_name_exclude_filter=('achievement_groups.txt')))

    heiarch = create_heiarchy(folders)
    issues = list()
    for top_level in heiarch.keys():
        issues.append(define_issue(top_level,heiarch))

    for issue in issues:
        print(repo.create_issue(title=issue['title'], body = issue['body'], labels=['new definitions','autogenerated']))
        sleep(10) # Go slowly so we don't get rate limited and so we can stop things if things go awry
