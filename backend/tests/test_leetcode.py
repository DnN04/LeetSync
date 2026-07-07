from unittest.mock import MagicMock, patch
import pytest
import httpx
from app.integrations.leetcode import LeetCodeIntegration

def test_validate_session_success():
    integration = LeetCodeIntegration(session_cookie="test_cookie", csrf_token="test_csrf")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "userStatus": {
                "username": "coder123",
                "isSignedIn": True
            }
        }
    }
    
    with patch("httpx.Client.post", return_value=mock_response) as mock_post:
        assert integration.validate_session() is True
        assert "Cookie" in integration.headers
        assert "LEETCODE_SESSION=test_cookie" in integration.headers["Cookie"]

def test_validate_session_failure():
    integration = LeetCodeIntegration(session_cookie="invalid_cookie")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "userStatus": {
                "username": "",
                "isSignedIn": False
            }
        }
    }
    
    with patch("httpx.Client.post", return_value=mock_response):
        assert integration.validate_session() is False

def test_get_recent_accepted_submissions():
    integration = LeetCodeIntegration(session_cookie="cookie")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "submissionList": {
                "hasNext": True,
                "submissions": [
                    {"id": "1", "title": "Two Sum", "statusDisplay": "Accepted", "lang": "python3"},
                    {"id": "2", "title": "Add Two Numbers", "statusDisplay": "Wrong Answer", "lang": "python3"},
                    {"id": "3", "title": "Reverse Integer", "statusDisplay": "Accepted", "lang": "java"}
                ]
            }
        }
    }
    
    with patch("httpx.Client.post", return_value=mock_response):
        accepted = integration.get_recent_accepted_submissions(limit=5)
        assert len(accepted) == 2
        assert accepted[0]["id"] == "1"
        assert accepted[1]["id"] == "3"

def test_get_submission_details():
    integration = LeetCodeIntegration(session_cookie="cookie")
    
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "submissionDetails": {
                "code": "class Solution:\n    def twoSum(self): pass",
                "timestamp": 1609459200,
                "lang": {"name": "python3", "verboseName": "Python3"},
                "question": {
                    "questionId": "1",
                    "title": "Two Sum",
                    "titleSlug": "two-sum",
                    "difficulty": "Easy",
                    "topicTags": [{"name": "Array", "slug": "array"}]
                }
            }
        }
    }
    
    with patch("httpx.Client.post", return_value=mock_response):
        details = integration.get_submission_details("12345")
        assert details is not None
        assert details["code"] == "class Solution:\n    def twoSum(self): pass"
        assert details["question"]["difficulty"] == "Easy"
        assert details["question"]["topicTags"][0]["name"] == "Array"
