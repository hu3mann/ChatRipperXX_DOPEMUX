"""iMessage attachment processing utilities."""

import hashlib
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from chatx.schemas.message import Attachment

# UTI to attachment type mapping (Apple Uniform Type Identifiers)
UTI_TYPE_MAP: Dict[str, str] = {
    # Images
    "public.jpeg": "image",
    "public.png": "image", 
    "public.tiff": "image",
    "public.gif": "image",
    "public.heic": "image",
    "public.heif": "image",
    "com.apple.private.live-photo": "image",
    
    # Videos
    "public.mpeg-4": "video",
    "public.quicktime-movie": "video",
    "public.avi": "video",
    "com.apple.m4v-video": "video",
    "public.3gpp": "video",
    
    # Audio
    "public.mp3": "audio",
    "public.mpeg-4-audio": "audio",
    "com.apple.m4a-audio": "audio",
    "public.aiff-audio": "audio",
    "public.wav": "audio",
    "com.apple.coreaudio-format": "audio",
    
    # Documents
    "com.adobe.pdf": "file",
    "com.microsoft.word.doc": "file",
    "org.openxmlformats.wordprocessingml.document": "file",
    "com.microsoft.excel.xls": "file",
    "com.microsoft.powerpoint.ppt": "file",
    "public.plain-text": "file",
    "public.rtf": "file",
    
    # Archives
    "public.zip-archive": "file",
    "public.tar-archive": "file",
    "com.apple.binhex-archive": "file",
}

# MIME type fallback mapping
MIME_TYPE_MAP: Dict[str, str] = {
    # Images
    "image/jpeg": "image",
    "image/png": "image",
    "image/gif": "image",
    "image/tiff": "image",
    "image/heic": "image",
    "image/heif": "image",
    
    # Videos  
    "video/mp4": "video",
    "video/quicktime": "video",
    "video/avi": "video",
    "video/3gpp": "video",
    
    # Audio
    "audio/mpeg": "audio",
    "audio/mp3": "audio", 
    "audio/mp4": "audio",
    "audio/wav": "audio",
    "audio/aiff": "audio",
    
    # Documents
    "application/pdf": "file",
    "application/msword": "file",
    "application/vnd.ms-excel": "file",
    "application/vnd.ms-powerpoint": "file",
    "text/plain": "file",
    "application/rtf": "file",
    
    # Archives
    "application/zip": "file",
    "application/x-tar": "file",
}


def determine_attachment_type(uti: Optional[str], mime_type: Optional[str], filename: Optional[str]) -> str:
    """Determine attachment type from UTI, MIME type, and filename.
    
    Args:
        uti: Apple UTI (Uniform Type Identifier)
        mime_type: MIME type
        filename: Original filename
        
    Returns:
        Attachment type: "image", "video", "audio", "file", or "unknown"
    """
    # Try UTI first (most reliable on macOS)
    if uti and uti in UTI_TYPE_MAP:
        return UTI_TYPE_MAP[uti]
    
    # Fallback to MIME type
    if mime_type and mime_type in MIME_TYPE_MAP:
        return MIME_TYPE_MAP[mime_type]
    
    # Last resort: filename extension
    if filename:
        ext = Path(filename).suffix.lower()
        if ext in {'.jpg', '.jpeg', '.png', '.gif', '.tiff', '.heic', '.heif'}:
            return "image"
        elif ext in {'.mp4', '.mov', '.avi', '.mkv', '.3gp'}:
            return "video"
        elif ext in {'.mp3', '.m4a', '.wav', '.aiff', '.flac'}:
            return "audio"
        elif ext in {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.zip', '.tar'}:
            return "file"
    
    return "unknown"


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
    """
    query = """
    SELECT 
        a.ROWID,
        a.filename,
        a.uti,
        a.mime_type,
        a.transfer_name,
        a.total_bytes,
        a.created_date,
        a.start_date
    FROM attachment a
    JOIN message_attachment_join maj ON a.ROWID = maj.attachment_id
    WHERE maj.message_id = ?
    """
    
    cursor = conn.execute(query, (message_rowid,))
    attachments = []
    
    for row in cursor:
        (rowid, filename, uti, mime_type, transfer_name, total_bytes, created_date, start_date) = row
        
        # Determine attachment type
        att_type = determine_attachment_type(uti, mime_type, filename or transfer_name)
        
        # Use transfer_name if filename is None
        display_filename = filename or transfer_name or f"attachment_{rowid}"
        
        attachment = Attachment(
            type=att_type,
            filename=display_filename,
            abs_path=None,  # Will be set during file copying if requested
            mime_type=mime_type,
            uti=uti,
            transfer_name=transfer_name
        )
        
        attachments.append(attachment)
    
    return attachments


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
        
    Uses content hashing for deduplication and collision avoidance:
    out_dir/attachments/<sha256[:2]>/<sha256>/<original_basename>
    """
    # Typical macOS attachment path
    attachments_dir = Path.home() / "Library" / "Messages" / "Attachments"
    
    updated_attachments = []
    
    for attachment in attachments:
        # Try to find source file
        source_path = None
        if attachment.filename:
            # Try common attachment paths
            potential_paths = [
                attachments_dir / attachment.filename,
                attachments_dir / "Attachments" / attachment.filename,  # Nested structure
                Path(attachment.filename)  # Absolute path case
            ]
            
            for path in potential_paths:
                if path.exists():
                    source_path = path
                    break
        
        # Copy file if found
        if source_path and source_path.exists():
            try:
                # Compute content hash
                file_hash = compute_file_hash(source_path)
                
                # Create destination directory structure
                dest_subdir = out_dir / "attachments" / file_hash[:2]
                dest_subdir.mkdir(parents=True, exist_ok=True)
                
                # Create final destination path
                dest_filename = f"{file_hash}_{attachment.filename}"
                dest_path = dest_subdir / dest_filename
                
                # Copy file if not already exists
                if not dest_path.exists():
                    shutil.copy2(source_path, dest_path)
                
                # Update attachment with copied file path
                attachment.abs_path = str(dest_path)
                
            except (OSError, IOError, shutil.Error):
                # File copy failed, but continue with metadata
                pass
        
        updated_attachments.append(attachment)
    
    return updated_attachments


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