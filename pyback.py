from dotenv import load_dotenv
import json
import os
import requests
import sys

def __has_git_folder(dirpath: str) -> bool:
    return os.path.exists(os.path.join(dirpath, '.git'))

def __check_path(dirpath: str) -> str:

    if not (os.path.exists(dirpath) and os.path.isdir(dirpath)):
        print('error: invalid directory')
        sys.exit(1)

    return dirpath

def __construct_path(dirpath: str, projects: [str]) -> [str]:
    return [os.path.join(dirpath, p) for p in projects]

def get_path_from_args(args: [str]) -> str:

    if len(args) != 1:
        print('error: needs one arg, the path to clone or pull')
        sys.exit(1)

    return __check_path(args[0])

def get_git_projects_to_pull(fullpaths: [str]) -> [str]:
    return [p for p in fullpaths if os.path.isdir(p) and __has_git_folder(p)]

def gitpull_in_existing_projects(dirpaths: [str]):
    
    for path in dirpaths: 
        print(f'git pull {path}')
        os.system(f"git -C {path} pull --all")
        print()

def get_github_repos() -> [tuple[str, str]]:

    token = os.getenv('TOKEN')
    page = 1
    repos = []
    fetching = True

    while fetching:

        url = 'https://api.github.com/user/repos'
        params = {
            'page': page,
            'per_page': 100
        }
        headers = {
            'Authorization': f'Bearer {token}'
        }
        r = requests.get(url, headers=headers, params=params)

        if r.status_code != 200:
            print('error: cannot retrieve repos')
            sys.exit(1)

        json_res: [any] = r.json()

        if len(json_res) == 0:
            fetching = False
        else:
            repos.extend([(repo['name'], repo['html_url']) for repo in json_res])
            page += 1

    return repos

def clone_missing_project(dirpath: str, repos: [tuple[str, str]]) -> [str]:

    token = os.getenv('TOKEN')
    existing_projects = []

    for r in repos:
        
        name, url = r

        if not os.path.exists(os.path.join(dirpath, name)):
            # https://<github_pat>@github.com/<user>/<repo>
            url = url[:8] + token + '@' + url[8:]
            os.system(f'git -C {dirpath} clone {url}')
            print()     
        else:
            existing_projects.append(name)

    return __construct_path(dirpath, existing_projects)

def main():

    path = get_path_from_args(sys.argv[1:])
    repos = get_github_repos()
    existing_projects = clone_missing_project(path, repos)
    existing_projects = get_git_projects_to_pull(existing_projects)
    gitpull_in_existing_projects(existing_projects)

if __name__ == '__main__':
    load_dotenv()
    main()