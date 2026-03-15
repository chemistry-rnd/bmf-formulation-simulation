# ScaleWithAI VC Chatbot — Implementation Plan

**Сайт**: `vc.aiqarus.ru`
**GCP проект**: `scalewithai-vc`
**Стек**: Cloud Run (Python/Node) + Firestore + Secret Manager + Firebase Hosting

---

## Архитектура

```
User → Chat UI (Firebase Hosting)
         ↓
    Cloud Run API (Router)
         ├── Tier 1: GPT-4o-mini (FAQ, простые вопросы)
         ├── Tier 2: Gemini 2.0 Flash (большой контекст)
         ├── Tier 3: Claude Code Session (сложные задачи)
         │     ├── Primary: WebSocket bridge → локальная машина
         │     └── Fallback: Vertex AI Claude API
         └── Vector Search: embeddings для knowledge base
```

### Routing Logic

```
1. Input → size check (>4000 tokens → trim or Gemini)
2. Input → keyword extraction (GPT-4o-mini: "дай 5 релевантных слов без сленга")
3. Keywords → vector search → context
4. Input + context → GPT-4o-mini → ответ
5. Validation (GPT-4o-mini): "ответ полный? нужен ли Claude?" → yes/no + confidence
6. Если нужен Claude:
   a. Проверить bridge → если online → Claude Code session
   b. Если offline → Vertex AI (Claude Sonnet)
   c. Если и Vertex fail → "Эксперт ответит в течение часа" + сохранить в Firestore
```

### Domain Constraint

Все промпты содержат системный контекст:
> "Ты консультант фонда ScaleWithAI VC. Мы инвестируем ТОЛЬКО в компании с производственным или
> хардварным ядром — НЕ чистое ПО. Примеры: заводы, инжиниринг, логистика с физическими активами,
> R&D с оборудованием. Если вопрос про чисто софтверный бизнес — вежливо объясни ограничение домена."

---

## Предустановленные сценарии (Chat Templates)

| # | Шаблон | Что делает | Tier |
|---|--------|-----------|------|
| 1 | Оценить компанию X | Запрашивает название/ИНН, анализирует по методике K1-K4 | 2-3 |
| 2 | Подобрать компании для покупки | Min 5 тегов (страна, отрасль, размер, статус, регион) с автокомплитом | 3 |
| 3 | Составить R&D план | Ожидаемый outcome vs стоимость вложений | 3 |
| 4 | Прогноз будущего для моей компании | Рынки, технологии, логистика — персонализированный | 3 |
| 5 | Тестовое задание для найма | Описание роли → план оценки + рыночная стоимость | 1-2 |

---

## Итерации

### Iteration 1 — MVP: Лендинг + FAQ-бот
**Цель**: рабочий сайт с простым чатом, деплой на `vc.aiqarus.ru`

**1.1 — Simple**
- [ ] Лендинг HTML (адаптация существующего ai-acquisition-landing.html)
- [ ] Chat UI: полноэкранное окно внизу, список готовых вопросов
- [ ] Cloud Run бэкенд: `/api/chat` endpoint
- [ ] GPT-4o-mini: отвечает на FAQ по знаниям фонда (hardcoded system prompt)
- [ ] Domain constraint в system prompt
- [ ] Firestore: сохранение сессий (session_id → messages[])
- [ ] Firebase Hosting: деплой статики
- [ ] DNS: обновить A-запись vc.aiqarus.ru → Firebase
- [ ] SSL: автоматический через Firebase

**1.2 — Mobile-friendly**
- [ ] Responsive chat UI (мобильный = полноэкранный чат)
- [ ] Touch-friendly кнопки шаблонов
- [ ] Loading states, typing indicator
- [ ] Markdown → HTML рендеринг ответов (marked.js)

**Деплой**: v0.1 на продакшн

---

### Iteration 2 — Smart Routing + Validation
**Цель**: бот понимает когда не справляется, и готовится к тяжёлому tier

**2.1 — Simple**
- [ ] Input size evaluation (token count)
- [ ] Validation step: после ответа GPT-4o-mini → "ответ полный?" (самопроверка)
- [ ] Если не полный → показать юзеру "Нужен глубокий анализ. Запустить?" (кнопка)
- [ ] Rate limiting: 10 запросов/сессия для анонимов, потом → "оставьте email"
- [ ] Email capture → Firestore (leads collection)
- [ ] Keyword extraction: перед vector search вытаскиваем нормализованные термины

**2.2 — Mobile-friendly**
- [ ] Плавные transitions между "простой ответ" → "нужен анализ"
- [ ] Email input UX
- [ ] Skeleton loaders

**Деплой**: v0.2 на продакшн

---

### Iteration 3 — Claude Code Bridge
**Цель**: тяжёлые задачи уходят на Claude Code через локальную машину

