from datetime import date
from io import StringIO

import pytest

from app.domain.csv_import import preview_performance_csv
from app.domain.data_quality import Severity, validate_heart_rate
from app.integrations.research import UnconfiguredResearchProvider
from app.integrations.video_analysis import UnconfiguredPoseProvider, VideoAnalysisStatus


def test_csv_preview_reports_duplicate_and_future_rows():
    file = StringIO("athlete_id,recorded_on,distance_m,stroke,time_seconds\na,2026-09-15,100,freestyle,62\na,2026-09-15,100,freestyle,62\na,2027-01-01,100,freestyle,61\n")
    preview = preview_performance_csv(file, today=date(2026, 9, 15))
    assert preview.total_rows == 3
    assert any(issue.severity is Severity.BLOCK for issue in preview.issues)
    assert len(preview.accepted_rows) == 1


def test_hr_validation_blocks_impossible_values():
    assert validate_heart_rate(row=2, heart_rate_bpm=260, hrmax_bpm=190)[0].severity is Severity.BLOCK


@pytest.mark.asyncio
async def test_unconfigured_providers_do_not_fabricate_results():
    research = await UnconfiguredResearchProvider().search("CSS threshold")
    video = await UnconfiguredPoseProvider().analyze("video-1")
    assert research.sources == ()
    assert video.status is VideoAnalysisStatus.UNCONFIGURED
    assert video.metrics == {}
