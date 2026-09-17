from typing import AsyncIterator, Protocol

import httpx


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


class OpenAICompatibleLLMClient:
    """Small provider adapter for OpenAI-compatible chat completion APIs."""

    def __init__(self, api_key: str, base_url: str, model: str, timeout_seconds: float = 20.0) -> None:
        self.api_key = api_key
        self.endpoint = f"{base_url.rstrip('/')}/chat/completions"
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def generate(self, system_prompt: str, user_message: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "max_tokens": 900,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("LLM provider boş yanıt döndürdü")
        return content.strip()

    async def stream(self, system_prompt: str, user_message: str) -> AsyncIterator[str]:
        yield await self.generate(system_prompt, user_message)
