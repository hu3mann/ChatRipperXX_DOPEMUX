"""Local-only audio transcription for voice notes."""

from pathlib import Path
from typing import Optional


def transcribe_local(audio_file_path: Path) -> Optional[str]:
    """Transcribe audio file using local transcription engine.
    
    Args:
        audio_file_path: Path to audio file to transcribe
        
    Returns:
        Transcript text if successful, None if failed
        
    Note:
        This is a placeholder shim. Actual transcription engine will be
        chosen via ADR after PR-6. Implementation will:
        - Use only local transcription (never cloud)
        - Support deterministic output for testing
        - Handle common audio formats (m4a, caf, etc.)
        - Store engine choice in source_meta for provenance
    """
    # TODO: Implement in PR-5
    # - Choose local transcription engine (Whisper variant?)
    # - Add engine configuration and model management
    # - Handle audio format detection and conversion
    # - Add deterministic mode for testing
    # - Add proper error handling and logging
    
    # Placeholder implementation for testing
    if audio_file_path.suffix.lower() in {'.m4a', '.caf', '.mp3', '.wav'}:
        return f"[MOCK TRANSCRIPT] Audio from {audio_file_path.name}"
    
    return None


def is_audio_attachment(mime_type: Optional[str], uti: Optional[str]) -> bool:
    """Check if attachment is an audio file suitable for transcription.
    
    Args:
        mime_type: MIME type from attachment metadata
        uti: Uniform Type Identifier from attachment metadata
        
    Returns:
        True if attachment appears to be audio
    """
    if mime_type and mime_type.startswith('audio/'):
        return True
        
    if uti:
        audio_utis = {
            'public.audio',
            'public.mp3', 
            'public.mpeg-4-audio',
            'com.apple.coreaudio-format'
        }
        return uti in audio_utis
        
    return False