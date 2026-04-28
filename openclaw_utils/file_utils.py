"""
File system utilities for OpenClaw workspace management.
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from typing import List, Union, Optional, Dict, Any


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure
        
    Returns:
        Path object of the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def backup_file(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Create a backup of a file with timestamp in filename.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory to store backup (defaults to same directory as file)
        
    Returns:
        Path to the backup file
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if backup_dir is None:
        backup_dir = file_path.parent
    else:
        backup_dir = Path(backup_dir)
        ensure_dir(backup_dir)
    
    timestamp = file_path.stat().st_mtime
    backup_name = f"{file_path.name}.{timestamp}.bak"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def find_files(
    directory: Union[str, Path], 
    pattern: str = "*", 
    recursive: bool = True,
    exclude_dirs: Optional[List[str]] = None
) -> List[Path]:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match (default: "*")
        recursive: Whether to search recursively (default: True)
        exclude_dirs: List of directory names to exclude from search
        
    Returns:
        List of Path objects matching the pattern
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Directory not found: {directory}")
    
    if recursive:
        files = directory.rglob(pattern)
    else:
        files = directory.glob(pattern)
    
    if exclude_dirs is None:
        exclude_dirs = []
    
    result = []
    for file_path in files:
        # Skip if any parent directory is in exclude_dirs
        if any(part in exclude_dirs for part in file_path.parts):
            continue
        if file_path.is_file():
            result.append(file_path)
    
    return result


def safe_write(
    file_path: Union[str, Path], 
    content: Union[str, bytes], 
    encoding: str = "utf-8",
    backup: bool = True
) -> Path:
    """
    Safely write content to a file, creating parent directories and optionally backing up.
    
    Args:
        file_path: Path to the file to write
        content: Content to write (string or bytes)
        encoding: Encoding to use for string content (default: utf-8)
        backup: Whether to create a backup if file exists (default: True)
        
    Returns:
        Path to the written file
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    
    if backup and file_path.is_file():
        backup_file(file_path)
    
    if isinstance(content, str):
        file_path.write_text(content, encoding=encoding)
    else:
        file_path.write_bytes(content)
    
    return file_path


def read_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON as dictionary
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(
    file_path: Union[str, Path], 
    data: Dict[str, Any], 
    indent: int = 2,
    encoding: str = "utf-8",
    backup: bool = True
) -> Path:
    """
    Write data as JSON to a file.
    
    Args:
        file_path: Path to the JSON file to write
        data: Dictionary to write as JSON
        indent: Indentation level for pretty printing (default: 2)
        encoding: Encoding to use (default: utf-8)
        backup: Whether to create backup if file exists (default: True)
        
    Returns:
        Path to the written file
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    
    if backup and file_path.is_file():
        backup_file(file_path)
    
    content = json.dumps(data, indent=indent, ensure_ascii=False)
    safe_write(file_path, content, encoding=encoding, backup=False)
    return file_path


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> Path:
    """
    Copy a file to a destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        Path to the copied file
    """
    src = Path(src)
    dst = Path(dst)
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return dst


def move_file(src: Union[str, Path], dst: Union[str, Path]) -> Path:
    """
    Move a file to a destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        Path to the moved file
    """
    src = Path(src)
    dst = Path(dst)
    ensure_dir(dst.parent)
    shutil.move(str(src), str(dst))
    return dst


def delete_file(file_path: Union[str, Path]) -> None:
    """
    Delete a file.
    
    Args:
        file_path: Path to the file to delete
    """
    file_path = Path(file_path)
    if file_path.is_file():
        file_path.unlink()
    else:
        raise FileNotFoundError(f"File not found: {file_path}")


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Size in bytes
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.stat().st_size


def get_file_hash(
    file_path: Union[str, Path], 
    algorithm: str = "sha256"
) -> str:
    """
    Calculate the hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Hexadecimal hash string
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()