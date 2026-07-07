import os
import shutil
import httpx
import logging
from pathlib import Path
from typing import Optional
import git
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GitHubIntegration:
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None, local_path: Optional[str] = None):
        self.token = token or settings.github_token
        self.repo_name = repo_name or settings.github_repo
        self.local_path = Path(local_path or settings.sync_repo_path)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def validate_credentials(self) -> bool:
        """Validates GitHub Token and verifies access to the target repository.
        
        Returns:
            bool: True if authorized, False otherwise.
        """
        if not self.token or not self.repo_name:
            logger.error("GitHub Token or Repository Name is not configured.")
            return False

        url = f"https://api.github.com/repos/{self.repo_name}"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, timeout=10.0)
                if response.status_code == 200:
                    logger.info(f"Successfully authenticated and verified access to repository: {self.repo_name}")
                    return True
                else:
                    logger.error(f"GitHub authentication failed. Status code: {response.status_code}, Response: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error connecting to GitHub API during authentication: {str(e)}")
            return False

    def get_clone_url(self) -> str:
        """Generates the authenticated clone URL for the repository."""
        return f"https://x-access-token:{self.token}@github.com/{self.repo_name}.git"

    def initialize_local_repo(self) -> git.Repo:
        """Initializes or clones the target GitHub repository locally.
        
        Returns:
            git.Repo: The initialized GitPython repository instance.
        """
        if not self.token or not self.repo_name:
            raise ValueError("GitHub credentials not configured. Cannot initialize repository.")

        self.local_path.mkdir(parents=True, exist_ok=True)
        git_dir = self.local_path / ".git"

        if git_dir.exists():
            try:
                logger.info(f"Loading existing Git repository at {self.local_path}")
                repo = git.Repo(self.local_path)
                # Verify or update remote origin URL to ensure authenticated token is up-to-date
                if "origin" in repo.remotes:
                    origin = repo.remotes.origin
                    origin.set_url(self.get_clone_url())
                else:
                    repo.create_remote("origin", self.get_clone_url())
                return repo
            except Exception as e:
                logger.warning(f"Failed to open existing repo: {e}. Re-initializing folder.")
                shutil.rmtree(self.local_path)
                self.local_path.mkdir(parents=True, exist_ok=True)

        # Clone remote repository or initialize a new one if it doesn't exist
        clone_url = self.get_clone_url()
        try:
            logger.info(f"Attempting to clone repository {self.repo_name} to {self.local_path}")
            repo = git.Repo.clone_from(clone_url, str(self.local_path))
            logger.info("Repository cloned successfully.")
            return repo
        except Exception as e:
            logger.warning(f"Could not clone repository: {e}. Creating a new local repository.")
            repo = git.Repo.init(self.local_path)
            origin = repo.create_remote("origin", clone_url)
            
            # Create a simple initial commit if branch is empty
            readme_path = self.local_path / "README.md"
            if not readme_path.exists():
                readme_path.write_text(f"# LeetCode Solutions\n\nAutomatically synchronized using LeetSync Pro.")
                repo.index.add(["README.md"])
                repo.index.commit("Initial commit from LeetSync Pro")
                
            # Rename default branch to main
            try:
                repo.git.branch("-M", "main")
            except Exception:
                pass
            return repo

    def commit_and_push(self, file_relative_path: str, file_content: str, commit_message: str) -> str:
        """Saves a file, commits it, and pushes the change to the GitHub repository.
        
        Args:
            file_relative_path (str): Path of the file relative to the repo root.
            file_content (str): The content to be written to the file.
            commit_message (str): The commit message.
            
        Returns:
            str: The commit SHA.
        """
        repo = self.initialize_local_repo()
        
        # Write file content
        full_file_path = self.local_path / file_relative_path
        full_file_path.parent.mkdir(parents=True, exist_ok=True)
        full_file_path.write_text(file_content, encoding="utf-8")
        
        # Stage and commit
        repo.index.add([file_relative_path])
        commit = repo.index.commit(commit_message)
        commit_sha = commit.hexsha
        logger.info(f"Created local commit: {commit_sha} with message: {commit_message}")

        # Push with retry/rebase logic
        try:
            origin = repo.remotes.origin
            logger.info("Pushing changes to remote repository...")
            origin.push().raise_if_error()
            logger.info("Successfully pushed changes to remote.")
        except Exception as e:
            logger.warning(f"Initial push failed: {e}. Attempting to pull and rebase...")
            try:
                # Fetch first, then pull with rebase
                repo.git.pull("--rebase", "origin", "main")
                logger.info("Rebase successful. Retrying push...")
                origin.push().raise_if_error()
                logger.info("Successfully pushed changes after rebase.")
            except Exception as rebase_err:
                logger.error(f"Failed to push changes even after rebase: {rebase_err}")
                raise rebase_err

        return commit_sha
