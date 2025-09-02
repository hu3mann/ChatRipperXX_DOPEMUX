"""Attachment metadata extraction and binary file copying."""

import hashlib
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from chatx.schemas.message import Attachment


def extract_attachment_metadata(
    conn: sqlite3.Connection, 
    message_rowid: int
) -> List[Attachment]:
    """Extract attachment metadata for a message.
    
    Args:
        conn: SQLite database connection
        message_rowid: Message ROWID to get attachments for
        
    Returns:
        List of attachment metadata objects
        
    Note:
        This is a placeholder. Full implementation in PR-3.
    """
    # TODO: Implement attachment metadata extraction
    # - JOIN message_attachment_join -> attachment
    # - Map attachment fields to MessageAttachment schema
    # - Handle missing files gracefully
    return []


def copy_attachment_files(
    attachments: List[Attachment],
    out_dir: Path
) -> List[Attachment]:
    """Copy attachment files to output directory with content hashing.
    
    Args:
        attachments: List of attachment metadata
        out_dir: Base output directory
        
    Returns:
        Updated attachment list with copied file paths
        
    Note:
        Uses content hashing for deduplication and collision avoidance:
        out_dir/attachments/<sha256[:2]>/<sha256>/<original_basename>
    """
    # TODO: Implement in PR-3
    # - Content-based hashing for deduplication
    # - Create directory structure
    # - Update abs_path in attachment metadata
    return attachments


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file contents.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hex-encoded SHA-256 hash
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()