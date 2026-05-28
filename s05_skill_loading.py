   1	#!/usr/bin/env python3
   2	"""
   3	s05_skill_loading.py: Implementation of On-Demand Knowledge Retrieval.
   4	
   5	Motto: "Load knowledge when you need it, not upfront"
   6	
   7	This module introduces a 'Meta-Tooling' approach to solve the "Context Window 
   8	Bloat" problem. Instead of stuffing every possible instruction, guideline, 
   9	or specialized SOP (Standard Operating Procedure) into the System Prompt, 
  10	this script allows the agent to 'discover' and 'load' specific skills 
  11	as needed.
  12	
  13	Key Architectural Concepts:
  14	    1. Discovery: The agent is given a lightweight index of available skills 
  15	       (Names and 1-line descriptions) in its system prompt.
  16	    2. Lazy Loading: The full documentation for a skill is only injected 
  17	       into the conversation when the agent explicitly calls `load_skill`.
  18	    3. Context Efficiency: This allows the agent to have access to hundreds 
  19	       of specialized skills without exceeding token limits or confusing the 
  20	       model with irrelevant data.
  21	
  22	Skill Structure:
  23	    Skills are stored in: skills/<skill_name>/SKILL.md
  24	"""
  25	
  26	# === Standard Library Imports ===
  27	import os      # Operating system interfaces
  28	import sys     # System-specific parameters and functions
  29	from pathlib import Path  # Object-oriented filesystem paths
  30	from typing import List, Dict, Any, Union, Optional  # For strict type hinting
  31	
  32	# === Local Module Imports ===
  33	from core import (
  34	    EXTENDED_TOOLS,      # Standard file/shell tools (bash, read, etc.)
  35	    EXTENDED_DISPATCH,   # Mapping for standard tools
  36	    stream_loop          # The core autonomous loop logic
  37	)
  38	
  39	# === Configuration and Constants ===
  40	
  41	# Define the absolute path to the 'skills' repository directory.
  42	# This assumes the directory structure: project_root/skills/
  43	SKILLS_DIR: Path = Path(__file__).parent / "skills"
  44	
  45	# === Skill Discovery Logic ===
  46	
  47	def discover_skills() -> Dict[str, str]:
  48	    """
  49	    Scans the skills directory and extracts metadata from SKILL.md files.
  50	
  51	    It parses the first non-empty line of text (ignoring YAML frontmatter) 
  52	    to use as a brief description for the agent's index.
  53	
  54	    Returns:
  55	        Dict[str, str]: A dictionary mapping {skill_name: short_description}.
  56	    """
  57	    skills: Dict[str, str] = {}
  58	    
  59	    if not SKILLS_DIR.exists():
  60	        return skills
  61	
  62	    for skill_dir in sorted(SKILLS_DIR.iterdir()):
  63	        skill_md = skill_dir / "SKILL.md"
  64	        
  65	        if skill_dir.is_dir() and skill_md.exists():
  66	            try:
  67	                lines = skill_md.read_text(encoding="utf-8").splitlines()
  68	                description = "No description available."
  69	                in_frontmatter = False
  70	                
  71	                for line in lines:
  72	                    stripped = line.strip()
  73	                    if stripped == "---":
  74	                        in_frontmatter = not in_frontmatter
  75	                        continue
  76	                    if in_frontmatter and stripped.startswith("description:"):
  77	                        description = stripped[len("description:"):].strip()[:80]
  78	                        break
  79	                
  80	                skills[skill_dir.name] = description
  81	            except Exception as e:
  82	                skills[skill_dir.name] = f"Error reading metadata: {e}"
  83	                
  84	    return skills
  85	
  86	
  87	def run_list_skills() -> str:
  88	    """
  89	    Formats the list of discovered skills for the agent's tool output.
  90	
  91	    Returns:
  92	        str: A formatted string list of available skills.
  93	    """
  94	    skills = discover_skills()
  95	    if not skills:
  96	        return "(no skills found in skills/ directory)"
  97	    
  98	    return "\n".join(f"  - {name}: {desc}" for name, desc in skills.items())
  99	
 100	
 101	def run_load_skill(name: str) -> str:
 102	    """
 103	    Loads the full content of a specific skill file into the context.
 104	
 105	    Args:
 106	        name (str): The folder name of the skill to load.
 107	
 108	    Returns:
 109	        str: The full text content of the skill, or an error message.
 110	    """
 111	    skill_path = SKILLS_DIR / name / "SKILL.md"
 112	    
 113	    if not skill_path.exists():
 114	        return f"Error: skill '{name}' not found. Use list_skills to see valid names."
 115	    
 116	    try:
 117	        content = skill_path.read_text(encoding="utf-8")
 118	        return f"=== SKILL: {name} ===\n\n{content}\n\n=== END SKILL ==="
 119	    except Exception as e:
 120	        return f"Error loading skill '{name}': {e}"
 121	
 122	
 123	# === Dynamic System Prompt Construction ===
 124	
 125	_initial_skills: Dict[str, str] = discover_skills()
 126	_skill_index_str: str = "\n".join(
 127	    f"  - {n}: {d}" for n, d in _initial_skills.items()
 128	) or "  (none currently installed)"
 129	
 130	SYSTEM: str = (
 131	    f"You are a coding agent at {os.getcwd()}.\n"
 132	    "You have access to specialized 'Skills' (domain knowledge files). "
 133	    "ALWAYS call load_skill(name) BEFORE starting ANY code task. "
 134	    "NEVER fix code without loading the relevant skill first. "
 135	    "Do NOT guess or hallucinate details if a skill is available.\n\n"
 136	    f"Available Skills Index:\n{_skill_index_str}"
 137	)
 138	
 139	# === Tool Schema and Dispatch Extensions ===
 140	
 141	SKILL_TOOLS: List[Dict[str, Any]] = EXTENDED_TOOLS + [
 142	    {
 143	        "name": "list_skills",
 144	        "description": "List all available specialized skills with their descriptions.",
 145	        "input_schema": {"type": "object", "properties": {}},
 146	    },
 147	    {
 148	        "name": "load_skill",
 149	        "description": (
 150	            "Load the full instructions for a skill into your context. "
 151	            "Use this before starting a task requiring specialized domain knowledge."
 152	        ),
 153	        "input_schema": {
 154	            "type": "object",
 155	            "properties": {
 156	                "name": {
 157	                    "type": "string",
 158	                    "description": "The exact name of the skill folder to load."
 159	                }
 160	            },
 161	            "required": ["name"],
 162	        },
 163	    },
 164	]
 165	
 166	SKILL_DISPATCH: Dict[str, Any] = {
 167	    **EXTENDED_DISPATCH,
 168	    "list_skills": lambda inp: run_list_skills(),
 169	    "load_skill":  lambda inp: run_load_skill(inp["name"]),
 170	}
 171	
 172	
 173	# === Main Execution Block ===
 174	
 175	def main() -> None:
 176	    """
 177	    Initializes the terminal interaction for the s05 'Skill Loading' agent.
 178	    """
 179	    print("\033[90ms05: on-demand skill loading | list_skills · load_skill\033[0m\n")
 180	    
 181	    history: List[Dict[str, Any]] = []
 182	
 183	    while True:
 184	        try:
 185	            query: str = input("\033[36ms05 >> \033[0m").strip()
 186	        except (EOFError, KeyboardInterrupt):
 187	            print("\nExiting session.")
 188	            sys.exit(0)
 189	
 190	        if not query or query.lower() in ("q", "exit", "quit"):
 191	            break
 192	
 193	        history.append({"role": "user", "content": query})
 194	        
 195	        stream_loop(
 196	            messages=history,
 197	            tools=SKILL_TOOLS,
 198	            dispatch=SKILL_DISPATCH,
 199	            system=SYSTEM
 200	        )
 201	        
 202	        print()
 203	
 204	
 205	if __name__ == "__main__":
 206	    main()