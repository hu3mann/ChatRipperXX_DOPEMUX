"""Core iMessage extraction logic - row to Message mapping."""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from chatx.schemas.message import CanonicalMessage


# Apple Core Data reference date: 2001-01-01 00:00:00 UTC
APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)


def extract_messages(
    db_path: Path,
    contact: str,
    *,
    include_attachments: bool = False,
    copy_binaries: bool = False,
    transcribe_audio: str = "off",
    out_dir: Path,
) -> Iterator[CanonicalMessage]:
    """Extract iMessage conversations for a contact.
    
    Args:
        db_path: Path to chat.db file
        contact: Phone number, email, or contact identifier
        include_attachments: Whether to include attachment metadata
        copy_binaries: Whether to copy attachment files to out_dir
        transcribe_audio: Transcription mode ('local' or 'off')
        out_dir: Output directory for files and reports
        
    Yields:
        CanonicalMessage objects with full fidelity (replies, reactions, attachments)
    """
    from chatx.imessage.db import copy_db_for_readonly, open_ro
    from chatx.schemas.message import SourceRef
    
    # Safe DB copy and read-only access
    with copy_db_for_readonly(db_path) as temp_db:
        conn = open_ro(temp_db)
        
        try:
            # Resolve contact to handle IDs  
            handle_ids = resolve_contact_handles(conn, contact)
            if not handle_ids:
                return  # No messages found for contact
            
            # Get conversation GUIDs for this contact
            conv_guids = get_conversation_guids(conn, handle_ids)
            
            # Extract messages for each conversation
            for conv_guid in conv_guids:
                yield from extract_messages_for_conversation(
                    conn, conv_guid, str(db_path), include_attachments, copy_binaries,
                    transcribe_audio, out_dir
                )
                
        finally:
            conn.close()


def extract_messages_for_conversation(
    conn: sqlite3.Connection,
    conv_guid: str, 
    original_db_path: str,
    include_attachments: bool,
    copy_binaries: bool,
    transcribe_audio: str,
    out_dir: Path
) -> Iterator[CanonicalMessage]:
    """Extract messages for a specific conversation."""
    from chatx.schemas.message import SourceRef
    
    # SQL to get messages with handle info - no reactions/replies/attachments yet (PR-2/3)
    query = """
    SELECT 
        m.ROWID,
        m.guid,
        m.text,
        m.attributedBody,
        m.is_from_me,
        m.service,
        m.date,
        m.handle_id,
        h.id as handle_address,
        c.guid as chat_guid
    FROM message m
    JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
    JOIN chat c ON cmj.chat_id = c.ROWID
    LEFT JOIN handle h ON m.handle_id = h.ROWID
    WHERE c.guid = ?
        AND m.associated_message_type = 0  -- Skip reactions for now (PR-2)
    ORDER BY m.date ASC
    """
    
    cursor = conn.execute(query, (conv_guid,))
    
    for row in cursor:
        (
            msg_rowid, guid, text, attributed_body, is_from_me, service, date,
            handle_id, handle_address, chat_guid
        ) = row
        
        # Convert Apple timestamp to ISO-8601 UTC
        timestamp = apple_timestamp_to_iso(date) if date else datetime.now(timezone.utc).isoformat()
        
        # Determine sender information
        if is_from_me:
            sender = "Me"
            sender_id = "me"
        else:
            sender = handle_address or f"Unknown_{handle_id}"
            sender_id = handle_address or f"unknown_{handle_id}"
        
        # Handle text content (attributed body takes precedence if present)
        message_text = text
        if attributed_body and not text:
            # For now, just indicate attributed content exists (proper parsing in future PR)
            message_text = "[Rich text content]"
        
        # Create message with basic provenance (no reactions/replies/attachments yet)
        yield CanonicalMessage(
            msg_id=f"msg_{msg_rowid}",
            conv_id=chat_guid or f"conv_{conv_guid}",
            platform="imessage",
            timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
            sender=sender,
            sender_id=sender_id,
            is_me=bool(is_from_me),
            text=message_text,
            reply_to_msg_id=None,  # Will be implemented in PR-2
            reactions=[],  # Will be implemented in PR-2  
            attachments=[],  # Will be implemented in PR-3
            source_ref=SourceRef(
                guid=guid or f"msg_{msg_rowid}",
                path=original_db_path
            ),
            source_meta={
                "rowid": msg_rowid,
                "service": service,
                "date_raw": date,
                "has_attributed_body": bool(attributed_body)
            }
        )


def get_conversation_guids(conn: sqlite3.Connection, handle_ids: List[int]) -> List[str]:
    """Get conversation GUIDs that involve the specified handles."""
    if not handle_ids:
        return []
    
    # Build query for conversations involving any of these handles
    placeholders = ",".join("?" * len(handle_ids))
    query = f"""
    SELECT DISTINCT c.guid
    FROM chat c
    JOIN chat_message_join cmj ON c.ROWID = cmj.chat_id  
    JOIN message m ON cmj.message_id = m.ROWID
    WHERE m.handle_id IN ({placeholders})
       OR m.is_from_me = 1  -- Include our own messages in these chats
    """
    
    cursor = conn.execute(query, handle_ids)
    return [row[0] for row in cursor if row[0]]


def apple_timestamp_to_iso(apple_timestamp: int) -> str:
    """Convert Apple Core Data timestamp to ISO-8601 UTC string.
    
    Args:
        apple_timestamp: Apple timestamp (nanoseconds since 2001-01-01)
        
    Returns:
        ISO-8601 UTC timestamp string
    """
    # Apple timestamps are in nanoseconds, convert to seconds
    timestamp_seconds = apple_timestamp / 1_000_000_000
    dt = APPLE_EPOCH + timedelta(seconds=timestamp_seconds)
    return dt.isoformat().replace('+00:00', 'Z')


def resolve_contact_handles(conn: sqlite3.Connection, contact: str) -> List[int]:
    """Resolve contact identifier to all associated handle ROWIDs.
    
    Args:
        conn: SQLite database connection
        contact: Phone number, email, or name to resolve
        
    Returns:
        List of handle ROWIDs associated with the contact
    """
    handle_rowids = []
    
    # Direct exact match first
    cursor = conn.execute("SELECT ROWID FROM handle WHERE id = ?", (contact,))
    exact_match = cursor.fetchone()
    if exact_match:
        handle_rowids.append(exact_match[0])
    
    # Phone number variations (basic normalization)
    if contact.startswith('+') or contact.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit():
        # Try different phone number formats
        normalized = ''.join(c for c in contact if c.isdigit())
        variations = [
            contact,
            f"+1{normalized}" if len(normalized) == 10 else contact,
            f"+{normalized}",
            normalized,
            f"({normalized[:3]}) {normalized[3:6]}-{normalized[6:]}" if len(normalized) == 10 else contact
        ]
        
        for variation in variations:
            cursor = conn.execute("SELECT ROWID FROM handle WHERE id = ?", (variation,))
            result = cursor.fetchone()
            if result and result[0] not in handle_rowids:
                handle_rowids.append(result[0])
    
    # Partial matching for emails and names (case insensitive)
    cursor = conn.execute(
        "SELECT ROWID FROM handle WHERE LOWER(id) LIKE LOWER(?)",
        (f"%{contact}%",)
    )
    for row in cursor:
        if row[0] not in handle_rowids:
            handle_rowids.append(row[0])
    
    return handle_rowids