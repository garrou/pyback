from dotenv import load_dotenv
import json
import os
import requests
import sys

def __has_git_folder(dirpath: str) -> bool:
    return os.path.exists(os.path.join(dirpath, '.git'))

def get_arg(args: [str]) -> str:

    if len(args) != 2:
        print('error: needs one arg, the path to clone or pull')
        sys.exit(1)

    return args[1:][0]

def check_path(dirpath: str) -> None:

    if not (os.path.exists(dirpath) and os.path.isdir(dirpath)):
        print('error: invalid directory')
        sys.exit(1)

def get_git_projects_to_pull(dirpath: str) -> [str]:
    return [f.path for f in os.scandir(dirpath) if f.is_dir() and __has_git_folder(f.path)]

def scran_dir(dirpaths: [str]):
    
    for path in dirpaths: 
        print(f"Git pull at {path}")
        os.system(f"git -C {path} pull --all")

def get_github_repo_url() -> [tuple[str, str]]:

    token = os.getenv('TOKEN')
    url = 'https://api.github.com/user/repos?per_page=100'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print('error: cannot retrieve repos')
        sys.exit(1)
    
    return [(repo['name'], repo['html_url']) for repo in r.json()]

def create_missing_dir(dirpath: str, repos: [tuple[str, str]]) -> None:

    token = os.getenv('TOKEN')

    for r in repos:
        
        name, url = r

        if not os.path.exists(os.path.join(dirpath, name)):
            url = url[:8] + token + '@' + url[8:]
            os.system(f'git -C {dirpath} clone {url}')     

def main():

    path = get_arg(sys.argv)
    check_path(path)
    repos = get_github_repo_url()
    create_missing_dir(path, repos)
    dirpaths = get_git_projects_to_pull(path)
    scran_dir(dirpaths)

if __name__ == '__main__':
    load_dotenv()
    main()