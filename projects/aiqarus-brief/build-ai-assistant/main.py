"""
aiqarus Brief — FastAPI backend.
Serves the brief form and accepts submissions.
"""

import os
import json
import hashlib
import logging
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("aiqarus-brief")

GCP_PROJECT = os.getenv("GCP_PROJECT", "scalewithai-vc")
FIRESTORE_ENABLED = os.getenv("FIRESTORE_ENABLED", "false").lower() == "true"
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://build-ai-assistant.aiqarus.ru,http://localhost:3000,http://localhost:8080,http://127.0.0.1:5500",
).split(",")

NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "vladimir@skillset.ae")

# ---------------------------------------------------------------------------
# Firestore
# ---------------------------------------------------------------------------
_firestore_client = None


def _get_firestore():
    global _firestore_client
    if _firestore_client is None:
        from google.cloud import firestore
        _firestore_client = firestore.Client(project=GCP_PROJECT)
    return _firestore_client


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="aiqarus Brief", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class BriefSubmission(BaseModel):
    # Step 1
    main_task: Optional[str] = None
    main_task_custom: Optional[str] = None
    # Step 2
    platforms: Optional[list[str]] = []
    daily_users: Optional[str] = None
    language: Optional[str] = None
    # Step 3
    docs_count: Optional[str] = None
    pages_count: Optional[str] = None
    docs_description: Optional[str] = None
    knowledge_sources: Optional[list[str]] = []
    integrations_needed: Optional[list[str]] = []
    # Step 4 — dynamic
    sales_qualifying: Optional[str] = None
    sales_action: Optional[str] = None
    sales_tone: Optional[str] = None
    support_fallback: Optional[str] = None
    support_top_questions: Optional[str] = None
    routing_entity: Optional[str] = None
    routing_criteria: Optional[str] = None
    routing_options_count: Optional[str] = None
    automation_processes: Optional[str] = None
    automation_frequency: Optional[str] = None
    custom_scenario: Optional[str] = None
    # Step 4 — safety & SOS
    safety_rules: Optional[list[str]] = []
    custom_restrictions: Optional[str] = None
    sos_triggers: Optional[list[str]] = []
    sos_action: Optional[str] = None
    escalation_target: Optional[str] = None
    # Step 5
    business_description: Optional[str] = None
    problem_description: Optional[str] = None
    current_process: Optional[str] = None
    # Step 6
    timeline: Optional[str] = None
    additional_notes: Optional[str] = None
    # Step 7
    contact_name: Optional[str] = None
    contact_company: Optional[str] = None
    contact_email: Optional[str] = None
    contact_telegram: Optional[str] = None
    contact_method: Optional[str] = None
    # Meta
    _brief_id: Optional[str] = None
    _submitted_at: Optional[str] = None
    _files: Optional[list[dict]] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "aiqarus-brief", "version": "0.1.0"}


@app.post("/api/brief")
async def submit_brief(brief: BriefSubmission):
    """Accept a brief submission and store it."""
    now = datetime.now(timezone.utc).isoformat()
    brief_data = brief.model_dump()
    brief_data["submitted_at"] = now

    logger.info("Brief received: %s from %s (%s)",
                brief_data.get("_brief_id", "?"),
                brief_data.get("contact_name", "?"),
                brief_data.get("contact_email", "?"))

    if FIRESTORE_ENABLED:
        try:
            db = _get_firestore()
            doc_id = brief_data.get("_brief_id") or now.replace(":", "-")
            db.collection("briefs").document(doc_id).set(brief_data)
            logger.info("Brief saved to Firestore: %s", doc_id)
            # Mark invite as submitted if present
            invite_id = brief_data.get("_invite_id")
            if invite_id:
                try:
                    db.collection("invites").document(invite_id).update({
                        "submitted": True,
                        "submitted_at": now,
                        "brief_id": doc_id,
                    })
                except Exception:
                    pass
        except Exception as exc:
            logger.error("Firestore save failed: %s", exc)
    else:
        logger.info("Brief data (Firestore disabled): %s", json.dumps(brief_data, ensure_ascii=False)[:500])

    return {
        "status": "ok",
        "brief_id": brief_data.get("_brief_id"),
        "message": "Бриф принят. Свяжемся в течение 1 рабочего дня.",
    }


# ---------------------------------------------------------------------------
# Voice auto-correct (reuse from vc-site)
# ---------------------------------------------------------------------------
class CorrectRequest(BaseModel):
    text: str


