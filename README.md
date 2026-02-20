# rnd-forge

База знаний и инструментарий для подготовки технологических описаний инновационных проектов.

## Зачем

Подготовка качественного описания технологии для фондов (Сколково и др.) — процесс, который можно систематизировать:

1. **Драфт** — AI генерирует структурированный черновик на основе имеющихся данных
2. **Клиент одобряет** — краткая версия показывает, что проект стоит развивать
3. **Полная версия** — детальное описание всех модулей, KPI, экономики
4. **Экспертная вычитка** — 2 предметных эксперта дают замечания
5. **Финальная версия** — с обработанными замечаниями и диаграммой процесса

Этот репозиторий содержит промпты, шаблоны, чеклисты и исследования для каждого этапа.

## Навигация

### [prompts/](prompts/) — Библиотека промптов

Воспроизводимый процесс от черновика до финальной версии.

| Промпт | Стадия | Назначение |
|--------|--------|-----------|
| [01-initial-draft.md](prompts/01-initial-draft.md) | Драфт / Полная версия | Генерация структурированного черновика |
| [02-expert-review-response.md](prompts/02-expert-review-response.md) | Экспертная вычитка | Обработка замечаний эксперта |
| [03-section-refinement.md](prompts/03-section-refinement.md) | Любая | Углублённая доработка конкретного раздела |
| [04-questionnaire-generation.md](prompts/04-questionnaire-generation.md) | Драфт / Полная версия | Генерация анкеты для сбора данных |
| [05-final-polish.md](prompts/05-final-polish.md) | Финальная версия | Вычитка на непротиворечивость и полноту |

История: [prompts/history/vivacrumb-session.md](prompts/history/vivacrumb-session.md) — разбор реальной сессии по VivaCrumb.

### [research/](research/) — Исследования

**Сколково:**
| Файл | Содержание |
|------|-----------|
| [overview.md](research/skolkovo/overview.md) | Общая справка, льготы, программы, контакты |
| [clusters.md](research/skolkovo/clusters.md) | 4 кластера и приоритеты (какой выбрать) |
| [evaluation-criteria.md](research/skolkovo/evaluation-criteria.md) | 4 критерия экспертизы + как под них писать |
| [application-process.md](research/skolkovo/application-process.md) | Этапы подачи: самостоятельно / Fast Track / МТК |
| [documents-required.md](research/skolkovo/documents-required.md) | Необходимые документы и шаблоны |

**Общее:**
| Файл | Содержание |
|------|-----------|
| [technology-description-principles.md](research/general/technology-description-principles.md) | Принципы написания описаний (из опыта VivaCrumb) |

### [templates/](templates/) — Шаблоны

| Шаблон | Назначение |
|--------|-----------|
| [technology-description.md](templates/technology-description.md) | Универсальный шаблон описания технологии (11 разделов) |
| [expert-questionnaire.md](templates/expert-questionnaire.md) | Анкета для предметного специалиста (мин + расширенная) |
| [skolkovo-application.md](templates/skolkovo-application.md) | Заявка в Сколково по 4 критериям экспертизы |

### [checklists/](checklists/) — Чеклисты

| Чеклист | Когда использовать |
|---------|-------------------|
| [before-expert-review.md](checklists/before-expert-review.md) | Перед отправкой описания эксперту |
| [after-expert-review.md](checklists/after-expert-review.md) | После получения замечаний |
| [skolkovo-readiness.md](checklists/skolkovo-readiness.md) | Перед подачей заявки в Сколково |
| [data-collection.md](checklists/data-collection.md) | Какие данные собрать с производства |

## Workflow

```
Стадия 1: ДРАФТ                    Стадия 2: ПОЛНАЯ ВЕРСИЯ
┌──────────────┐                    ┌──────────────┐
│ Сбор данных  │                    │ Детальное    │
│ AI-черновик  │──→ Клиент OK ──→  │ описание     │
│ Краткая      │                    │ всех модулей │
│ версия       │                    │ KPI, числа   │
└──────────────┘                    └──────┬───────┘
                                          │
                    ┌─────────────────────┘
                    ↓
Стадия 3: ЭКСПЕРТЫ                  Стадия 4: ФИНАЛ
┌──────────────┐                    ┌──────────────┐
│ Эксперт 1    │                    │ Обработка    │
│ Эксперт 2    │──→ Замечания ──→  │ + полировка  │
│ Вычитка      │                    │ + диаграмма  │
└──────────────┘                    └──────────────┘
```

## Проекты

| Проект | Стадия | Кластер Сколково | Документы |
|--------|--------|-----------------|-----------|
| VivaCrumb (clean-label shelf-life, хлебопечение) | 1→2 | Биомед / 6.6 | [Google Drive](https://drive.google.com/drive/u/0/folders/16K5c1MKNjj1_MUVmFQZxQoL1oQut8qRV) |
