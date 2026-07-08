import logging
from typing import Optional, List, Dict, Any
import httpx
from app.config.settings import settings

logger = logging.getLogger(__name__)

class LeetCodeIntegration:
    GRAPHQL_URL = "https://leetcode.com/graphql"

    def __init__(self, session_cookie: Optional[str] = None, csrf_token: Optional[str] = None):
        self.session_cookie = session_cookie or settings.leetcode_session
        self.csrf_token = csrf_token or settings.leetcode_csrf_token
        
        # Build headers
        self.headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        if self.session_cookie and not self.csrf_token:
            self._auto_fetch_csrf()
            
        self._build_cookies()

    def _auto_fetch_csrf(self):
        try:
            logger.info("LeetCode CSRF Token not configured. Attempting to fetch automatically from LeetCode home page...")
            with httpx.Client() as client:
                resp = client.get(
                    "https://leetcode.com/",
                    headers={
                        "Cookie": f"LEETCODE_SESSION={self.session_cookie}",
                        "User-Agent": self.headers["User-Agent"]
                    },
                    timeout=10.0
                )
                csrf = resp.cookies.get("csrftoken")
                if csrf:
                    self.csrf_token = csrf
                    logger.info("Successfully fetched CSRF token from cookies.")
                else:
                    logger.warning("CSRF token cookie ('csrftoken') was not found in response cookies.")
        except Exception as e:
            logger.error(f"Failed to automatically retrieve LeetCode CSRF token: {e}")

    def _build_cookies(self):
        cookies = []
        if self.session_cookie:
            cookies.append(f"LEETCODE_SESSION={self.session_cookie}")
        if self.csrf_token:
            cookies.append(f"csrftoken={self.csrf_token}")
            self.headers["X-CSRFToken"] = self.csrf_token
            
        if cookies:
            self.headers["Cookie"] = "; ".join(cookies)

    def validate_session(self) -> bool:
        """Validates if the provided LeetCode session cookie is authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise.
        """
        if not self.session_cookie:
            logger.error("LeetCode Session Cookie is not configured.")
            return False

        query = """
        query globalCurrentUserData {
            userStatus {
                username
                isSignedIn
            }
        }
        """
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.GRAPHQL_URL,
                    json={"query": query},
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    errors = data.get("errors")
                    if errors:
                        logger.error(f"GraphQL returned errors: {errors}")
                        return False
                    
                    user_status = data.get("data", {}).get("userStatus", {})
                    is_signed_in = user_status.get("isSignedIn", False)
                    username = user_status.get("username", "")
                    
                    if is_signed_in:
                        logger.info(f"Successfully authenticated LeetCode session for user: {username}")
                        return True
                    else:
                        logger.error("LeetCode session is not signed in (isSignedIn is False).")
                        return False
                else:
                    logger.error(f"LeetCode session validation failed with HTTP status: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Error checking LeetCode session: {str(e)}")
            return False

    def get_recent_accepted_submissions(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieves a list of recent accepted submissions from the authenticated user.
        
        Args:
            limit (int): The maximum number of submissions to fetch.
            
        Returns:
            List[Dict[str, Any]]: List of accepted submissions.
        """
        query = """
        query submissionList($offset: Int!, $limit: Int!, $lastKey: String) {
            submissionList(offset: $offset, limit: $limit, lastKey: $lastKey) {
                hasNext
                submissions {
                    id
                    title
                    titleSlug
                    statusDisplay
                    lang
                    timestamp
                }
            }
        }
        """
        variables = {
            "offset": 0,
            "limit": limit
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.GRAPHQL_URL,
                    json={"query": query, "variables": variables},
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    submissions = data.get("data", {}).get("submissionList", {}).get("submissions", [])
                    accepted_submissions = [
                        sub for sub in submissions if sub.get("statusDisplay") == "Accepted"
                    ]
                    logger.info(f"Fetched {len(submissions)} recent submissions. Found {len(accepted_submissions)} Accepted submissions.")
                    return accepted_submissions
                else:
                    logger.error(f"Failed to fetch recent submissions. HTTP Status: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Error querying submission list: {str(e)}")
            return []

    def get_submission_details(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full metadata and source code for a specific LeetCode submission.
        
        Args:
            submission_id (str): The ID of the submission to fetch.
            
        Returns:
            Optional[Dict[str, Any]]: Detailed metadata dictionary, or None if error.
        """
        query = """
        query submissionDetails($submissionId: Int!) {
            submissionDetails(submissionId: $submissionId) {
                code
                timestamp
                lang {
                    name
                    verboseName
                }
                question {
                    questionId
                    title
                    titleSlug
                    difficulty
                    topicTags {
                        name
                        slug
                    }
                }
            }
        }
        """
        # Submission ID is passed as integer to GraphQL
        variables = {
            "submissionId": int(submission_id)
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.GRAPHQL_URL,
                    json={"query": query, "variables": variables},
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    details = data.get("data", {}).get("submissionDetails")
                    if details:
                        logger.info(f"Successfully retrieved details for submission: {submission_id}")
                        return details
                    else:
                        logger.error(f"No submission details returned for ID: {submission_id}. Errors: {data.get('errors')}")
                        return None
                else:
                    logger.error(f"Failed to fetch submission details. HTTP Status: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error querying submission details for ID {submission_id}: {str(e)}")
            return None
