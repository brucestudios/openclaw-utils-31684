"""
OpenClaw-specific helper functions for common operations.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union


def get_workspace_path() -> Path:
    """
    Get the current OpenClaw workspace path.
    
    Returns:
        Path object pointing to the workspace root
    """
    # Check common environment variables that might indicate workspace
    workspace_env = os.getenv("OPENCLAW_WORKSPACE")
    if workspace_env:
        return Path(workspace_env)
    
    # Check if we're in a typical OpenClaw workspace structure
    current = Path.cwd()
    
    # Look for AGENTS.md or SOUL.md which are typical workspace markers
    for parent in [current] + list(current.parents):
        if (parent / "AGENTS.md").exists() or (parent / "SOUL.md").exists():
            return parent
    
    # Fallback to current directory
    return current


def read_agent_context() -> Dict[str, Any]:
    """
    Read common agent context files (AGENTS.md, SOUL.md, IDENTITY.md, USER.md, TOOLS.md).
    
    Returns:
        Dictionary containing the contents of found context files
    """
    workspace = get_workspace_path()
    context_files = ["AGENTS.md", "SOUL.md", "IDENTITY.md", "USER.md", "TOOLS.md"]
    context = {}
    
    for filename in context_files:
        file_path = workspace / filename
        if file_path.is_file():
            try:
                context[filename.lower().replace('.md', '')] = file_path.read_text(encoding='utf-8')
            except Exception as e:
                context[filename.lower().replace('.md', '')] = f"Error reading file: {e}"
    
    return context


def generate_skill_template(skill_name: str, description: str, output_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Generate a new skill template directory structure.
    
    Args:
        skill_name: Name of the skill to create
        description: Description of what the skill does
        output_dir: Directory to create the skill in (defaults to workspace/skills)
        
    Returns:
        Path to the created skill directory
    """
    if output_dir is None:
        workspace = get_workspace_path()
        output_dir = workspace / "skills"
    else:
        output_dir = Path(output_dir)
    
    skill_dir = output_dir / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    # Create SKILL.md
    skill_md_content = f"""# {skill_name.replace('-', ' ').title()} Skill

{description}

## When to Use This Skill

Use this skill when you need to:
- Perform specific operations related to {skill_name}
- Automate repetitive tasks in OpenClaw
- Integrate with external systems or APIs

## Available Tools

This skill provides the following tools:
- [Tool 1]: Description of what this tool does
- [Tool 2]: Description of what this tool does

## Usage Examples

Example 1: Basic usage
```python
# Example code here
```

Example 2: Advanced usage
```python
# Example code here
```

## Installation

This skill is designed to be used within the OpenClaw framework. No additional installation steps are required.

## Configuration

List any configuration options or environment variables this skill might use.

## Contributing

Feel free to submit issues or pull requests to improve this skill.

## License

This skill is part of the OpenClaw Utils package and follows its licensing terms.
"""
    
    (skill_dir / "SKILL.md").write_text(skill_md_content, encoding='utf-8')
    
    # Create __init__.py
    init_content = f"""\"\"\"
{skill_name.replace('-', ' ').title()} Skill for OpenClaw
\"\"\"

# Skill implementation goes here
# Export any tools or functions that should be available to agents

__all__ = [
    # Add exported functions/tools here
]
"""
    
    (skill_dir / "__init__.py").write_text(init_content, encoding='utf-8')
    
    # Create references directory
    (skill_dir / "references").mkdir(exist_ok=True)
    
    # Create scripts directory
    (skill_dir / "scripts").mkdir(exist_ok=True)
    
    return skill_dir


def generate_agent_template(agent_name: str, description: str, output_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Generate a new agent template directory structure.
    
    Args:
        agent_name: Name of the agent to create
        description: Description of what the agent does
        output_dir: Directory to create the agent in (defaults to workspace/agents)
        
    Returns:
        Path to the created agent directory
    """
    if output_dir is None:
        workspace = get_workspace_path()
        output_dir = workspace / "agents"
    else:
        output_dir = Path(output_dir)
    
    agent_dir = output_dir / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    # Create agent configuration
    agent_config = {
        "name": agent_name,
        "description": description,
        "version": "0.1.0",
        "author": "OpenClaw Agent",
        "skills": [],
        "tools": [],
        "config": {}
    }
    
    (agent_dir / "agent.json").write_text(json.dumps(agent_config, indent=2), encoding='utf-8')
    
    # Create README
    readme_content = f"""# {agent_name.replace('-', ' ').title()} Agent

{description}

## Overview

This agent is designed to {description.lower()}.

## Skills

List of skills this agent uses:
- Skill 1: Description
- Skill 2: Description

## Configuration

Configuration options for this agent:
- `option1`: Description
- `option2`: Description

## Usage

How to use this agent in OpenClaw:
```python
# Example usage
```

## Development

Instructions for developing and extending this agent.
"""
    
    (agent_dir / "README.md").write_text(readme_content, encoding='utf-8')
    
    return agent_dir


def list_workspace_files(
    pattern: str = "*", 
    recursive: bool = True,
    exclude_dirs: Optional[List[str]] = None,
    exclude_files: Optional[List[str]] = None
) -> List[Path]:
    """
    List files in the OpenClaw workspace.
    
    Args:
        pattern: Glob pattern to match (default: "*")
        recursive: Whether to search recursively (default: True)
        exclude_dirs: List of directory names to exclude
        exclude_files: List of file names to exclude
        
    Returns:
        List of Path objects matching the criteria
    """
    workspace = get_workspace_path()
    
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", "node_modules", ".openclaw"]
    
    if exclude_files is None:
        exclude_files = [".DS_Store", "Thumbs.db"]
    
    return find_files(workspace, pattern, recursive, exclude_dirs)


def read_memory_file(date_str: Optional[str] = None) -> Optional[str]:
    """
    Read a memory file from the workspace memory directory.
    
    Args:
        date_str: Date string in YYYY-MM-DD format (defaults to today)
        
    Returns:
        Contents of the memory file, or None if not found
    """
    workspace = get_workspace_path()
    memory_dir = workspace / "memory"
    
    if date_str is None:
        from datetime import date
        date_str = date.today().isoformat()
    
    memory_file = memory_dir / f"{date_str}.md"
    
    if memory_file.is_file():
        return memory_file.read_text(encoding='utf-8')
    
    return None


def write_memory_file(content: str, date_str: Optional[str] = None) -> Path:
    """
    Write content to a memory file in the workspace memory directory.
    
    Args:
        content: Content to write to the memory file
        date_str: Date string in YYYY-MM-DD format (defaults to today)
        
    Returns:
        Path to the written memory file
    """
    workspace = get_workspace_path()
    memory_dir = workspace / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    if date_str is None:
        from datetime import date
        date_str = date.today().isoformat()
    
    memory_file = memory_dir / f"{date_str}.md"
    return safe_write(memory_file, content)


def safe_write(
    file_path: Union[str, Path], 
    content: Union[str, bytes], 
    encoding: str = "utf-8",
    backup: bool = True
) -> Path:
    """
    Safely write content to a file (imported from file_utils for convenience).
    
    Args:
        file_path: Path to the file to write
        content: Content to write (string or bytes)
        encoding: Encoding to use for string content (default: utf-8)
        backup: Whether to create a backup if file exists (default: True)
        
    Returns:
        Path to the written file
    """
    # Import here to avoid circular imports
    from .file_utils import safe_write as _safe_write
    return _safe_write(file_path, content, encoding, backup)