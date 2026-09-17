# Yüzme AI Asistanı — Backend Çekirdeği

Bu depo, Yüzme AI Asistanı'nın ilk çalışan dikey dilimini içerir:

WebSocket → bağlam → güvenlik → niyet → LangGraph modu → karar → Türkçe yanıt

## Çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
uvicorn app.main:app --reload
```

## Kaynaklı AI yanıtları

Varsayılan yapılandırma `mock` sağlayıcıdır ve gerçek bilgi iddiasında bulunmaz. Kaynaklı AI yanıtlarını açmak için proje kökünde `.env` oluşturun. LLM için OpenAI-uyumlu bir endpoint, web araştırması için Tavily kullanılabilir:

```env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=...
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
RESEARCH_PROVIDER=tavily
RESEARCH_API_KEY=...
RESEARCH_TIMEOUT_SECONDS=4
RESEARCH_MAX_RESULTS=5
```

Asistan araştırma bulgularını sistem prompt'una kaynak URL'siyle birlikte alır, çelişkileri ve sınırlılıkları belirtir. Sağlayıcı veya araştırma servisi yanıt vermezse sistem kaynak uydurmaz ve tahmin yürütmek yerine bunu kullanıcıya bildirir. Tıbbi, sakatlık ve yüksek riskli performans kararları yine antrenör/sağlık profesyoneli tarafından değerlendirilmelidir.

Health:

```text
GET http://127.0.0.1:8000/api/v1/health
```

WebSocket:

```text
ws://127.0.0.1:8000/ws/v1/assistant?student_id=demo-student
```

İlk aşamada STT, LLM ve TTS mock adapter'ları kullanılır. Gerçek sağlayıcılar adapter arkasından bağlanacaktır.