**3.1 — Simple**
- [ ] WebSocket relay service на Cloud Run (принимает запрос, держит соединение)
- [ ] Локальный bridge-agent: скрипт на маке, подключается к relay через WS
- [ ] Bridge получает задачу → запускает Claude Code session → стримит результат обратно
- [ ] Auth: API key для bridge (в Secret Manager)
- [ ] Fallback: если bridge offline >15 сек → Vertex AI (Claude Sonnet)
- [ ] Queue: Firestore очередь задач, обработка по одной
- [ ] SSE стриминг ответа в chat UI (токены появляются по мере генерации)

**3.2 — Mobile-friendly**
- [ ] Progress indicator: "Эксперт анализирует... ~2 мин"
- [ ] Partial results streaming в мобильном view
- [ ] "Получить результат на email" для длинных ответов

**Деплой**: v0.3 на продакшн

---

### Iteration 4 — Vector Search + Knowledge Base
**Цель**: бот знает про фонд, методику, кейсы — не только из промпта

**4.1 — Simple**
- [ ] Knowledge base: markdown файлы → embeddings (OpenAI ada-002 или Vertex)
- [ ] Firestore или Pinecone для хранения векторов
- [ ] Pre-search: GPT-4o-mini извлекает релевантные слова (не зависим от сленга юзера)
- [ ] Контекст из vector search → подаётся в LLM вместе с вопросом (RAG)
- [ ] Источники: методика K1-K4, примеры оценок, отраслевые данные

**4.2 — Mobile-friendly**
- [ ] "Источники" блок под ответом (откуда бот взял информацию)
- [ ] Expandable sections для длинных ответов

**Деплой**: v0.4 на продакшн

---

### Iteration 5 — Structured Queries (Templates)
**Цель**: шаблонные сценарии с UI формами

**5.1 — Simple**
- [ ] Template 1: "Оценить компанию" → форма: название/ИНН/описание → структурированный отчёт
- [ ] Template 2: "Подобрать компании" → tag input (min 5 тегов), autocomplete из справочника
- [ ] Template 3: "R&D план" → форма: отрасль, размер, текущие проблемы → план + ROI
- [ ] Template 4: "Прогноз" → форма: описание компании → персонализированный прогноз
- [ ] Template 5: "Тестовое задание" → форма: роль, задачи → задание + рыночная вилка
- [ ] Output: всегда MD → styled HTML с заголовками, таблицами, графиками
- [ ] "Скачать отчёт" кнопка (генерация PDF или ссылка на instant-publish)

**5.2 — Mobile-friendly**
- [ ] Step-by-step wizard для каждого template (не всё на одном экране)
- [ ] Tag input с мобильным autocomplete
- [ ] Swipe-friendly отчёты

**Деплой**: v0.5 на продакшн

---

### Iteration 6 — Polish: Analytics, Cache, Feedback
**Цель**: production-grade качество

**6.1 — Simple**
- [ ] Analytics: Firestore events → какие вопросы, какой tier, время ответа
- [ ] Cache: Redis/Firestore cache для повторяющихся вопросов (TTL 24h)
- [ ] Feedback: кнопки "полезно / не полезно" → сохранение в Firestore
- [ ] Auth (опционально): Google Sign-In для premium features
- [ ] Budget monitoring: Cloud Monitoring alerts на API spend
- [ ] Error tracking: structured logging в Cloud Run

**6.2 — Mobile-friendly**
- [ ] Feedback UX (slide-up sheet)
- [ ] Offline indicator

**Деплой**: v1.0 на продакшн

---

## Стоимость (оценка на Free Trial)

| Компонент | Стоимость/мес |
|-----------|---------------|
| Firebase Hosting | $0 (free tier) |
| Cloud Run | ~$2-5 (scale to zero) |
| Firestore | ~$0-1 (small volume) |
| GPT-4o-mini | ~$1-5 (зависит от трафика) |
| Gemini Flash | ~$0-2 |
| Vertex AI Claude (fallback) | ~$0-5 (только когда bridge offline) |
| Secret Manager | $0 (free tier) |
| **Итого** | **~$3-18/мес** |

Покрывается Free Trial ($300) на 16+ месяцев.

---

## Технические решения

### Chat UI
- Vanilla JS + CSS (без фреймворков, как лендинг)
- marked.js для MD→HTML
- SSE для стриминга
- localStorage для session_id

### Backend (Cloud Run)
- Python (FastAPI) или Node (Express)
- Выбор: **Python** — лучше для AI/ML интеграций, OpenAI SDK, embeddings
- Docker → Artifact Registry → Cloud Run

### Bridge (локальная машина)
- Node.js скрипт, запускается как daemon
- WebSocket подключение к Cloud Run relay
- Запускает `claude --dangerously-skip-permissions` с промптом
- Стримит stdout обратно через WS

### Output Format
- Всё в Markdown
- Frontend рендерит в styled HTML
- Таблицы, заголовки, списки, code blocks
- Для длинных отчётов — instant-publish ссылка
