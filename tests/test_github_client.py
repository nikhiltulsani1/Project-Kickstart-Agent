import pytest

from src.github_client import GitHubClient


REPO_NAME = "test-pksa-delete-me"


@pytest.fixture(scope="module")
def gh_repo():
    client = GitHubClient()
    # Ensure clean start: if repo exists, try to delete first
    user = client.gh.get_user()
    try:
        existing = user.get_repo(REPO_NAME)
        try:
            existing.delete()
        except Exception:
            pass
    except Exception:
        pass

    try:
        repo = client.create_repo(REPO_NAME, "Temporary test repository for PKSA tests")
    except ValueError:
        # Repo already exists; use the existing one
        repo = user.get_repo(REPO_NAME)
    try:
        yield repo
    finally:
        # Attempt to delete repo after tests
        try:
            repo.delete()
        except Exception:
            pass


def test_repo_created(gh_repo):
    assert "github.com" in gh_repo.html_url


def test_push_file(gh_repo):
    client = GitHubClient()
    ok = client.push_file(gh_repo, "test.md", "# Test", "Add test.md")
    assert ok is True


def test_create_issue(gh_repo):
    client = GitHubClient()
    issue_number = client.create_issue(gh_repo, "Test issue", "This is a test issue created by pytest")
    assert isinstance(issue_number, int)
