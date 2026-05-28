# !/usr/bin/env python3

from pathlib import Path
# === Standard Library Imports ===
import os      # Operating system interfaces
import sys     # System-specific parameters and functions
from pathlib import Path  # Object-oriented filesystem paths
from typing import List, Dict, Any, Union, Optional  # For strict type hinting



SKILLS_DIR: Path = Path(__file__).parent / "skills"
print (SKILLS_DIR)

def discover_skills() -> Dict[str, str]:
    """
    Scans the skills directory and extracts metadata from SKILL.md files.

    It parses the first non-empty line of text (ignoring YAML frontmatter) 
    to use as a brief description for the agent's index.

    Returns:
        Dict[str, str]: A dictionary mapping {skill_name: short_description}.
    """
    skills: Dict[str, str] = {}
    
    # Ensure the skills directory actually exists to avoid iteration errors
    if not SKILLS_DIR.exists():
        return skills

    # Iterate through subdirectories in alphabetical order
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        
        # We only consider directories that contain a SKILL.md file
        if skill_dir.is_dir() and skill_md.exists():
            try:
                # Read file and split into lines for parsing
                lines = skill_md.read_text(encoding="utf-8").splitlines()
                description = "No description available."
                in_frontmatter = False
                
                # Logic to find the first relevant line of descriptive text
                for line in lines:
                    stripped = line.strip()
                    # Toggle frontmatter state (skipping YAML headers)
                    if stripped == "---":
                        in_frontmatter = not in_frontmatter
                        continue
                    
                    # # Ignore empty lines, headers (#), and frontmatter content
                    # if not in_frontmatter and stripped and not stripped.startswith("#"):
                    #     description = stripped[:100]  # Cap length for prompt brevity
                    #     break
                    if in_frontmatter and stripped.startswith("description:"):
                        description = stripped[len("description:"):].strip()[:80]
                        break
                
                skills[skill_dir.name] = description
            except Exception as e:
                # Log error and continue to the next skill
                skills[skill_dir.name] = f"Error reading metadata: {e}"
                
    return skills
skills_discover = discover_skills()
print (skills_discover)


def run_list_skills() -> str:
    """
    Formats the list of discovered skills for the agent's tool output.

    Returns:
        str: A formatted string list of available skills.
    """
    skills = discover_skills()
    if not skills:
        return "(no skills found in skills/ directory)"
    
    # Format as a bulleted list for the LLM's consumption
    return "\n".join(f"  - {name}: {desc}" for name, desc in skills.items())


def run_load_skill(name: str) -> str:
    """
    Loads the full content of a specific skill file into the context.

    Args:
        name (str): The folder name of the skill to load.

    Returns:
        str: The full text content of the skill, or an error message.
    """
    # Sanitize and build the path to the skill file
    skill_path = SKILLS_DIR / name / "SKILL.md"
    
    # Check for existence and potential directory traversal attempts
    if not skill_path.exists():
        return f"Error: skill '{name}' not found. Use list_skills to see valid names."
    
    try:
        # Load the full documentation
        content = skill_path.read_text(encoding="utf-8")
        return f"=== SKILL: {name} ===\n\n{content}\n\n=== END SKILL ==="
    except Exception as e:
        return f"Error loading skill '{name}': {e}"
load_skill = run_load_skill("agent-builder")
print (load_skill)

_initial_skills: Dict[str, str] = discover_skills()
_skill_index_str: str = "\n".join(
    f"  - {n}: {d}" for n, d in _initial_skills.items()
) or "  (none currently installed)"

print (_skill_index_str)


SKILLS_DIR=Path('/home/yogender/Desktop/AI-training/harnessEngineering/claude-code-from-scratch/skills')


history = [{"role": "user", "content": 

    "I want to build a simple Python web scraper. "

    "Create a task graph for this project with dependencies: "

    "1) Research which libraries to use (no dependencies) "

    "2) Write the scraper code (depends on task 1) "

    "3) Write tests (depends on task 2) "

    "4) Write documentation (depends on task 2) "

    "5) Then execute all the tasks one by one following the dependency order"

     "6) for each task mark it in_progress, do the work and mark it as done with result"

}]


history.append({"role": "user", "content": 

"In your previous run, 1. find put why you did not update .agent_todo.json file"
"2. Then update the json file for previous tasks"
"do not guess anything. You have access to full hitory of what you did"

})