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

## Vercel ve Google OAuth

Bu repository'nin Vercel ayarı `vercel.json` ile `frontend` klasörünü Next.js uygulaması olarak build eder. FastAPI backend'i WebSocket ve OAuth callback kullandığı için Vercel frontend'inden ayrı bir backend servisi olarak yayınlanmalıdır.

Vercel Project Settings > Environment Variables içine backend'in HTTPS adresiyle şu public değerleri ekleyin:

```env
NEXT_PUBLIC_BACKEND_URL=https://api.example.com
NEXT_PUBLIC_WS_URL=wss://api.example.com/ws/chat
NEXT_PUBLIC_GOOGLE_AUTH_URL=https://api.example.com/api/v1/auth/google
```

Backend servisine ise `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` ve `FRONTEND_URL` değerlerini ekleyin. Google Cloud Console'da Authorized redirect URI tam olarak `https://api.example.com/api/v1/auth/google/callback`, frontend origin de Vercel domain'i olmalıdır. Sadece frontend'i Vercel'e göndermek, `localhost:8000` üzerindeki backend'i internete açmaz.

Health:

```text
GET http://127.0.0.1:8000/api/v1/health
```

WebSocket:

```text
ws://127.0.0.1:8000/ws/v1/assistant?student_id=demo-student
```

İlk aşamada STT, LLM ve TTS mock adapter'ları kullanılır. Gerçek sağlayıcılar adapter arkasından bağlanacaktır.
