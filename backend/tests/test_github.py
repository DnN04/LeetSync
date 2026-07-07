import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch
import pytest
import git
import httpx
from app.integrations.github import GitHubIntegration

@pytest.fixture
def temp_git_dir():
    # Setup temporary directory for local git repository tests
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup directory
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_validate_credentials_success():
    integration = GitHubIntegration(token="ghp_test", repo_name="owner/repo")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    
    with patch("httpx.Client.get", return_value=mock_response) as mock_get:
        assert integration.validate_credentials() is True
        mock_get.assert_called_once_with("https://api.github.com/repos/owner/repo", headers=integration.headers, timeout=10.0)

def test_validate_credentials_failure():
    integration = GitHubIntegration(token="ghp_test", repo_name="owner/repo")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    
    with patch("httpx.Client.get", return_value=mock_response):
        assert integration.validate_credentials() is False

def test_initialize_local_repo_new(temp_git_dir):
    # Mocking clone_from to simulate repo creation/init behavior without hitting remote
    integration = GitHubIntegration(token="ghp_test", repo_name="owner/repo", local_path=temp_git_dir)
    
    # We expect clone_from to fail or raise exception to fallback to local init in tests
    with patch("git.Repo.clone_from", side_effect=Exception("Clone failed")):
        repo = integration.initialize_local_repo()
        assert isinstance(repo, git.Repo)
        assert os.path.exists(os.path.join(temp_git_dir, ".git"))
        assert os.path.exists(os.path.join(temp_git_dir, "README.md"))

def test_commit_and_push_local_only(temp_git_dir):
    integration = GitHubIntegration(token="ghp_test", repo_name="owner/repo", local_path=temp_git_dir)
    
    with patch("git.Repo.clone_from", side_effect=Exception("Clone failed")):
        # Initialize local repository
        repo = integration.initialize_local_repo()
        
        # Patch the remote.push method to avoid connecting to GitHub
        mock_push = MagicMock()
        with patch.object(git.Remote, "push", return_value=mock_push):
            # Test file save and local commit
            commit_sha = integration.commit_and_push(
                file_relative_path="leetcode/Easy/Arrays/0001_Two_Sum/solution.py",
                file_content="print('Hello World')",
                commit_message="Solved #1 Two Sum"
            )
            
            assert commit_sha is not None
            assert len(commit_sha) == 40
            
            # Verify file exists
            saved_file_path = os.path.join(temp_git_dir, "leetcode/Easy/Arrays/0001_Two_Sum/solution.py")
            assert os.path.exists(saved_file_path)
            with open(saved_file_path, "r") as f:
                assert f.read() == "print('Hello World')"
