"""Missing attachment reporting for iCloud eviction scenarios."""

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def generate_missing_attachments_report(
    conn: sqlite3.Connection,
    out_dir: Path
) -> Dict[str, int]:
    """Generate report of missing/evicted attachment files.
    
    Args:
        conn: SQLite database connection  
        out_dir: Output directory for report file
        
    Returns:
        Dictionary with per-conversation missing counts
        
    Note:
        Creates out_dir/missing_attachments.json with detailed report
        for operator remediation. Exit code remains 0 (non-fatal).
    """
    # TODO: Implement in PR-4
    # - Scan all attachment records in DB
    # - Check file existence on disk
    # - Group by conversation for actionable counts
    # - Include sample filenames for guidance
    
    report_data = {
        "summary": {
            "total_missing": 0,
            "conversations_affected": 0,
            "report_timestamp": "",
        },
        "conversations": {},
        "remediation_guidance": {
            "manual_steps": [
                "Open Messages app",
                "Navigate to affected conversation",
                "Go to conversation Details/Info",
                "Tap 'Download All Attachments' if available",
                "Re-run extraction after download completes"
            ]
        }
    }
    
    report_path = out_dir / "missing_attachments.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    return {}