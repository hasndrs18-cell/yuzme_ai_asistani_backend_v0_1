from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    BLOCK = "BLOCK"
    WARNING = "WARNING"
    INFO = "INFO"


class DataIssue(BaseModel):
    row: int
    field: str
    severity: Severity
    message: str


def validate_performance_input(*, row: int, distance_m: int, time_seconds: float, record_date: date, today: date | None = None) -> list[DataIssue]:
    issues: list[DataIssue] = []
    if distance_m <= 0:
        issues.append(DataIssue(row=row, field="distance_m", severity=Severity.BLOCK, message="Mesafe pozitif olmalıdır"))
    if time_seconds <= 0:
        issues.append(DataIssue(row=row, field="time_seconds", severity=Severity.BLOCK, message="Süre pozitif olmalıdır"))
    if today and record_date > today:
        issues.append(DataIssue(row=row, field="record_date", severity=Severity.BLOCK, message="Gelecek tarihli performans kaydı alınamaz"))
    if time_seconds > 0 and distance_m / time_seconds > 8:
        issues.append(DataIssue(row=row, field="time_seconds", severity=Severity.WARNING, message="Olağandışı hız; kaynağı doğrulayın"))
    return issues


def validate_heart_rate(*, row: int, heart_rate_bpm: float | None, hrmax_bpm: float | None) -> list[DataIssue]:
    issues: list[DataIssue] = []
    if heart_rate_bpm is not None and not 20 <= heart_rate_bpm <= 240:
        issues.append(DataIssue(row=row, field="heart_rate_bpm", severity=Severity.BLOCK, message="HR 20-240 bpm arasında olmalıdır"))
    if hrmax_bpm is not None and not 80 <= hrmax_bpm <= 250:
        issues.append(DataIssue(row=row, field="hrmax_bpm", severity=Severity.BLOCK, message="HRmax 80-250 bpm arasında olmalıdır"))
    if heart_rate_bpm and hrmax_bpm and heart_rate_bpm > hrmax_bpm:
        issues.append(DataIssue(row=row, field="heart_rate_bpm", severity=Severity.WARNING, message="HR, HRmax değerini aşıyor; veri doğrulanmalı"))
    return issues
