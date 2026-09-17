from typing import AsyncIterator, Protocol, Sequence


class LLMClient(Protocol):
    async def generate(self, system_prompt: str, user_message: str) -> str:
        ...

    async def stream(self, system_prompt: str, user_message: str) -> AsyncIterator[str]:
        ...


class MockLLMClient:
    async def generate(self, system_prompt: str, user_message: str) -> str:
        return self._reply(user_message)

    async def stream(self, system_prompt: str, user_message: str) -> AsyncIterator[str]:
        reply = self._reply(user_message)
        for word in reply.split():
            yield word + " "

    @staticmethod
    def _reply(user_message: str) -> str:
        message = user_message.lower()
        if "merhaba" in message:
            return "Merhaba. Bugün neye odaklanmak istediğini birlikte belirleyelim."
        if "bugün" in message and "çalış" in message:
            return "Bugün mevcut odağımız olan nefes zamanlamasına devam edelim. Önce kısa bir drill, ardından normal freestyle yapalım."
        if "nefes" in message:
            return "Nefes alırken başını kaldırmak yerine gövdenle birlikte yana dönmeyi dene. Önce kısa mesafede kontrolü koruyalım."
        return "Anladım. Bunu öğrencinin mevcut hedefi ve son çalışmalarına göre birlikte değerlendirelim."
