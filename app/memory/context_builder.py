from app.agent.schemas import StudentContext
from app.students.repository import StudentRepository


class ContextBuilder:
    def __init__(self, repository: StudentRepository) -> None:
        self.repository = repository

    async def build(self, student_id: str, user_message: str) -> StudentContext:
        return await self.repository.get_context(student_id, user_message)
