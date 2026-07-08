import logging
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.models import SyncedSubmission, SyncJob, SyncLog
from app.integrations.github import GitHubIntegration
from app.integrations.leetcode import LeetCodeIntegration
from app.services.doc_generator import DocumentationGeneratorService
from app.services.stats_engine import StatisticsEngineService

logger = logging.getLogger(__name__)

# Map LeetCode language names to standard extensions
LANGUAGE_EXTENSIONS = {
    "cpp": "cpp",
    "java": "java",
    "python": "py",
    "python3": "py",
    "c": "c",
    "csharp": "cs",
    "javascript": "js",
    "typescript": "ts",
    "ruby": "rb",
    "swift": "swift",
    "golang": "go",
    "go": "go",
    "kotlin": "kt",
    "rust": "rs",
    "php": "php",
    "scala": "scala",
    "html": "html",
    "erlang": "erl",
    "elixir": "ex",
    "racket": "rkt"
}

class SyncEngineService:
    def __init__(self, github_client: Optional[GitHubIntegration] = None, leetcode_client: Optional[LeetCodeIntegration] = None, doc_generator: Optional[DocumentationGeneratorService] = None, stats_engine: Optional[StatisticsEngineService] = None):
        self.github_client = github_client or GitHubIntegration()
        self.leetcode_client = leetcode_client or LeetCodeIntegration()
        self.doc_generator = doc_generator or DocumentationGeneratorService()
        self.stats_engine = stats_engine or StatisticsEngineService()

    def get_extension(self, lang_name: str) -> str:
        """Translates a programming language name to its file extension."""
        clean_lang = lang_name.lower().strip()
        return LANGUAGE_EXTENSIONS.get(clean_lang, "txt")

    def format_title_slug(self, question_id: str, title_slug: str) -> str:
        """Formats the folder directory name, e.g., '0001_Two_Sum'."""
        # Left pad question ID to 4 characters
        padded_id = question_id.zfill(4)
        # Convert dashes to underscores and capitalize title slug segments
        words = [word.capitalize() for word in title_slug.split("-")]
        capitalized_slug = "_".join(words)
        return f"{padded_id}_{capitalized_slug}"

    def get_primary_topic(self, topic_tags: List[Dict[str, str]]) -> str:
        """Extracts primary category topic, defaulting to 'Algorithms'."""
        if not topic_tags:
            return "Algorithms"
        # Pluralize topic name for directory cleanliness (e.g. Array -> Arrays)
        primary = topic_tags[0].get("name", "Algorithms")
        if primary.lower() in ["array", "string", "hash table", "tree", "matrix", "graph", "heap"]:
            if not primary.endswith("s") and not primary.endswith("table"):
                return f"{primary}s"
        return primary.replace(" ", "_")

    def run_sync(self, db: Session) -> SyncJob:
        """Executes a full synchronization cycle.
        
        Args:
            db (Session): Database session context.
            
        Returns:
            SyncJob: The completed or failed SyncJob metadata.
        """
        start_time = datetime.utcnow()
        logger.info("Initializing LeetSync Pro Synchronization Job...")
        
        # 1. Create and save SyncJob model
        job = SyncJob(start_time=start_time, status="RUNNING")
        db.add(job)
        db.commit()
        db.refresh(job)
        
        try:
            # 2. Check credentials
            if not self.leetcode_client.validate_session():
                raise ValueError("LeetCode authentication session validation failed. Check session cookies.")
            if not self.github_client.validate_credentials():
                raise ValueError("GitHub credentials validation failed. Check API tokens.")
            
            # 3. Initialize/verify local repository structure
            self.github_client.initialize_local_repo()
            
            # 4. Fetch recent accepted submissions
            recent_subs = self.leetcode_client.get_recent_accepted_submissions()
            if not recent_subs:
                logger.info("No recent submissions found or all recent submissions are non-Accepted.")
                self._complete_job(db, job, start_time)
                return job
                
            # Filter duplicates by checking SQLite db
            synced_submission_ids = {
                sub.leetcode_submission_id for sub in db.query(SyncedSubmission.leetcode_submission_id).all()
            }
            
            new_submissions_to_sync = [
                sub for sub in recent_subs if str(sub["id"]) not in synced_submission_ids
            ]
            
            if not new_submissions_to_sync:
                logger.info("All fetched submissions have already been synchronized.")
                self._complete_job(db, job, start_time)
                return job
                
            logger.info(f"Identified {len(new_submissions_to_sync)} new accepted submissions to synchronize.")
            
            # 5. Process and synchronize each submission (oldest first to maintain commit history sequence)
            new_submissions_to_sync.reverse()
            for sub in new_submissions_to_sync:
                sub_id = str(sub["id"])
                logger.info(f"Retrieving details for submission ID: {sub_id} ({sub['title']})...")
                
                details = self.leetcode_client.get_submission_details(sub_id)
                if not details:
                    logger.warning(f"Skipping submission {sub_id} because details could not be retrieved.")
                    continue
                
                # Extract details
                code_content = details["code"]
                question = details["question"]
                q_id = question["questionId"]
                q_title = question["title"]
                q_slug = question["titleSlug"]
                difficulty = question["difficulty"]
                topic_tags = question.get("topicTags", [])
                
                # Formulate structural variables
                ext = self.get_extension(details["lang"]["name"])
                folder_name = self.format_title_slug(q_id, q_slug)
                primary_topic = self.get_primary_topic(topic_tags)
                
                # File path: leetcode/{Difficulty}/{Topic}/{FolderName}/solution.{ext}
                file_rel_path = f"leetcode/{difficulty}/{primary_topic}/{folder_name}/solution.{ext}"
                readme_rel_path = f"leetcode/{difficulty}/{primary_topic}/{folder_name}/README.md"
                
                # Commit Message: Solved #1 Two Sum (Python3)
                lang_display = details["lang"]["verboseName"]
                commit_msg = f"Solved #{q_id} {q_title} ({lang_display})"
                
                # Generate individual README.md content using Doc Generator Service
                readme_content = self.doc_generator.generate_problem_readme(
                    question_id=q_id,
                    title=q_title,
                    slug=q_slug,
                    difficulty=difficulty,
                    topic_tags=topic_tags,
                    lang_name=details["lang"]["name"],
                    code_content=code_content
                )
                
                # Commit solution & README files to Git
                # In order to commit multiple files, we first write README then write the solution (committing and pushing them)
                # First write README locally
                self.github_client.commit_and_push(readme_rel_path, readme_content, f"docs: Add description for #{q_id} {q_title}")
                commit_sha = self.github_client.commit_and_push(file_rel_path, code_content, commit_msg)
                
                # Save submission record in database
                topic_names = [t["name"] for t in topic_tags]
                synced_record = SyncedSubmission(
                    leetcode_submission_id=sub_id,
                    problem_id=q_id,
                    problem_title=q_title,
                    difficulty=difficulty,
                    language=details["lang"]["name"],
                    topic_tags=",".join(topic_names),
                    solved_at=datetime.utcfromtimestamp(int(details["timestamp"])),
                    github_commit_sha=commit_sha,
                    github_file_path=file_rel_path,
                    synced_at=datetime.utcnow()
                )
                db.add(synced_record)
                db.commit()
                
            # 6. Rebuild Statistics and commit/push statistics.json and master README.md
            logger.info("Rebuilding repository statistics files...")
            stats_dict, master_readme_content = self.stats_engine.generate_statistics(db)
            
            # Commit stats json and root readme
            self.github_client.commit_and_push("statistics.json", json.dumps(stats_dict, indent=2), "stats: Update portfolio statistics")
            self.github_client.commit_and_push("README.md", master_readme_content, "docs: Update master solved summary README")
            
            self._complete_job(db, job, start_time)
            
        except Exception as e:
            logger.error(f"Sync Engine execution failed: {str(e)}")
            self._fail_job(db, job, str(e), start_time)
            
        return job

    def _complete_job(self, db: Session, job: SyncJob, start_time: datetime):
        end_time = datetime.utcnow()
        job.status = "COMPLETED"
        job.end_time = end_time
        job.execution_time_seconds = (end_time - start_time).total_seconds()
        db.commit()
        
        # Log event
        log = SyncLog(
            level="INFO",
            message=f"Sync job #{job.id} completed successfully in {job.execution_time_seconds:.2f} seconds."
        )
        db.add(log)
        db.commit()

    def _fail_job(self, db: Session, job: SyncJob, error_msg: str, start_time: datetime):
        end_time = datetime.utcnow()
        job.status = "FAILED"
        job.end_time = end_time
        job.execution_time_seconds = (end_time - start_time).total_seconds()
        job.error_message = error_msg
        db.commit()
        
        # Save structured log
        log = SyncLog(
            level="ERROR",
            message=f"Sync job #{job.id} failed: {error_msg}",
            error_code="SYNC_ENGINE_EXECUTION_FAILURE",
            recovery_suggestion="Verify GitHub and LeetCode credentials and ensure local repository directory is writable."
        )
        db.add(log)
        db.commit()
