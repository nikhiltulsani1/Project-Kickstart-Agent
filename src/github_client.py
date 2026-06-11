import os
from typing import Dict

from dotenv import load_dotenv
from github import Github
from github.GithubException import UnknownObjectException, GithubException


load_dotenv()


class GitHubClient:
    def __init__(self, token: str | None = None, username: str | None = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.username = username or os.getenv("GITHUB_USERNAME")
        if not self.token:
            raise EnvironmentError("GITHUB_TOKEN is not set in environment")
        if not self.username:
            raise EnvironmentError("GITHUB_USERNAME is not set in environment")

        self.gh = Github(self.token)

    def create_repo(self, name: str, description: str):
        """Create a public repository under the authenticated user.

        Raises ValueError if the repo already exists.
        Returns the created Repository object.
        """
        user = self.gh.get_user()
        try:
            # If repo exists, get_repo will succeed
            existing = user.get_repo(name)
            if existing:
                raise ValueError(f"Repository '{name}' already exists for user {self.username}")
        except UnknownObjectException:
            # Repo does not exist, create it
            try:
                repo = user.create_repo(name=name, description=description, private=False)
                return repo
            except GithubException as e:
                raise RuntimeError(f"Failed to create repository: {e}") from e
        except GithubException as e:
            raise RuntimeError(f"GitHub API error checking repo existence: {e}") from e

    def push_file(self, repo, file_path: str, content: str, commit_message: str) -> bool:
        """Create or update a file in the repository. Returns True on success."""
        try:
            try:
                existing = repo.get_contents(file_path)
                repo.update_file(existing.path, commit_message, content, existing.sha)
            except (UnknownObjectException, GithubException) as e:
                # PyGithub can raise GithubException with status 404 for empty repo
                status = getattr(e, "status", None)
                msg = str(e)
                if status == 404 or "This repository is empty" in msg or "Not Found" in msg:
                    repo.create_file(file_path, commit_message, content)
                else:
                    raise
            return True
        except GithubException as e:
            raise RuntimeError(f"Failed to push file '{file_path}': {e}") from e

    def create_issue(self, repo, title: str, body: str) -> int:
        """Create an issue in the given repo and return its number."""
        try:
            issue = repo.create_issue(title=title, body=body)
            return issue.number
        except GithubException as e:
            raise RuntimeError(f"Failed to create issue: {e}") from e

    def create_folder_structure(self, repo, files: Dict[str, str]) -> bool:
        """Push multiple files to the repository. `files` is a dict of path->content."""
        for path, content in files.items():
            ok = self.push_file(repo, path, content, commit_message=f"Add {path}")
            if not ok:
                return False
        return True
# Creates the repo, pushes the generated files, and opens the first sprint issues.
