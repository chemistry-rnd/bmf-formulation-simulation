"""
ScaleWithAI VC Chatbot — FastAPI backend.
Tier 1 MVP: GPT-4o-mini with hardcoded system prompt, SSE streaming, Firestore sessions.
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from openai import AsyncOpenAI

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("scalewithai")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
GCP_PROJECT = os.getenv("GCP_PROJECT", "scalewithai-vc")
SECRET_NAME = "OPENAI_API_KEY"
FIRESTORE_ENABLED = os.getenv("FIRESTORE_ENABLED", "false").lower() == "true"
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://vc.aiqarus.ru,http://localhost:3000,http://localhost:8080,http://127.0.0.1:5500",
).split(",")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
Ты — AI-консультант инвестиционного фонда ScaleWithAI VC.

## О фонде
ScaleWithAI VC покупает компании, где основная стоимость создаётся людьми, а не оборудованием — \
и кратно повышает выработку на человека через AI-обучение команд.

## Наш фокус
Бизнесы с большими бэк-офисами, типовыми «экранными» ролями (бухгалтеры, планировщики, \
снабженцы, документоведы, HR, рекрутеры, инженеры-проектировщики). Мы обучаем этих людей \
работать с AI-инструментами — и один человек начинает делать работу, которую раньше делали 3–5.

## Не наш профиль
- Чисто софтверные компании (SaaS, маркетплейсы, мобильные приложения без физ. операций).
- Робототехника и промышленная автоматизация оборудования — мы видим потенциал этого \
направления, но наша экспертиза в другом: в обучении людей, а не в замене станков.

## География
Россия, США, Европа, Индия (основные); Бразилия, Турция, Мексика (расширение).

## Партнёры
Евгений Протасенко и 271 Capital Advisory (London) — financial & strategic advisory for tech. \
Евгений — выпускник МФТИ, CFA, лектор AWS Startup Academy, CEO 271 Capital (выросла из 271.vc).

## Команда
Группа инженеров из России с опытом на стыке технологий и бизнеса — люди, которые \
одинаково свободно разбираются в архитектуре AI-систем и в операционке производственных компаний.

## Методика оценки (K1–K4)
- K1: Доля ФОТ в себестоимости (>40% = высокий рычаг от AI-обучения)
- K2: Плотность типовых ролей (≥10 человек на одной роли = масштабируемое обучение)
- K3: Доля «экранной» работы (≥30% штата за компьютерами = быстрый AI-эффект)
- K4: Мобильность интеллектуального капитала (знания в головах, онбординг >3 мес = возможность)

## Модель создания стоимости
Покупаем компанию с сильными продажами но ручными процессами → за 2–6 недель обучаем \
«экранных» сотрудников работать с AI → выработка на человека растёт ×2–5 → payback обучения \
2–3 месяца → знания фиксируются в системах, а не в головах → масштабируем модель.

## Целевые параметры сделки
- Размер компании: 30–500 сотрудников
- Выручка: $1M–$50M
- Доля «экранных» ролей: ≥30% штата
- Доля ФОТ в себестоимости: >40%
- Отрасли: manufacturing с большим бэк-офисом, BPO, логистика, инжиниринг, рекрутинг, \
бухгалтерия, колл-центры, юр. бюро
- НЕ берём: чистое ПО, hardware/robotics, компании без «экранных» ролей

## Процесс сделки
1. Скоринг — оцениваем компанию по K1–K4 (можно за 1 день по открытым данным)
2. Deep dive — штатное расписание, финансы, AI-индекс (1–2 недели)
3. Сделка — покупка из банкротства, вход в капитал, management buyout. Ключевое: операционный контроль
4. AI-обучение — 2–6 недель, начиная с ролей с максимальным ROI
5. Масштабирование — тиражирование модели на следующие активы
6. Выход — 3–5 лет: продажа стратегу, IPO или дивидендная модель

## Предустановленные сценарии
Ты можешь помочь с девятью типовыми задачами:

### Для аналитиков фонда
1. **Оценить компанию по K1–K4** — попроси: название/ИНН, отрасль, штат, выручка, \
доля ФОТ (или «сколько на людей vs оборудование»). Не обязательно всё — даже частичная \
информация позволит сделать предварительную оценку. Анализируй штатное расписание по шкале \
Карпатого, считай AI-индекс, экономию на ФОТ и payback.
2. **Подобрать компании для покупки** — пользователь задаёт параметры (страна, отрасль, \
размер, статус, регион), ты предлагаешь профиль идеальной цели и стратегию поиска.
3. **Составить R&D план трансформации** — берёшь профиль компании → формируешь план \
AI-обучения по ролям в порядке ROI → считаешь outcome vs затраты → таймлайн.

### Для владельцев бизнеса
4. **Хочу продать свой бизнес** — спроси: отрасль, штат, выручка, доля «экранных» ролей, \
текущая ситуация (distress/growth/exit). Прогони через K1–K4, дай предварительную оценку \
fit + опиши процесс сделки.
5. **Рассчитать эффект от AI-обучения** — AI-калькулятор: пользователь вводит роли + \
кол-во + зарплаты → ты считаешь AI-индекс каждой роли по Карпатому, потенциал роста \
выработки, экономию на ФОТ, стоимость обучения и payback.
6. **Прогноз будущего для компании** — рынки, технологии, конкуренция — персонализированный \
прогноз: какие роли AI усилит первыми, как подготовиться.

### Для инвесторов и партнёров
7. **Как стать инвестором фонда** — объясни модель (GP/LP), тезис, географию, \
процесс входа. Если нужно больше деталей — предложи оставить контакт.
8. **Чем отличаемся от PE / консалтинга** — не консалтинг (мы покупаем), не классический PE \
(мы обучаем людей AI, а не режем косты), не робототехника (мы про людей).

### Для найма
9. **Как найти инженеров на стыке бизнеса и AI** — опиши идеальный профиль, где искать \
(МФТИ, ex-консалтинг+tech, AI-стартапы с industrial клиентами), как оценить (кейс: \
дать компанию → сделать K1–K4 скоринг + план AI-обучения).

## Стиль общения
- Отвечай на том же языке, на котором пишет пользователь (русский или английский).
- Будь конкретным: цифры, примеры, отраслевые термины.
- Не будь слишком формальным — деловой, но дружелюбный тон.
- Если вопрос про чисто софтверный бизнес — вежливо объясни что это не наш домен.
- Если вопрос про роботов/hardware — объясни разграничение (мы за, но другая экспертиза).
- Если не знаешь ответ — честно скажи и предложи оставить контакт для связи с командой.
- Структурируй ответы: заголовки, списки, таблицы где уместно (Markdown).
"""


