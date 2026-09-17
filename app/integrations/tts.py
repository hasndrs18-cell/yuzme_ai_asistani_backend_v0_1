from typing import AsyncIterator, Protocol


class TTSClient(Protocol):
    async def synthesize(self, text: str) -> AsyncIterator[bytes]:
        ...


class MockTTSClient:
    async def synthesize(self, text: str) -> AsyncIterator[bytes]:
        # Gerçek TTS sağlayıcısı bir sonraki aşamada bağlanacak.
        yield text.encode("utf-8")
