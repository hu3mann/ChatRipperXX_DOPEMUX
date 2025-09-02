"""Tests for run report writer and validator."""

from datetime import datetime, timedelta
from pathlib import Path

from chatx.utils.run_report import write_extract_run_report, validate_run_report


class TestRunReport:
    def test_write_and_validate_run_report(self, tmp_path):
        out = tmp_path / "out"
        started_at = datetime.utcnow()
        finished_at = started_at + timedelta(seconds=2)

        report_path = write_extract_run_report(
            out_dir=out,
            started_at=started_at,
            finished_at=finished_at,
            messages_total=10,
            attachments_total=2,
            images_total=1,
            throughput_msgs_min=300.0,
            artifacts=[str(out / "messages_contact.json")],
            warnings=["example warning"],
        )

        assert report_path.exists()
        assert validate_run_report(report_path) is True
        data = report_path.read_text(encoding="utf-8")
        assert '"images_total": 1' in data

    def test_validate_run_report_failure(self, tmp_path):
        # Create an invalid report missing required fields
        invalid_path = tmp_path / "run_report.json"
        invalid_path.write_text("{}", encoding="utf-8")

        # Should be invalid (schema present in repo)
        assert validate_run_report(invalid_path) is False

