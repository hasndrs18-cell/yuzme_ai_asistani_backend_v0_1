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

Health:

```text
GET http://127.0.0.1:8000/api/v1/health
```

WebSocket:

```text
ws://127.0.0.1:8000/ws/v1/assistant?student_id=demo-student
```

İlk aşamada STT, LLM ve TTS mock adapter'ları kullanılır. Gerçek sağlayıcılar adapter arkasından bağlanacaktır.
