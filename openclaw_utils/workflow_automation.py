"""
Workflow automation utilities for OpenClaw.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


def setup_git_hooks(workspace_path: Optional[Union[str, Path]] = None) -> bool:
    """
    Set up useful git hooks for OpenClaw development.
    
    Args:
        workspace_path: Path to the workspace (defaults to current workspace)
        
    Returns:
        True if hooks were set up successfully, False otherwise
    """
    if workspace_path is None:
        workspace_path = get_workspace_path()
    else:
        workspace_path = Path(workspace_path)
    
    git_dir = workspace_path / ".git"
    if not git_dir.is_dir():
        return False
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # Pre-commit hook to run tests
    pre_commit_hook = hooks_dir / "pre-commit"
    pre_commit_content = """#!/bin/bash
# OpenClaw pre-commit hook
echo "Running pre-commit checks..."

# Run basic syntax checks
if command -v python >/dev/null 2>&1; then
    echo "Checking Python syntax..."
    find . -name "*.py" -not -path "./.git/*" -exec python -m py_compile {} \\;
fi

# Run any configured linters
if command -v ruff >/dev/null 2>&1; then
    echo "Running ruff linting..."
    ruff check .
fi

if command -v black >/dev/null 2>&1; then
    echo "Checking black formatting..."
    black --check . --diff || echo "Files need formatting. Run 'black .' to fix."
fi

echo "Pre-commit checks completed."
exit 0
"""
    pre_commit_hook.write_text(pre_commit_content)
    pre_commit_hook.chmod(0o755)
    
    # Post-commit hook to update memory
    post_commit_hook = hooks_dir / "post-commit"
    post_commit_content = """#!/bin/bash
# OpenClaw post-commit hook
echo "Running post-commit actions..."

# Update commit log in memory if in OpenClaw workspace
if [ -f "AGENTS.md" ] || [ -f "SOUL.md" ]; then
    COMMIT_MSG=$(git log -1 --pretty=%B)
    COMMIT_HASH=$(git log -1 --pretty=%h)
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    
    echo "[$TIMESTAMP] Commit $COMMIT_HASH: $COMMIT_MSG" >> memory/commit-log.md 2>/dev/null || true
fi

echo "Post-commit actions completed."
exit 0
"""
    post_commit_hook.write_text(post_commit_content)
    post_commit_hook.chmod(0o755)
    
    return True


def create_daily_report(
    date_str: Optional[str] = None,
    workspace_path: Optional[Union[str, Path]] = None
) -> Path:
    """
    Create a daily report summarizing workspace activity.
    
    Args:
        date_str: Date string in YYYY-MM-DD format (defaults to today)
        workspace_path: Path to the workspace (defaults to current workspace)
        
    Returns:
        Path to the generated report file
    """
    if workspace_path is None:
        workspace_path = get_workspace_path()
    else:
        workspace_path = Path(workspace_path)
    
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    workspace_path = Path(workspace_path)
    reports_dir = workspace_path / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / f"daily-report-{date_str}.md"
    
    # Gather information for the report
    report_content = f"""# Daily Report - {date_str}

## Workspace Overview
- **Workspace**: {workspace_path}
- **Report Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## File Activity
"""
    
    # Count files by type
    try:
        all_files = list_workspace_files(recursive=True)
        file_types = {}
        for file_path in all_files:
            suffix = file_path.suffix.lower()
            if not suffix:
                suffix = "(no extension)"
            file_types[suffix] = file_types.get(suffix, 0) + 1
        
        report_content += "### File Types\n"
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            report_content += f"- {ext}: {count} files\n"
        report_content += "\n"
        
    except Exception as e:
        report_content += f"*Error gathering file statistics: {e}*\n\n"
    
    # Recent memory entries
    memory_dir = workspace_path / "memory"
    if memory_dir.exists():
        report_content += "## Recent Memory Entries\n"
        memory_files = sorted(memory_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        for mem_file in memory_files:
            try:
                content = mem_file.read_text(encoding='utf-8')
                preview = content[:200] + "..." if len(content) > 200 else content
                report_content += f"### {mem_file.stem}\n{preview}\n\n"
            except Exception:
                report_content += f"### {mem_file.stem}\n*Error reading file*\n\n"
    
    # Git status if available
    git_dir = workspace_path / ".git"
    if git_dir.exists():
        report_content += "## Git Status\n"
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=workspace_path, 
                capture_output=True, 
                text=True
            )
            if result.stdout.strip():
                report_content += "### Modified Files\n"
                for line in result.stdout.strip().split('\\n'):
                    if line.strip():
                        report_content += f"- {line}\n"
            else:
                report_content += "*Working directory clean*\n"
            
            # Recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"], 
                cwd=workspace_path, 
                capture_output=True, 
                text=True
            )
            if result.stdout.strip():
                report_content += "\n### Recent Commits\n"
                for line in result.stdout.strip().split('\\n'):
                    if line.strip():
                        report_content += f"- {line}\n"
        except Exception as e:
            report_content += f"*Error getting git status: {e}*\n"
    
    # TODO: Add more metrics as needed
    report_content += f"""## Summary
