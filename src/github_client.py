import os
from typing import Dict

import github
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
        # make a new public repo, blow up if it already exists
        user = self.gh.get_user()
        try:
            existing = user.get_repo(name)
            if existing:
                raise ValueError(f"Repository '{name}' already exists for user {self.username}")
        except UnknownObjectException:
            try:
                repo = user.create_repo(name=name, description=description, private=False)
                return repo
            except GithubException as e:
                raise RuntimeError(f"Failed to create repository: {e}") from e
        except GithubException as e:
            raise RuntimeError(f"GitHub API error checking repo existence: {e}") from e

    def push_file(self, repo, file_path: str, content: str, commit_message: str) -> bool:
        # push a single file — handles empty repos where get_contents throws 404
        try:
            try:
                existing = repo.get_contents(file_path)
                repo.update_file(existing.path, commit_message, content, existing.sha)
            except (UnknownObjectException, GithubException) as e:
                status = getattr(e, "status", None)
                msg = str(e)
                if status == 404 or "This repository is empty" in msg or "Not Found" in msg:
                    repo.create_file(file_path, commit_message, content)
                else:
                    raise
            return True
        except GithubException as e:
            raise RuntimeError(f"Failed to push file '{file_path}': {e}") from e

    def create_folder_structure(self, repo, files: Dict[str, str], commit_message: str = "initial project setup") -> bool:
        # batch all files into a single commit using git tree API
        # empty repos don't have a main branch yet, so we seed one first
        try:
            try:
                ref = repo.get_git_ref("heads/main")
                base_commit = repo.get_git_commit(ref.object.sha)
                base_tree = base_commit.tree
            except (UnknownObjectException, GithubException):
                # repo is empty — seed it with a placeholder so we have a ref
                repo.create_file(".gitkeep", "initial commit", "")
                ref = repo.get_git_ref("heads/main")
                base_commit = repo.get_git_commit(ref.object.sha)
                base_tree = base_commit.tree

            tree_elements = []
            for path, content in files.items():
                tree_elements.append(
                    github.InputGitTreeElement(
                        path=path,
                        mode="100644",
                        type="blob",
                        content=content,
                    )
                )

            new_tree = repo.create_git_tree(tree_elements, base_tree)
            new_commit = repo.create_git_commit(
                message=commit_message,
                tree=new_tree,
                parents=[base_commit],
            )
            ref.edit(new_commit.sha)
            return True

        except Exception as e:
            raise RuntimeError(f"Failed to push files in single commit: {e}") from e

    def create_issue(self, repo, title: str, body: str) -> int:
        try:
            issue = repo.create_issue(title=title, body=body)
            return issue.number
        except GithubException as e:
            raise RuntimeError(f"Failed to create issue: {e}") from e
