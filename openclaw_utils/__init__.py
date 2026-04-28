"""
OpenClaw Utils Package
"""

from .file_utils import (
    ensure_dir,
    backup_file,
    find_files,
    safe_write,
    read_json,
    write_json,
    copy_file,
    move_file,
    delete_file,
    get_file_size,
    get_file_hash
)

from .openclaw_helpers import (
    get_workspace_path,
    read_agent_context,
    generate_skill_template,
    generate_agent_template,
    list_workspace_files,
    read_memory_file,
    write_memory_file
)

from .workflow_automation import (
    setup_git_hooks,
    create_daily_report,
    backup_workspace,
    restore_workspace,
    cleanup_temp_files
)

__version__ = "0.1.0"
__author__ = "OpenClaw Agent"
__email__ = "agent@openclaw.dev"

__all__ = [
    # File utilities
    "ensure_dir",
    "backup_file", 
    "find_files",
    "safe_write",
    "read_json",
    "write_json",
    "copy_file",
    "move_file",
    "delete_file",
    "get_file_size",
    "get_file_hash",
    
    # OpenClaw helpers
    "get_workspace_path",
    "read_agent_context",
    "generate_skill_template",
    "generate_agent_template",
    "list_workspace_files",
    "read_memory_file",
    "write_memory_file",
    
    # Workflow automation
    "setup_git_hooks",
    "create_daily_report",
    "backup_workspace",
    "restore_workspace",
    "cleanup_temp_files"
]