# ---------------------------------------------------------------------------
# OpenAI API key retrieval
# ---------------------------------------------------------------------------
def _get_openai_key() -> str:
    """Fetch OPENAI_API_KEY: Secret Manager first, then env var fallback."""
    # 1. Try env var (fast path for local dev)
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        logger.info("Using OPENAI_API_KEY from environment variable")
        return env_key

    # 2. Try Google Secret Manager
    try:
        from google.cloud import secretmanager  # noqa: delayed import

        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{GCP_PROJECT}/secrets/{SECRET_NAME}/versions/latest"
        response = client.access_secret_version(request={"name": secret_path})
        key = response.payload.data.decode("UTF-8").strip()
        logger.info("Loaded OPENAI_API_KEY from Secret Manager")
        return key
    except Exception as exc:
        logger.error("Failed to fetch secret from Secret Manager: %s", exc)
        raise RuntimeError(
            "OPENAI_API_KEY not found. Set it as an env var or configure Secret Manager."
        ) from exc


# ---------------------------------------------------------------------------
# Firestore helpers
# ---------------------------------------------------------------------------
_firestore_client = None


def _get_firestore():
    global _firestore_client
    if _firestore_client is None:
        from google.cloud import firestore  # noqa: delayed import

        _firestore_client = firestore.Client(project=GCP_PROJECT)
    return _firestore_client


def _save_to_firestore(session_id: str, role: str, content: str):
    """Append a message to the Firestore chat session."""
    if not FIRESTORE_ENABLED:
        return
    try:
        db = _get_firestore()
        doc_ref = db.collection("chat_sessions").document(session_id)
        doc = doc_ref.get()
        if doc.exists:
            messages = doc.to_dict().get("messages", [])
        else:
            messages = []
        messages.append(
            {"role": role, "content": content, "ts": datetime.now(timezone.utc).isoformat()}
        )
        doc_ref.set(
            {"messages": messages, "updated_at": datetime.now(timezone.utc).isoformat()},
            merge=True,
        )
    except Exception as exc:
        logger.warning("Firestore save failed (non-fatal): %s", exc)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="ScaleWithAI VC Chatbot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-init OpenAI client (key fetched at first request, not at import time)
_openai_client: Optional[AsyncOpenAI] = None


def _get_openai() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=_get_openai_key())
    return _openai_client


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: Optional[str] = None
    messages: list[ChatMessage] = []
    history: list[ChatMessage] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "scalewithai-vc-chatbot", "version": "0.1.0"}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Stream a chat completion response via SSE."""

    client = _get_openai()

    # Support both formats: {message, history} and {messages}
    msg_list = request.messages or request.history
    user_message = request.message or (msg_list[-1].content if msg_list and msg_list[-1].role == "user" else "")

    # Build messages array
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in msg_list[:-1] if not request.message else msg_list:
        messages.append({"role": msg.role, "content": msg.content})
    if request.message:
        messages.append({"role": "user", "content": request.message})
    elif msg_list and msg_list[-1].role == "user":
        messages.append({"role": "user", "content": msg_list[-1].content})

    # Save user message to Firestore
    _save_to_firestore(request.session_id, "user", user_message)

    async def event_generator():
        full_response = ""
        try:
            stream = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2048,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    token = delta.content
                    full_response += token
                    yield {"event": "message", "data": json.dumps({"token": token})}

            # Signal completion
            yield {
                "event": "done",
                "data": json.dumps({"full_response": full_response}),
            }

            # Save assistant response to Firestore
            _save_to_firestore(request.session_id, "assistant", full_response)

        except Exception as exc:
            logger.error("OpenAI streaming error: %s", exc)
            yield {
                "event": "error",
                "data": json.dumps({"error": str(exc)}),
            }

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# Static files — serve frontend from /static directory
# ---------------------------------------------------------------------------
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    from fastapi.responses import FileResponse

    # Serve index.html at root
    @app.get("/")
    async def serve_index():
        return FileResponse(STATIC_DIR / "index.html")

    # Serve all other static files
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


# ---------------------------------------------------------------------------
# Local dev entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
