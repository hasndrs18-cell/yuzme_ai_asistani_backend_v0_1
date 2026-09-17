import csv
from datetime import date
from io import TextIOWrapper

from pydantic import BaseModel

from app.domain.data_quality import DataIssue, Severity, validate_heart_rate, validate_performance_input


class ImportPreview(BaseModel):
    accepted_rows: list[dict[str, str]]
    issues: list[DataIssue]
    total_rows: int
    requires_confirmation: bool = True


def preview_performance_csv(file: TextIOWrapper, *, today: date | None = None) -> ImportPreview:
    reader = csv.DictReader(file)
    required = {"athlete_id", "recorded_on", "distance_m", "stroke", "time_seconds"}
    missing = required - set(reader.fieldnames or [])
    if missing:
        return ImportPreview(accepted_rows=[], issues=[DataIssue(row=1, field="header", severity=Severity.BLOCK, message=f"Eksik kolon: {', '.join(sorted(missing))}")], total_rows=0)
    accepted: list[dict[str, str]] = []
    issues: list[DataIssue] = []
    total = 0
    seen: set[tuple[str, str, str, str]] = set()
    for row_number, row in enumerate(reader, start=2):
        total += 1
        try:
            key = (row["athlete_id"], row["recorded_on"], row["distance_m"], row["time_seconds"])
            row_issues = validate_performance_input(row=row_number, distance_m=int(row["distance_m"]), time_seconds=float(row["time_seconds"]), record_date=date.fromisoformat(row["recorded_on"]), today=today)
        except (ValueError, TypeError):
            row_issues = [DataIssue(row=row_number, field="record", severity=Severity.BLOCK, message="Format geçersiz: tarih, mesafe veya süre okunamadı")]
            key = (str(row_number), "", "", "")
        if key in seen:
            row_issues.append(DataIssue(row=row_number, field="record", severity=Severity.BLOCK, message="Aynı dosyada duplicate kayıt"))
        seen.add(key)
        issues.extend(row_issues)
        if not any(issue.severity is Severity.BLOCK for issue in row_issues):
            accepted.append(row)
    return ImportPreview(accepted_rows=accepted, issues=issues, total_rows=total)
