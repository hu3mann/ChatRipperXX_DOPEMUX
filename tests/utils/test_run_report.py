"""Tests for run report writer and validator."""

import builtins
from datetime import UTC, datetime, timedelta
from pathlib import Path

from chatx.utils.run_report import (
    append_metrics_event,
    iso_now,
    validate_run_report,
    write_extract_run_report,
)


class TestRunReport:
    def test_write_and_validate_run_report(self, tmp_path):
        out = tmp_path / "out"
        started_at = datetime.now(UTC)
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
        assert "images_total" in data

    def test_validate_run_report_failure(self, tmp_path):
        # Create an invalid report missing required fields
        invalid_path = tmp_path / "run_report.json"
        invalid_path.write_text("{}", encoding="utf-8")

        # Should be invalid (schema present in repo)
        assert validate_run_report(invalid_path) is False

    def test_validate_run_report_missing_schema(self, tmp_path):
        report = tmp_path / "run_report.json"
        report.write_text("{}", encoding="utf-8")

        schemas_dir = Path(__file__).resolve().parents[2] / "schemas"
        schema = schemas_dir / "run_report.schema.json"
        backup = schema.with_suffix(".bak")
        schema.rename(backup)
        try:
            assert validate_run_report(report) is True
        finally:
            backup.rename(schema)

    def test_validate_run_report_import_error(self, tmp_path, monkeypatch):
        report = tmp_path / "run_report.json"
        report.write_text("{}", encoding="utf-8")

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):  # pragma: no cover - exercised
            if name == "jsonschema":
                raise ImportError
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        assert validate_run_report(report) is True

    def test_append_metrics_event(self, tmp_path):
        started_at = datetime.now(UTC)
        finished_at = started_at
        path = append_metrics_event(
            out_dir=tmp_path,
            component="extract",
            started_at=started_at,
            finished_at=finished_at,
            counters={"messages_total": 1},
        )
        assert path.exists()

    def test_iso_now(self):
        ts = iso_now()
        assert isinstance(ts, str)

