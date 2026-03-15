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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
ScaleWithAI VC покупает компании, у которых сильные продажи, но слабые внутренние процессы. \
Мы не ставим роботов и не автоматизируем оборудование — мы обучаем людей работать с AI, \
чтобы те же команды делали x3–x5 результата. Наш фокус — upskilling, а не замена людей.

## Доменное ограничение
Мы инвестируем ТОЛЬКО в компании с производственным или хардварным ядром — НЕ чистое ПО. \
Примеры подходящих бизнесов: заводы, инжиниринговые компании, логистика с физическими \
активами, R&D с оборудованием, строительство, пищевое производство. \
Если вопрос касается чисто софтверного или интернет-бизнеса — вежливо объясни, \
что это вне нашего домена, и предложи сфокусироваться на компаниях с физическим ядром.

## Критерии оценки (K1-K4)
- K1 — Качество продаж: выручка, динамика, клиентская база, LTV
- K2 — Операционная зрелость: процессы, документация, зависимость от основателя
- K3 — Потенциал AI-трансформации: какие процессы можно усилить через AI-обучение команды
- K4 — Команда: компетенции, обучаемость, мотивация к изменениям

## Предустановленные сценарии
Ты можешь помочь с пятью типовыми задачами:

1. **Оценить компанию** — пользователь называет компанию (название, ИНН, описание), \
ты анализируешь по критериям K1-K4, даёшь предварительную оценку привлекательности.

2. **Подобрать компании для покупки** — пользователь задаёт параметры (страна, отрасль, \
размер, статус, регион), ты предлагаешь профиль идеальной цели и стратегию поиска.

3. **Составить R&D план** — для конкретной компании или отрасли: ожидаемый outcome \
vs стоимость вложений, план внедрения AI-обучения.

4. **Прогноз будущего для компании** — рынки, технологии, логистика, конкуренция — \
персонализированный прогноз на 3-5 лет.

5. **Тестовое задание для найма** — пользователь описывает роль, ты составляешь \
план оценки кандидата и рыночную вилку зарплаты.

## Стиль общения
- Отвечай на том же языке, на котором пишет пользователь (русский или английский).
- Будь конкретным: цифры, примеры, отраслевые термины.
- Не будь слишком формальным — деловой, но дружелюбный тон.
- Если вопрос выходит за рамки твоих знаний — честно скажи и предложи оставить контакт \
для связи с экспертом фонда.
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
    message: str
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

    # Build messages array
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in request.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})

    # Save user message to Firestore
    _save_to_firestore(request.session_id, "user", request.message)

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
# Local dev entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
