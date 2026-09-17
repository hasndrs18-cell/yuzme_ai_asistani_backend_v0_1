from dataclasses import dataclass, field
from enum import Enum


class VideoAnalysisStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    ANALYZING = "ANALYZING"
    READY = "READY"
    FAILED = "FAILED"
    UNCONFIGURED = "UNCONFIGURED"
    QUEUED = "QUEUED"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True)
class VideoAnalysisReport:
    video_id: str
    status: VideoAnalysisStatus
    confidence: str
    metrics: dict[str, float]
    evidence: list[str]
    limitation: str
    observations: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    failure_code: str | None = None


class PoseEstimationProvider:
    async def analyze(self, video_id: str, *, context: dict[str, object] | None = None) -> VideoAnalysisReport:
        raise NotImplementedError


class UnconfiguredPoseProvider(PoseEstimationProvider):
    async def analyze(self, video_id: str, *, context: dict[str, object] | None = None) -> VideoAnalysisReport:
        return VideoAnalysisReport(
            video_id=video_id,
            status=VideoAnalysisStatus.UNCONFIGURED,
            confidence="LOW",
            metrics={},
            evidence=[],
            limitation="AI video analysis provider not connected; no biomechanical measurement was produced.",
            provenance=["PROVIDER_NOT_CONNECTED"],
            failure_code="PROVIDER_NOT_CONNECTED",
        )