@app.post("/api/correct")
async def correct_speech(request: CorrectRequest):
    """Fix speech recognition errors using GPT-4o-mini."""
    try:
        from openai import AsyncOpenAI

        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            resp = client.access_secret_version(
                request={"name": f"projects/{GCP_PROJECT}/secrets/OPENAI_API_KEY/versions/latest"}
            )
            key = resp.payload.data.decode("UTF-8").strip()

        ai = AsyncOpenAI(api_key=key)
        resp = await ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "Ты исправляешь ошибки распознавания речи. "
                    "Исправь контекстуальные ошибки: слова, похожие по звучанию но неправильные по смыслу. "
                    "Сохрани стиль и смысл оригинала. Не добавляй ничего нового. "
                    "Верни только исправленный текст."
                )},
                {"role": "user", "content": request.text},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        corrected = resp.choices[0].message.content.strip()
        return {"corrected": corrected, "original": request.text}
    except Exception as exc:
        logger.error("Correct API error: %s", exc)
        return {"corrected": request.text, "original": request.text}


# ---------------------------------------------------------------------------
# Invite links — short URLs with prefilled data
# ---------------------------------------------------------------------------
class InviteRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    telegram: Optional[str] = None
    phone: Optional[str] = None
    task: Optional[str] = None      # sales, support, routing, automation, custom
    platform: Optional[str] = None  # telegram, website, etc. (comma-separated)
    note: Optional[str] = None      # internal note, not in URL


def _make_invite_code(seed: str) -> str:
    """4-char short code from seed."""
    raw = f"{seed}:{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:6]


@app.post("/api/invite")
async def create_invite(req: InviteRequest):
    """Create a short invite link with prefilled data."""
    code = _make_invite_code(req.email or req.name or "anon")

    # Build URL params (only non-empty)
    params = {}
    if req.name: params["name"] = req.name
    if req.email: params["email"] = req.email
    if req.company: params["company"] = req.company
    if req.telegram: params["telegram"] = req.telegram
    elif req.phone: params["phone"] = req.phone
    if req.task: params["task"] = req.task
    if req.platform: params["platform"] = req.platform
    params["inv"] = code

    full_url = "/?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    invite_doc = {
        "code": code,
        "params": params,
        "full_url": full_url,
        "name": req.name,
        "email": req.email,
        "company": req.company,
        "note": req.note,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "opened": False,
        "submitted": False,
    }

    if FIRESTORE_ENABLED:
        try:
            db = _get_firestore()
            db.collection("invites").document(code).set(invite_doc)
            logger.info("Invite created: /i/%s → %s (%s)", code, req.name, req.email)
        except Exception as exc:
            logger.error("Invite save failed: %s", exc)
    else:
        logger.info("Invite (no Firestore): /i/%s → %s", code, full_url)

    return {
        "code": code,
        "short_url": f"/i/{code}",
        "full_url": full_url,
    }


@app.get("/i/{code}")
async def redirect_invite(code: str):
    """Redirect short invite URL to form with prefilled params."""
    if FIRESTORE_ENABLED:
        try:
            db = _get_firestore()
            doc = db.collection("invites").document(code).get()
            if doc.exists:
                data = doc.to_dict()
                # Mark as opened
                db.collection("invites").document(code).update({
                    "opened": True,
                    "opened_at": datetime.now(timezone.utc).isoformat(),
                })
                full_url = data.get("full_url", "/")
                return RedirectResponse(url=full_url, status_code=302)
        except Exception as exc:
            logger.error("Invite lookup failed: %s", exc)

    # Fallback: redirect to form with just inv param
    return RedirectResponse(url=f"/?inv={code}", status_code=302)


@app.get("/api/invites")
async def list_invites():
    """List all invites (for admin use)."""
    if not FIRESTORE_ENABLED:
        return {"invites": [], "note": "Firestore disabled"}
    try:
        db = _get_firestore()
        docs = db.collection("invites").order_by("created_at", direction="DESCENDING").limit(50).stream()
        invites = []
        for doc in docs:
            d = doc.to_dict()
            invites.append({
                "code": d.get("code"),
                "name": d.get("name"),
                "email": d.get("email"),
                "company": d.get("company"),
                "short_url": f"/i/{d.get('code')}",
                "opened": d.get("opened", False),
                "submitted": d.get("submitted", False),
                "created_at": d.get("created_at"),
            })
        return {"invites": invites}
    except Exception as exc:
        logger.error("List invites failed: %s", exc)
        return {"invites": [], "error": str(exc)}


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    @app.get("/")
    async def serve_index():
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8081")))
