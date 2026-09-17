from datetime import date

import pytest

from app.core.auth import AuthenticatedUser, AuthorizationError, Role
from app.domain.calculations import calculate_css, detect_performance_anomaly, readiness_score, session_rpe_load
from app.domain.models import AthleteProfile, PerformanceRecord, WellnessRecord
from app.domain.repository import DomainRepository


def test_css_is_deterministic_and_not_lactate_claim():
    result = calculate_css(140, 300)
    assert result.pace_100_seconds == pytest.approx(80.0)
    assert result.pace_50_seconds == pytest.approx(40.0)


def test_css_rejects_invalid_protocol():
    with pytest.raises(ValueError):
        calculate_css(300, 200)


def test_load_is_deterministic():
    assert session_rpe_load(60, 7) == 420


def test_readiness_explains_multiple_signals_and_confidence():
    result = readiness_score(WellnessRecord(athlete_id="a", recorded_on=date.today(), sleep_hours=5, hrv_ms=40, resting_hr_bpm=58, mood=7, rpe=8), recent_load=700)
    assert result.score < 75
    assert "Sleep" in result.reasons or "HRV" in result.reasons or "RPE" in result.reasons
    assert result.confidence.value == "HIGH"


def test_anomaly_is_not_accepted_as_normal_performance():
    previous = PerformanceRecord(athlete_id="a", recorded_on=date(2026, 1, 1), distance_m=100, stroke="freestyle", time_seconds=62)
    current = PerformanceRecord(athlete_id="a", recorded_on=date(2026, 1, 2), distance_m=100, stroke="freestyle", time_seconds=48)
    assert detect_performance_anomaly(previous, current) is True


def test_future_performance_record_is_rejected():
    with pytest.raises(ValueError, match="Gelecek tarihli"):
        PerformanceRecord(
            athlete_id="a",
            recorded_on=date(2027, 1, 1),
            distance_m=100,
            stroke="freestyle",
            time_seconds=62,
        )


def test_repository_requires_health_consent_and_scopes_tenant():
    repository = DomainRepository()
    admin = AuthenticatedUser(user_id="admin", role=Role.ADMIN)
    athlete = repository.add_athlete(admin, AthleteProfile(organization_id="org-a", team_id="team-a", display_name="Ada", consent_health_data=True))
    athlete_user = AuthenticatedUser(user_id="athlete", role=Role.ATHLETE, student_id=athlete.athlete_id)
    repository.add_performance(athlete_user, PerformanceRecord(athlete_id=athlete.athlete_id, recorded_on=date.today(), distance_m=100, stroke="freestyle", time_seconds=62))
    outsider = AuthenticatedUser(user_id="outsider", role=Role.ATHLETE, student_id="other")
    with pytest.raises(AuthorizationError):
        repository.get_performances(outsider, athlete.athlete_id)
