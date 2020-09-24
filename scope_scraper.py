import itertools

import requests
from github import Github
import re
import os

debug = True

if not debug:
    PROJECT_OWNER = "cwtools"
    REPO_NAME = "cwtools-ck3-config"
    URL_BASE = "https://api.github.com"
else:
    PROJECT_OWNER = "Zonr0"
    REPO_NAME = "FakeRepo"
    URL_BASE = "https://api.github.com"

CK3_PATH = os.environ["CK3_PATH"]
CWT_PATH = os.environ["CK3_PATH"]

def enumerate_ck3_directories(path):
    return


def enumerate_files(path,folder_exclude_filter=None,file_ext_exclude_filter=None,file_name_exclude_filter=None):
    def filter_list(filter_name,index):
        """Sub-function to filter the list down"""
        if not filter_name:
            return working_list
        return [f for f in working_list if os.path.splitext(f[2])[index] not in filter_name]
    # We could do this much much more efficiently, but this is a single use tool and its not worth the engineering
    # effort to be super elegant here. Thus, we remove many common things we don't want through hard coded multiple
    # passes.
    working_list = list()
    for root, dirs, files in os.walk(path,topdown=True):
        for folder in dirs:
            for f in folder_exclude_filter:
                # Feels weird to do this in the loop, but taken almost exactly from docs.
                if f in folder:
                    dirs.remove(folder)
            for file in files:
                working_list.append((root,folder,file))

    working_list = filter_list(file_ext_exclude_filter,-1) # Ordered by largest groups to eliminate first
    working_list = filter_list(file_name_exclude_filter,-2)
    # for root, dir, file in working_list:
    #     print(os.path.join(root,dir,file))
    return working_list

if __name__ == '__main__':
    g = Github(os.environ['GH_API_KEY'])
    repo = g.get_repo(f"{PROJECT_OWNER}/{REPO_NAME}")
    open_issues = repo.get_issues(state='open')
    for issue in open_issues:
        print(issue)
    folders = []
    for sub_path in ('common','history'):
        folders.extend(enumerate_files(os.path.join(CWT_PATH,sub_path),
                    folder_exclude_filter=('localization','gfx','tools','gui'),
                    file_ext_exclude_filter=('.gui','.font','yml','.shortcuts'),
                    file_name_exclude_filter=('achievement_groups.txt')))
    folders = list(set([folder[1] for folder in folders]))
    for f in folders:
        print(f)
