from typing import Protocol


class STTClient(Protocol):
    async def transcribe(self, audio: bytes) -> str:
        ...


class MockSTTClient:
    async def transcribe(self, audio: bytes) -> str:
        # Gerçek STT sağlayıcısı bir sonraki aşamada bağlanacak.
        return ""
