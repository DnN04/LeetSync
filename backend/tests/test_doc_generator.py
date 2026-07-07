import pytest
from app.services.doc_generator import DocumentationGeneratorService

def test_get_difficulty_badge_color():
    service = DocumentationGeneratorService()
    assert service.get_difficulty_badge_color("Easy") == "brightgreen"
    assert service.get_difficulty_badge_color("Medium") == "orange"
    assert service.get_difficulty_badge_color("Hard") == "red"
    assert service.get_difficulty_badge_color("Unknown") == "blue"

def test_generate_problem_readme():
    service = DocumentationGeneratorService()
    readme = service.generate_problem_readme(
        question_id="1",
        title="Two Sum",
        slug="two-sum",
        difficulty="Easy",
        topic_tags=[{"name": "Array", "slug": "array"}, {"name": "Hash Table", "slug": "hash-table"}],
        lang_name="python3",
        code_content="class Solution:\n    def twoSum(self): pass"
    )
    
    assert "# Two Sum" in readme
    assert "https://leetcode.com/problems/two-sum/" in readme
    assert "Difficulty-Easy-brightgreen" in readme
    assert "Topic-Array-blue" in readme
    assert "Topic-Hash_Table-blue" in readme or "Topic-Hash" in readme
    assert "```python" in readme
    assert "def twoSum(self): pass" in readme
    assert "Complexity Analysis" in readme
