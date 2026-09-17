from app.memory.segmentation import DurableMemorySegmentor, MemoryRecord, MemoryScope


def test_student_cannot_see_coach_private_notes():
    segmentor = DurableMemorySegmentor()
    records = [
        MemoryRecord(
            record_id="r1",
            owner_id="student-1",
            scope=MemoryScope.STUDENT,
            content="Öğrenci notu",
        ),
        MemoryRecord(
            record_id="r2",
            owner_id="coach-1",
            scope=MemoryScope.COACH,
            content="Özel koç notu",
        ),
        MemoryRecord(
            record_id="r3",
            owner_id="system",
            scope=MemoryScope.SYSTEM,
            content="Sistem uyarısı",
        ),
    ]

    sanitized = segmentor.sanitize_context_for_agent(
        records,
        requesting_role="student",
        authenticated_student_id="student-1",
    )

    assert [rec.record_id for rec in sanitized] == ["r1", "r3"]


def test_coach_can_read_private_context_for_student_scope():
    segmentor = DurableMemorySegmentor()
    records = [
        MemoryRecord(
            record_id="student-note",
            owner_id="student-1",
            scope=MemoryScope.STUDENT,
            content="Öğrenci ana hedefi",
        ),
        MemoryRecord(
            record_id="coach-note",
            owner_id="coach-1",
            scope=MemoryScope.COACH,
            content="Koçun özel notu",
        ),
    ]

    sanitized = segmentor.sanitize_context_for_agent(
        records,
        requesting_role="coach",
        authenticated_student_id="student-1",
    )

    assert {rec.record_id for rec in sanitized} == {"student-note", "coach-note"}


def test_prompt_context_formats_memory_blocks():
    segmentor = DurableMemorySegmentor()
    records = [
        MemoryRecord(
            record_id="r1",
            owner_id="student-1",
            scope=MemoryScope.STUDENT,
            content="Düzenli çalışıyor",
        )
    ]

    prompt = segmentor.prepare_agent_prompt_context(records)

    assert "[STUDENT CONTEXT]" in prompt
    assert "Düzenli çalışıyor" in prompt
