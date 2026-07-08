import json
import logging
from collections import Counter
from datetime import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.models import SyncedSubmission

logger = logging.getLogger(__name__)

class StatisticsEngineService:
    def generate_statistics(self, db: Session) -> Tuple[Dict[str, Any], str]:
        """Compiles synchronized submission statistics and generates master README content.
        
        Args:
            db (Session): Database session context.
            
        Returns:
            Tuple[Dict[str, Any], str]: Statistics data dict and Master README Markdown string.
        """
        logger.info("Recalculating database statistics metrics...")
        
        # 1. Fetch all synced submissions
        submissions = db.query(SyncedSubmission).order_by(SyncedSubmission.solved_at.desc()).all()
        total_count = len(submissions)
        
        # 2. Compile metrics
        easy_count = 0
        medium_count = 0
        hard_count = 0
        topics = []
        recent_activity = []
        
        for sub in submissions:
            # Difficulty counts
            diff = sub.difficulty.lower().strip()
            if diff == "easy":
                easy_count += 1
            elif diff == "medium":
                medium_count += 1
            elif diff == "hard":
                hard_count += 1
                
            # Topic counts (comma separated string)
            if sub.topic_tags:
                tag_list = [t.strip() for t in sub.topic_tags.split(",") if t.strip()]
                topics.extend(tag_list)
                
            # Recent activity details (limit to latest 10)
            if len(recent_activity) < 10:
                recent_activity.append({
                    "problem_id": sub.problem_id,
                    "problem_title": sub.problem_title,
                    "difficulty": sub.difficulty,
                    "language": sub.language,
                    "solved_at": sub.solved_at.strftime("%Y-%m-%d"),
                    "file_path": sub.github_file_path or ""
                })

        topic_distribution = dict(Counter(topics).most_common())
        
        # Build Stats Dict
        stats_data = {
            "total_solved": total_count,
            "difficulty_breakdown": {
                "Easy": easy_count,
                "Medium": medium_count,
                "Hard": hard_count
            },
            "topic_distribution": topic_distribution,
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "recent_solved": recent_activity
        }
        
        readme_content = self.generate_master_readme(stats_data)
        return stats_data, readme_content

    def generate_master_readme(self, stats: dict) -> str:
        """Formats the master README.md template for the portfolio repository."""
        difficulty = stats["difficulty_breakdown"]
        
        # Build difficulty table/text
        stats_section = f"""## Portfolio Stats

| Metric | Count |
| :--- | :--- |
| **Total Solved** | **{stats["total_solved"]}** |
| 🟢 Easy | {difficulty["Easy"]} |
| 🟡 Medium | {difficulty["Medium"]} |
| 🔴 Hard | {difficulty["Hard"]} |
"""

        # Build Topics list
        topics_str = ""
        if stats["topic_distribution"]:
            topics_str = "\n## Solved by Topic\n\n"
            for topic, count in stats["topic_distribution"].items():
                topics_str += f"- **{topic}**: {count} problems\n"

        # Build Recent Activity Table
        activity_str = "\n## Recent Solved Problems\n\n"
        if stats["recent_solved"]:
            activity_str += "| # | Problem | Difficulty | Language | Solved Date | Solution |\n"
            activity_str += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            for index, item in enumerate(stats["recent_solved"], 1):
                clean_title = item["problem_title"]
                solution_link = f"[Solution](./{item['file_path']})" if item["file_path"] else "N/A"
                activity_str += f"| {item['problem_id']} | {clean_title} | {item['difficulty']} | {item['language'].capitalize()} | {item['solved_at']} | {solution_link} |\n"
        else:
            activity_str += "*No solved problems registered yet.*\n"

        # Assemble README
        readme_md = f"""# LeetCode Portfolio

Welcome to my LeetCode problem-solving portfolio! This repository is automatically updated by [LeetSync Pro](https://github.com/DnN04/LeetSync.git) every time a new accepted solution is submitted.

{stats_section}
{topics_str}
{activity_str}
---
*Last synchronization run: {stats["last_updated"]}*
"""
        return readme_md
