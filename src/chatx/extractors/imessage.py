"""iMessage extractor for macOS/iOS chat.db SQLite databases."""

import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from chatx.extractors.base import BaseExtractor, ExtractionError
from chatx.schemas.message import Attachment, CanonicalMessage, Reaction, SourceRef
from chatx.utils.logging import get_logger

logger = get_logger(__name__)

# Apple epoch starts at 2001-01-01T00:00:00Z
APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

# Reaction type mappings
REACTION_TYPES = {
    2000: "love",
    2001: "like", 
    2002: "dislike",
    2003: "laugh",
    2004: "emphasize",
    2005: "question",
}


class IMessageExtractor(BaseExtractor):
    """Extract messages from iMessage chat.db SQLite database.
    
    Implements the iMessage specification with support for:
    - Message extraction with proper Apple epoch conversion
    - Reaction folding into target messages
    - Reply chain resolution
    - Attachment metadata extraction
    - Lossless source_meta preservation
    """
    
    @property
    def platform(self) -> str:
        return "imessage"
    
    def validate_source(self) -> bool:
        """Validate that source is an iMessage database."""
        if not self.source_path.suffix == '.db':
            return False
            
        try:
            with sqlite3.connect(self.source_path) as conn:
                cursor = conn.cursor()
                # Check for required iMessage tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('message', 'chat', 'handle')
                """)
                tables = {row[0] for row in cursor.fetchall()}
                return {'message', 'chat', 'handle'}.issubset(tables)
        except Exception as e:
            logger.warning(f"Failed to validate iMessage database: {e}")
            return False
    
    def _convert_apple_timestamp(self, timestamp: Optional[float]) -> Optional[datetime]:
        """Convert Apple epoch timestamp to UTC datetime.
        
        Args:
            timestamp: Apple epoch timestamp (may be seconds or nanoseconds)
            
        Returns:
            UTC datetime or None if timestamp is invalid
        """
        if timestamp is None or timestamp == 0:
            return None
            
        # Determine if timestamp is in nanoseconds or seconds
        if abs(timestamp) >= 1e11:
            # Nanoseconds - divide by 1 billion
            timestamp = timestamp / 1_000_000_000
            
        try:
            return APPLE_EPOCH.replace(tzinfo=timezone.utc) + \
                   datetime.fromtimestamp(timestamp, tz=timezone.utc).utctimetuple()
        except (ValueError, OSError) as e:
            logger.warning(f"Failed to convert timestamp {timestamp}: {e}")
            return None
    
    def _copy_database(self) -> Path:
        """Copy database to temporary location to avoid file locks.
        
        Returns:
            Path to temporary database copy
        """
        temp_dir = Path(tempfile.mkdtemp(prefix="chatx_imessage_"))
        temp_db = temp_dir / "chat.db"
        
        # Copy main database
        shutil.copy2(self.source_path, temp_db)
        
        # Copy WAL file if present
        wal_path = self.source_path.with_suffix('.db-wal')
        if wal_path.exists():
            temp_wal = temp_db.with_suffix('.db-wal') 
            shutil.copy2(wal_path, temp_wal)
        
        # Copy SHM file if present
        shm_path = self.source_path.with_suffix('.db-shm')
        if shm_path.exists():
            temp_shm = temp_db.with_suffix('.db-shm')
            shutil.copy2(shm_path, temp_shm)
            
        return temp_db
    
    def _fetch_raw_messages(self, conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Fetch all messages with joins to related tables.
        
        Args:
            conn: SQLite connection
            
        Returns:
            List of raw message dictionaries
        """
        query = """
        SELECT 
          m.ROWID as msg_rowid,
          m.guid as msg_guid,
          m.text as body,
          m.attributedBody as body_rich,
          m.is_from_me as is_me,
          m.handle_id as handle_id,
          m.service as service,
          m.date as date_raw,
          m.associated_message_guid as assoc_guid,
          m.associated_message_type as assoc_type,
          m.cache_has_attachments as has_attachments,
          m.balloon_bundle_id as balloon_bundle_id,
          c.guid as chat_guid,
          h.id as handle_id_resolved
        FROM message m
        LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID  
        LEFT JOIN chat c ON c.ROWID = cmj.chat_id
        LEFT JOIN handle h ON h.ROWID = m.handle_id
        ORDER BY m.date ASC
        """
        
        cursor = conn.cursor()
        cursor.execute(query)
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _fetch_attachments(self, conn: sqlite3.Connection, msg_rowid: int) -> List[Attachment]:
        """Fetch attachments for a specific message.
        
        Args:
            conn: SQLite connection
            msg_rowid: Message ROWID
            
        Returns:
            List of Attachment objects
        """
        query = """
        SELECT
          a.filename,
          a.uti,
          a.mime_type,
          a.transfer_name,
          a.total_bytes,
          a.created_date,
          a.start_date,
          a.user_info
        FROM message_attachment_join maj
        JOIN attachment a ON maj.attachment_id = a.ROWID
        WHERE maj.message_id = ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (msg_rowid,))
        
        attachments = []
        for row in cursor.fetchall():
            filename, uti, mime_type, transfer_name, total_bytes, created_date, start_date, user_info = row
            
            # Determine attachment type from UTI or filename
            att_type = "unknown"
            if uti:
                if "image" in uti.lower():
                    att_type = "image"
                elif "video" in uti.lower() or "movie" in uti.lower():
                    att_type = "video"
                elif "audio" in uti.lower():
                    att_type = "audio"
                else:
                    att_type = "file"
            elif filename and '.' in filename:
                ext = filename.split('.')[-1].lower()
                if ext in {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'heic'}:
                    att_type = "image"
                elif ext in {'mp4', 'mov', 'avi', 'mkv', 'wmv', 'm4v'}:
                    att_type = "video" 
                elif ext in {'mp3', 'wav', 'aac', 'm4a', 'flac', 'ogg'}:
                    att_type = "audio"
                else:
                    att_type = "file"
            
            attachment = Attachment(
                type=att_type,  # type: ignore
                filename=filename or transfer_name or "unknown",
                mime_type=mime_type,
                uti=uti,
                transfer_name=transfer_name,
            )
            attachments.append(attachment)
            
        return attachments
    
    def _group_reactions(self, raw_messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, List[Reaction]]]:
        """Group reactions by target message and filter out reaction rows.
        
        Args:
            raw_messages: List of raw message dictionaries
            
        Returns:
            Tuple of (non-reaction messages, reactions grouped by target guid)
        """
        reactions_by_target: Dict[str, List[Reaction]] = {}
        non_reaction_messages = []
        
        for msg in raw_messages:
            assoc_type = msg.get('assoc_type')
            assoc_guid = msg.get('assoc_guid')
            
            # Check if this is a reaction (tapback)
            if assoc_type in REACTION_TYPES and assoc_guid:
                # This is a reaction - fold it into target message
                reaction_kind = REACTION_TYPES[assoc_type]
                
                # Determine sender
                if msg['is_me']:
                    sender = "Me"
                else:
                    sender = msg.get('handle_id_resolved', 'Unknown')
                
                # Convert timestamp
                timestamp = self._convert_apple_timestamp(msg['date_raw'])
                if timestamp is None:
                    timestamp = datetime.now(timezone.utc)
                    
                reaction = Reaction(
                    from_=sender,
                    kind=reaction_kind,
                    ts=timestamp
                )
                
                if assoc_guid not in reactions_by_target:
                    reactions_by_target[assoc_guid] = []
                reactions_by_target[assoc_guid].append(reaction)
                
                self.report.reactions_folded += 1
                
            else:
                # Regular message
                non_reaction_messages.append(msg)
                
        return non_reaction_messages, reactions_by_target
    
    def _build_guid_to_rowid_map(self, messages: List[Dict[str, Any]]) -> Dict[str, str]:
        """Build mapping from message GUID to ROWID for reply resolution.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary mapping GUID to string ROWID
        """
        return {msg['msg_guid']: str(msg['msg_rowid']) for msg in messages if msg.get('msg_guid')}
    
    def extract_messages(self) -> Iterator[CanonicalMessage]:
        """Extract messages from iMessage database."""
        if not self.validate_source():
            raise ExtractionError(f"Invalid iMessage database: {self.source_path}")
        
        # Copy database to temporary location
        temp_db = self._copy_database()
        
        try:
            with sqlite3.connect(temp_db) as conn:
                # Fetch all raw messages
                raw_messages = self._fetch_raw_messages(conn)
                logger.info(f"Found {len(raw_messages)} raw messages")
                
                # Group reactions and filter out reaction messages
                messages, reactions_by_target = self._group_reactions(raw_messages)
                logger.info(f"Grouped {self.report.reactions_folded} reactions")
                
                # Build GUID to ROWID mapping for reply resolution  
                guid_to_rowid = self._build_guid_to_rowid_map(messages)
                
                # Process each message
                for msg in messages:
                    try:
                        # Convert timestamp
                        timestamp = self._convert_apple_timestamp(msg['date_raw'])
                        if timestamp is None:
                            timestamp = datetime.now(timezone.utc)
                            
                        # Determine sender
                        if msg['is_me']:
                            sender = "Me"
                            sender_id = "me"
                        else:
                            handle = msg.get('handle_id_resolved', 'Unknown')
                            sender = handle
                            sender_id = handle.lower()
                            
                        # Handle replies
                        reply_to_msg_id = None
                        assoc_guid = msg.get('assoc_guid')
                        assoc_type = msg.get('assoc_type')
                        
                        if assoc_guid and assoc_type not in REACTION_TYPES:
                            # This might be a reply
                            if assoc_guid in guid_to_rowid:
                                reply_to_msg_id = guid_to_rowid[assoc_guid]
                            else:
                                # Unresolved reply - track in source_meta
                                self.report.unresolved_replies += 1
                                
                        # Get reactions for this message
                        msg_reactions = reactions_by_target.get(msg['msg_guid'], [])
                        
                        # Fetch attachments
                        attachments = self._fetch_attachments(conn, msg['msg_rowid'])
                        
                        # Build source_meta with all original fields
                        source_meta = {
                            'msg_rowid': msg['msg_rowid'],
                            'service': msg.get('service'),
                            'assoc_guid': msg.get('assoc_guid'),
                            'assoc_type': msg.get('assoc_type'),
                            'has_attachments': msg.get('has_attachments'),
                            'balloon_bundle_id': msg.get('balloon_bundle_id'),
                            'body_rich': msg.get('body_rich'),
                        }
                        
                        # Remove None values
                        source_meta = {k: v for k, v in source_meta.items() if v is not None}
                        
                        # Create canonical message
                        canonical_msg = CanonicalMessage(
                            msg_id=str(msg['msg_rowid']),
                            conv_id=msg.get('chat_guid', 'unknown'),
                            platform="imessage",
                            timestamp=timestamp,
                            sender=sender,
                            sender_id=sender_id,
                            is_me=bool(msg['is_me']),
                            text=msg.get('body'),
                            reply_to_msg_id=reply_to_msg_id,
                            reactions=msg_reactions,
                            attachments=attachments,
                            source_ref=SourceRef(
                                guid=msg.get('chat_guid'),
                                path=str(self.source_path)
                            ),
                            source_meta=source_meta
                        )
                        
                        yield canonical_msg
                        
                    except Exception as e:
                        error_msg = f"Failed to process message {msg.get('msg_rowid', 'unknown')}: {e}"
                        logger.error(error_msg)
                        self.report.errors.append(error_msg)
                        continue
                        
        finally:
            # Clean up temporary database
            try:
                shutil.rmtree(temp_db.parent)
            except Exception as e:
                logger.warning(f"Failed to clean up temp database: {e}")