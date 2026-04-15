import os
from git import Repo

def clone_repo(repo_url: str):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    path = f"repos/{repo_name}"

    if not os.path.exists(path):
        Repo.clone_from(repo_url, path)

    return path