Generated daily report for {date_str}.

*This report was automatically generated by OpenClaw Utils.*
"""
    
    return safe_write(report_file, report_content)


def backup_workspace(
    backup_name: Optional[str] = None,
    workspace_path: Optional[Union[str, Path]] = None,
    backup_dir: Optional[Union[str, Path]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> Path:
    """
    Create a backup of the OpenClaw workspace.
    
    Args:
        backup_name: Name for the backup (defaults to timestamp)
        workspace_path: Path to the workspace (defaults to current workspace)
        backup_dir: Directory to store backups (defaults to workspace/backups)
        exclude_patterns: List of patterns to exclude from backup
        
    Returns:
        Path to the backup archive
    """
    if workspace_path is None:
        workspace_path = get_workspace_path()
    else:
        workspace_path = Path(workspace_path)
    
    if backup_dir is None:
        backup_dir = workspace_path / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    if backup_name is None:
        backup_name = f"workspace-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    if exclude_patterns is None:
        exclude_patterns = [
            ".git/*",
            "__pycache__/*",
            "*.pyc",
            "node_modules/*",
            ".openclaw/*",
            "backups/*",
            "reports/*",
            ".DS_Store",
            "Thumbs.db"
        ]
    
    # Create temporary directory for backup preparation
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_source = Path(temp_dir) / "workspace"
        
        # Copy workspace excluding patterns
        def _should_exclude(path: Path) -> bool:
            path_str = str(path.relative_to(workspace_path))
            for pattern in exclude_patterns:
                if path.match(pattern) or any(part.match(pattern) for part in path.relative_to(workspace_path).parts):
                    return True
            return False
        
        def _copy_workspace(src: Path, dst: Path):
            for item in src.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(src)
                    if not _should_exclude(item):
                        target = dst / rel_path
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target)
        
        _copy_workspace(workspace_path, backup_source)
        
        # Create archive
        archive_path = backup_dir / f"{backup_name}.tar.gz"
        shutil.make_archive(
            str(archive_path).replace('.tar.gz', ''),
            'gztar',
            backup_source.parent,
            backup_source.name
        )
    
    return archive_path


def restore_workspace(
    backup_archive: Union[str, Path],
    workspace_path: Optional[Union[str, Path]] = None,
    restore_dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    Restore a workspace from a backup archive.
    
    Args:
        backup_archive: Path to the backup archive (.tar.gz)
        workspace_path: Path to restore to (defaults to current workspace)
        restore_dir: Subdirectory within workspace to restore to (optional)
        
    Returns:
        Path to the restored workspace directory
    """
    if workspace_path is None:
        workspace_path = get_workspace_path()
    else:
        workspace_path = Path(workspace_path)
    
    backup_archive = Path(backup_archive)
    if not backup_archive.is_file():
        raise FileNotFoundError(f"Backup archive not found: {backup_archive}")
    
    if restore_dir is None:
        restore_path = workspace_path
    else:
        restore_path = workspace_path / restore_dir
        restore_path.mkdir(parents=True, exist_ok=True)
    
    # Extract archive
    import tarfile
    with tarfile.open(backup_archive, "r:gz") as tar:
        tar.extractall(path=restore_path)
    
    # Assuming the archive contains a 'workspace' directory at its root
    extracted_items = list(restore_path.iterdir())
    if len(extracted_items) == 1 and extracted_items[0].is_dir():
        # Move contents up one level if it's a single directory
        workspace_content = extracted_items[0]
        for item in workspace_content.iterdir():
            target = restore_path / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(item), str(restore_path))
        workspace_content.rmdir()  # Remove the now-empty directory
    
    return restore_path


def cleanup_temp_files(
    workspace_path: Optional[Union[str, Path]] = None,
    max_age_hours: int = 24,
    patterns: Optional[List[str]] = None
) -> int:
    """
    Clean up temporary files in the workspace.
    
    Args:
        workspace_path: Path to the workspace (defaults to current workspace)
        max_age_hours: Maximum age of files to keep (default: 24 hours)
        patterns: List of glob patterns to clean up (default: common temp patterns)
        
    Returns:
        Number of files removed
    """
    if workspace_path is None:
        workspace_path = get_workspace_path()
    else:
        workspace_path = Path(workspace_path)
    
    if patterns is None:
        patterns = [
            "*.tmp",
            "*.temp",
            "*~",
            ".#*",  # Emacs lock files
            "#*#",  # Emacs autosave
            "*.pyc",
            "__pycache__",
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            "*.log",
            "*.swp",
            "*.swo",
            ".DS_Store",
            "Thumbs.db"
        ]
    
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    removed_count = 0
    
    for pattern in patterns:
        for file_path in workspace_path.rglob(pattern):
            try:
                # Check if file is old enough
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    if file_path.is_file():
                        file_path.unlink()
                        removed_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        removed_count += 1
            except Exception:
                # Skip files we can't process
                continue
    
    return removed_count