from typing import Protocol

from app.agent.schemas import StudentContext


class StudentRepository(Protocol):
    async def get_context(self, student_id: str, user_message: str) -> StudentContext:
        ...


class InMemoryStudentRepository:
    def __init__(self) -> None:
        self._students: dict[str, StudentContext] = {
            "demo-student": StudentContext(
                student_id="demo-student",
                student_name="Deneme Öğrencisi",
                level="Orta seviye",
                primary_goal="Freestyle tekniğini geliştirmek",
                current_focus="Nefes zamanlaması",
                current_problems=["Nefes alırken baş hareketi"],
                recent_training=["25 m nefes drill'i tamamlandı", "50 m normal freestyle uygulandı"],
                recent_feedback=["Nefes sırasında baş hareketine dikkat et"],
                coach_notes=["Şimdilik hizalanmayı önceliklendir."],
                relevant_lessons=["Nefes Zamanlaması"],
                relevant_drills=["6-Count Switch"],
                performance_history=["Son 2 seansta nefes çalışması düzenli tamamlandı"],
            )
        }

    async def get_context(self, student_id: str, user_message: str) -> StudentContext:
        return self._students.get(
            student_id,
            StudentContext(
                student_id=student_id,
                student_name="Öğrenci",
                level="Belirtilmemiş",
            ),
        )
