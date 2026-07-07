import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DocumentationGeneratorService:
    @staticmethod
    def get_difficulty_badge_color(difficulty: str) -> str:
        """Returns the hex color code or shields.io color name for a given difficulty level."""
        diff_lower = difficulty.lower().strip()
        if diff_lower == "easy":
            return "brightgreen"
        elif diff_lower == "medium":
            return "orange"
        elif diff_lower == "hard":
            return "red"
        return "blue"

    def generate_problem_readme(
        self,
        question_id: str,
        title: str,
        slug: str,
        difficulty: str,
        topic_tags: List[Dict[str, str]],
        lang_name: str,
        code_content: str
    ) -> str:
        """Generates a beautifully structured Markdown README.md content string for a LeetCode problem.
        
        Args:
            question_id (str): LeetCode problem ID.
            title (str): Problem title.
            slug (str): Problem title slug.
            difficulty (str): Difficulty (Easy, Medium, Hard).
            topic_tags (List[Dict[str, str]]): List of topic tag dicts containing name and slug.
            lang_name (str): The language name (e.g., python3, java).
            code_content (str): Solution source code content.
            
        Returns:
            str: Markdown formatted README content.
        """
        logger.info(f"Generating README markdown content for: {title}")
        
        # Difficulty badge styling
        badge_color = self.get_difficulty_badge_color(difficulty)
        difficulty_badge = f"![Difficulty: {difficulty}](https://img.shields.io/badge/Difficulty-{difficulty}-{badge_color}?style=flat-square)"
        
        # Topics formatted as badges or bullet points
        topic_badges = []
        for tag in topic_tags:
            tag_name = tag.get("name", "")
            tag_slug = tag.get("slug", "")
            if tag_name:
                badge = f"![Topic: {tag_name}](https://img.shields.io/badge/Topic-{tag_name}-blue?style=flat-square)"
                topic_badges.append(f"[{badge}](https://leetcode.com/tag/{tag_slug}/)")
        
        topic_badges_str = " ".join(topic_badges) if topic_badges else "Algorithms"

        # Map language name for syntax block highlighting
        syntax_highlight = lang_name.lower().strip()
        if syntax_highlight in ["python3", "python"]:
            syntax_highlight = "python"
        elif syntax_highlight in ["golang"]:
            syntax_highlight = "go"

        # Create structured markdown template
        markdown = f"""# {title}

## Metadata
{difficulty_badge}
{topic_badges_str}

- **LeetCode Link**: [https://leetcode.com/problems/{slug}/](https://leetcode.com/problems/{slug}/)
- **Problem ID**: {question_id}
- **Language**: {lang_name.capitalize()}

## Solution Design

### Method Explanation
- *We solve this problem by leveraging standard data structures or algorithms suitable for the problem constraints.*
- *Make sure to update this section with notes on your implementation approaches.*

### Complexity Analysis
- **Time Complexity**: \\(O(N)\\) (where \\(N\\) is the number of elements)
- **Space Complexity**: \\(O(1)\\) auxiliary space

## Solution Code

```{syntax_highlight}
{code_content}
```
"""
        return markdown
