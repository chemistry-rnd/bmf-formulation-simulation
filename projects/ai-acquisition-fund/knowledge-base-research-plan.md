# План сбора knowledge base для ScaleWithAI VC

**Дата**: 2026-03-15
**Источник**: knowledge-base-collection-brief.md
**География**: Россия, США, Европа, Индия

---

## Обзор: 6 блоков данных × 4 географии

| # | Блок | RU | US | EU | IN | Приоритет |
|---|------|----|----|----|----|-----------|
| 1 | Методика фонда | из репо | из репо | из репо | из репо | P0 |
| 2 | Distressed / банкротства | fedresurs.ru | PACER, BankruptcyData | EU Insolvency registers | NCLT, IBC cases | P1 |
| 3 | Бизнесы на продажу | biztorg, bizzona, avito | BizBuySell, BizQuest | DealRoom, BusinessesForSale.com | IndiaBizForSale, SMEConnect | P2 |
| 4 | Зарплаты по ролям | hh.ru API | BLS, Glassdoor, Levels.fyi | Eurostat, Glassdoor EU | Naukri, PayScale India | P1 |
| 5 | Отраслевые бенчмарки | Росстат, ЕМИСС | BLS, Census, FRED | Eurostat, OECD | MoSPI, RBI data | P2 |
| 6 | Кейсы AI-обучения | Хабр, vc.ru | McKinsey, HBR, Deloitte | BCG, EU AI reports | NASSCOM, Indian case studies | P1 |

---

## Блок 1: Методика фонда (P0 — первый)

**Источники**: файлы в репозитории
- `projects/ai-acquisition-landing.html` — лендинг (тезис, K1–K4, примеры, сегменты)
- `projects/ai-acquisition-fund/scalewithai-vc-chatbot-implementation-plan.md` — архитектура, сценарии

**Задача**: нарезать на chunks 500–1000 токенов с метаданными.

**Шаги**:
1. Извлечь текстовый контент из HTML-лендинга (без разметки)
2. Разбить на смысловые блоки:
   - Инвестиционный тезис (зачем покупаем, что ищем)
   - Модель Карпатого (шкала 0–10, три зоны)
   - Методика оценки (5 шагов: штатное → баллы → индекс → кластеры → экономика)
   - K1–K4 критерии (каждый — отдельный chunk)
   - Пример скоринга (производство пластика)
   - Пример оценки (120 человек)
   - Целевые сегменты (каждый — отдельный chunk)
   - Процесс (4 фазы)
   - Сценарии чатбота (5 шаблонов)
3. Каждый chunk → MD-файл с метаданными

**Время**: ~1 час
**Результат**: `knowledge-base/methodology/` — 15–20 файлов

---

## Блок 2: Distressed-активы и банкротства (P1)

### 2.1 Россия — fedresurs.ru

**Что парсить**:
- Название компании, ИНН
- ОКВЭД (фильтр: секции B, C, D, E, F, G (кроме 62.xx, 63.xx), H, J (кроме 62.xx, 63.xx))
- Регион
- Стадия банкротства (наблюдение, конкурсное производство, торги)
- Дата публикации, ссылка

**Подход**:
- fedresurs.ru имеет anti-bot → использовать Playwright MCP (профиль skillset)
- Альтернатива: поиск через API (если есть) или ручной экспорт за последние 6 мес.
- Фильтр: только производство, инжиниринг, логистика с физ. активами

**Объём**: ~100–200 компаний
**Время**: 2–3 часа (с учётом anti-bot)

### 2.2 США — публичные банкротства

**Источники**:
- **PACER** (pacer.uscourts.gov) — федеральный реестр банкротств, Chapter 7/11
- **BankruptcyData.com** (Reorg Research) — аналитика по крупным банкротствам
- **SEC EDGAR** — filing 10-K, 8-K для публичных компаний в distress
- **CourtListener** (free.law) — бесплатный доступ к части court records

**Что собирать**:
- Company name, EIN/CIK
- Industry (NAICS codes — filter: 31–33 Manufacturing, 48–49 Transportation, 23 Construction, 54 Professional Services with physical ops)
- State / region
- Chapter (7 = liquidation, 11 = reorganization)
- Filing date, link
- Revenue / employees (если доступно)

**Подход**:
- Web search по свежим Chapter 11 filings (manufacturing, engineering, services)
- BankruptcyData.com — бесплатный tier даёт заголовки и базовые данные
- SEC EDGAR full-text search: "chapter 11" + industry filters

**Объём**: ~50–100 компаний
**Время**: 2–3 часа

### 2.3 Европа — insolvency registers

**Источники**:
- **EU Insolvency Registers Interconnection** (e-justice.europa.eu) — агрегатор по странам
- **Companies House (UK)** — insolvency list, бесплатный API
- **Handelsregister (DE)** — insolvenzbekanntmachungen.de
- **Infogreffe (FR)** — procédures collectives
- **European Business Register** — cross-border данные

**Что собирать**:
- Company name, registration number
- Country, industry (NACE codes — filter: same logic as ОКВЭД)
- Insolvency type (restructuring / liquidation)
- Date, link
- Employee count / revenue (если есть)

**Фокус стран**: UK, Germany, France, Netherlands, Poland (наибольшая база manufacturing)

**Подход**:
- Companies House API (UK) — бесплатный, хорошо документирован
- insolvenzbekanntmachungen.de (DE) — парсинг
- e-justice.europa.eu — поиск по странам

**Объём**: ~50–100 компаний
**Время**: 3–4 часа

### 2.4 Индия — NCLT / IBC cases

**Источники**:
- **NCLT** (nclt.gov.in) — National Company Law Tribunal, реестр IBC (Insolvency and Bankruptcy Code) дел
- **IBBI** (ibbi.gov.in) — Insolvency and Bankruptcy Board of India, публикует quarterly reports + списки CIRP/liquidation
- **Tofler / Zauba Corp** — данные о компаниях (MCA filings)

**Что собирать**:
- Company name, CIN (Corporate Identity Number)
- Industry (NIC codes — filter: manufacturing, engineering, logistics)
- State
- IBC stage (CIRP, liquidation, resolution)
- Date, link
- Revenue / employees (из Tofler если доступно)

**Подход**:
- IBBI публикует CSV/PDF отчёты quarterly — скачать и распарсить
- nclt.gov.in — ограниченный поиск, лучше через IBBI aggregate data
- Web search: "IBC resolution manufacturing India 2025 2026"

**Объём**: ~30–50 компаний
**Время**: 2–3 часа

---

## Блок 3: Бизнесы на продажу (P2)

### 3.1 Россия
- **biztorg.ru** — фильтр: производство, инжиниринг (не ИТ)
- **bizzona.ru** — аналогичный фильтр
- **avito.ru/biznes** — раздел "Готовый бизнес"

### 3.2 США
- **BizBuySell.com** — крупнейший marketplace (фильтр: Manufacturing, Services, Construction)
- **BizQuest.com** — аналог
- **LoopNet** — commercial RE + businesses
- **DealStream.com** — mid-market deals

### 3.3 Европа
- **BusinessesForSale.com** — мультистрановый (UK фокус)
- **DealRoom** / **Dealsuite** — EU mid-market
- **Flippa** (для мелких, но с physical component)
- Локальные: **Daltons Business (UK)**, **DUB.de (DE)**, **Transentreprise.com (FR)**

### 3.4 Индия
- **IndiaBizForSale.com** — основной marketplace
- **SMERGERS.com** — M&A платформа для SME
- **IndiaMart** (раздел бизнесов)

**Что парсить (единый формат)**:
- Название / описание
- Отрасль (фильтровать: не чистое ПО)
- Страна, регион
- Цена (asking price)
- Выручка, EBITDA (если указаны)
- Штат (если указан)
- Ссылка, дата

**Объём**: по 20–50 на географию = ~100–200 всего
**Время**: 3–4 часа

---

## Блок 4: Зарплаты по ролям (P1)

### Целевые роли (единые для всех стран)

Роли из методики K1–K4, сгруппированные:

| Группа | Роли |
|--------|------|
| Бэк-офис | Бухгалтер, HR-специалист, Рекрутер, Документовед |
| Производство/ops | Планировщик производства, Снабженец, Контролёр ОТК, Оператор станка |
| Инжиниринг | Инженер-проектировщик |
| Продажи | Менеджер по продажам |

### 4.1 Россия — hh.ru API

**API**: `GET https://api.hh.ru/vacancies?text=бухгалтер&area=1&per_page=100`
- area=1 Москва, area=2 СПб, area=3 Екатеринбург, area=4 Новосибирск
- Парсить: min/max зарплата из выдачи, считать медиану, 25-й и 75-й перцентиль

**Регионы**: Москва, СПб, МО, регионы-миллионники (Екб, Нск, Казань, Нижний)

### 4.2 США — BLS + Glassdoor

**Источники**:
- **BLS Occupational Employment and Wage Statistics (OEWS)** — api.bls.gov, официальные данные по occupations (SOC codes)
- **Glassdoor** — web scraping или API (для tech-adjacent roles)
- **Levels.fyi** — для инженерных ролей

**SOC-маппинг**:
| Роль | SOC Code |
|------|----------|
| Accountant | 13-2011 |
| HR Specialist | 13-1071 |
| Recruiter | 13-1071.01 |
| Production Planner | 13-1081 |
| Purchasing Agent | 13-1023 |
| Quality Inspector | 51-9061 |
| Machine Operator | 51-4041 |
| Mechanical Engineer | 17-2141 |
| Sales Manager | 11-2022 |

**Регионы**: NYC, SF Bay Area, Texas, Midwest (manufacturing belt)
**Формат**: median, 10th, 25th, 75th, 90th percentile (BLS даёт всё это)

### 4.3 Европа — Eurostat + Glassdoor

**Источники**:
- **Eurostat** — Structure of Earnings Survey (SES), данные по NACE/ISCO
- **Glassdoor EU** — по странам (UK, DE, FR)
- **UK ONS** — Annual Survey of Hours and Earnings (ASHE)
- **Destatis (DE)** — Verdienststrukturerhebung

**Регионы**: London, Berlin, Paris, Amsterdam, Warsaw
**Маппинг**: ISCO-08 коды → аналоги SOC

### 4.4 Индия — Naukri + PayScale

**Источники**:
- **Naukri.com** — крупнейший job portal, salary data (web search / scraping)
- **PayScale India** — salary reports
- **AmbitionBox** — salary data by company/role
- **MoSPI** — Periodic Labour Force Survey (PLFS) — макроданные

**Регионы**: Mumbai, Delhi/NCR, Bangalore, Chennai, Pune
**Валюта**: INR (с конвертацией в USD для сравнения)

### Единый формат выхода

```markdown
---
id: salary-{country}-{role}-{region}
source: hh_api | bls | eurostat | naukri
date: 2026-03-15
topic: salary
region: Moscow | NYC | London | Mumbai
country: RU | US | EU-DE | IN
industry: back_office | manufacturing | engineering | sales
role: accountant | hr_specialist | production_planner | ...
currency: RUB | USD | EUR | INR
---

Роль: Бухгалтер
Регион: Москва
Медиана: 95 000 ₽
25-й перцентиль: 70 000 ₽
75-й перцентиль: 130 000 ₽
Источник: hh.ru, выборка 247 вакансий
Дата: март 2026
```

**Время**: 3–4 часа (все 4 географии)

---

## Блок 5: Отраслевые бенчмарки (P2)

### Что собирать (единый набор метрик)

1. **Выработка на сотрудника** (Revenue per employee) по отраслям
2. **Доля ФОТ в себестоимости** (Labor cost as % of COGS/revenue)
3. **Средний штат по размеру компании** (SME segmentation)
4. **Рентабельность по отраслям** (Operating margin, EBITDA margin)

### 5.1 Россия
- **Росстат / ЕМИСС** (fedstat.ru) — по ОКВЭД секциям C, F, G, H
- **СПАРК / Контур.Фокус** — агрегаты по отраслям (платный, но есть открытые отчёты)

### 5.2 США
- **BLS Productivity data** — Labor productivity by industry
- **US Census — Annual Business Survey** — revenue, payroll, employees by NAICS
- **FRED (St. Louis Fed)** — macro indicators
- **IBISWorld** — industry reports (платный, но executive summaries доступны)

### 5.3 Европа
- **Eurostat — Structural Business Statistics (SBS)** — revenue, employment, costs by NACE
- **OECD Data** — productivity, labor costs by country/industry
- **UK ONS — Annual Business Survey**

### 5.4 Индия
- **MoSPI** — Annual Survey of Industries (ASI) — factory sector data
- **RBI** — Handbook of Statistics on Indian Economy
- **NASSCOM** — для services/BPO sector benchmarks
- **CMIE (Centre for Monitoring Indian Economy)** — Prowess database

### Ключевые отрасли для бенчмарков

| NAICS/NACE | Описание | Почему важно |
|------------|----------|--------------|
| 31–33 / C | Manufacturing | Основной таргет: большие бэк-офисы |
| 23 / F | Construction | Проектные + инжиниринговые компании |
| 42–45 / G | Wholesale/Retail trade | Логистика, снабжение |
| 48–49 / H | Transportation | Диспетчеризация, планирование |
| 54 / M | Professional services | Инжиниринг, консалтинг |
| 56 / N | Administrative services | BPO, аутсорсинг (особенно Индия) |

**Время**: 3–4 часа

---

## Блок 6: Кейсы AI-обучения команд (P1)

### Что ищем

Кейсы, где AI внедрялся для **обучения/усиления людей** (НЕ замена оборудования, НЕ чистая автоматизация). Фокус:
- Обучение сотрудников работе с AI-инструментами
- Рост выработки на человека (productivity per employee)
- Сокращение времени онбординга
- ROI от AI-обучения (cost of training vs. productivity gain)
- Отраслевая привязка (manufacturing, services, BPO)

### 6.1 Глобальные отчёты (все географии)

**Источники**:
- **McKinsey Global Institute** — "The economic potential of generative AI" (2023–2026)
- **BCG + MIT Sloan** — "AI at Work" reports
- **Deloitte** — "State of AI in the Enterprise"
- **Harvard Business Review** — case studies
- **World Economic Forum** — "Future of Jobs" report
- **Accenture** — "Work, Workforce, Workers" AI reports

**Поисковые запросы**:
- "AI workforce training ROI manufacturing"
- "generative AI employee productivity case study"
- "AI upskilling non-tech companies results"
- "AI training back office productivity improvement"

### 6.2 Россия

**Источники**:
- **vc.ru** — поиск: "AI обучение сотрудников", "AI производительность"
- **Хабр** — аналогичные запросы
- **РБК** — "искусственный интеллект бизнес внедрение"
- **Сколково / НИУ ВШЭ** — отчёты об AI adoption в РФ

### 6.3 США

**Источники**:
- **MIT Technology Review** — AI case studies
- **Stanford HAI** — AI Index Report (annual)
- **NBER** — working papers on AI and productivity
- **Fortune / Bloomberg** — AI transformation stories

### 6.4 Европа

**Источники**:
- **EU AI Act context** — reports on AI adoption in EU enterprises
- **European Commission** — Digital Economy and Society Index (DESI)
- **UK DSIT** — AI activity in UK businesses survey
- **Fraunhofer Institute (DE)** — industry AI reports

### 6.5 Индия

**Источники**:
- **NASSCOM** — AI adoption in Indian enterprises, BPO transformation
- **Niti Aayog** — National Strategy for AI
- **Indian School of Business / IIM** — case studies
- **YourStory / Inc42** — Indian startup AI adoption stories

### Формат выхода

```markdown
---
id: case-{country}-{company_or_topic}
source: case_study
date: 2026-03-15
topic: case
region: US | EU-UK | IN | RU | global
country: US | UK | DE | IN | RU
industry: manufacturing | bpo | engineering | back_office
tags: [AI-обучение, productivity, ROI, onboarding]
url: https://...
---

**Кейс**: [Название компании / отчёта]
**Отрасль**: Manufacturing (automotive parts)
**Страна**: США, Мичиган
**Что сделали**: Обучили 120 бэк-офисных сотрудников работать с AI-инструментами для планирования и закупок
**Результат**: Выработка на человека +180% за 6 месяцев, сокращение штата бэк-офиса с 120 до 45
**ROI**: Стоимость обучения $200K, экономия на ФОТ $1.8M/год
**Источник**: McKinsey report, 2025
```

**Объём**: 30–50 кейсов (8–12 на географию + 10 глобальных)
**Время**: 4–5 часов

---

## Общая структура папок

```
projects/ai-acquisition-fund/knowledge-base/
├── methodology/           ← нарезка из лендинга и плана (15–20 файлов)
├── distressed/
│   ├── ru/               ← fedresurs
│   ├── us/               ← PACER, SEC
│   ├── eu/               ← Companies House, Handelsregister
│   └── in/               ← NCLT, IBBI
├── businesses-for-sale/
│   ├── ru/               ← biztorg, bizzona, avito
│   ├── us/               ← BizBuySell, BizQuest
│   ├── eu/               ← BusinessesForSale, DUB
│   └── in/               ← IndiaBizForSale, SMERGERS
├── salaries/
│   ├── ru/               ← hh.ru
│   ├── us/               ← BLS
│   ├── eu/               ← Eurostat, ONS
│   └── in/               ← Naukri, PayScale
├── benchmarks/
│   ├── ru/               ← Росстат
│   ├── us/               ← BLS, Census
│   ├── eu/               ← Eurostat, OECD
│   └── in/               ← MoSPI, RBI
└── cases/
    ├── global/           ← McKinsey, BCG, Deloitte
    ├── ru/               ← vc.ru, Хабр
    ├── us/               ← MIT, Stanford, HBR
    ├── eu/               ← EC reports, Fraunhofer
    └── in/               ← NASSCOM, Niti Aayog
```

---

## Порядок выполнения

### Фаза 1 — Фундамент (день 1)

| # | Задача | Время | Блокеры |
|---|--------|-------|---------|
| 1.1 | Methodology: нарезка лендинга на chunks | 1ч | нет |
| 1.2 | Salaries RU: hh.ru API (10 ролей × 4 региона) | 1.5ч | нет |
| 1.3 | Salaries US: BLS OEWS data pull | 1ч | нет |
| 1.4 | Cases global: поиск McKinsey/BCG/Deloitte отчётов | 1.5ч | нет |

### Фаза 2 — Основные данные (день 2)

| # | Задача | Время | Блокеры |
|---|--------|-------|---------|
| 2.1 | Distressed RU: fedresurs парсинг | 2–3ч | anti-bot |
| 2.2 | Distressed US: PACER + SEC + web search | 2ч | PACER может требовать ручной доступ |
| 2.3 | Cases RU: vc.ru, Хабр | 1.5ч | нет |
| 2.4 | Cases US: MIT, Stanford HAI, HBR | 1.5ч | нет |

### Фаза 3 — Расширение (день 3)

| # | Задача | Время | Блокеры |
|---|--------|-------|---------|
| 3.1 | Salaries EU: Eurostat + Glassdoor | 1.5ч | Eurostat UI медленный |
| 3.2 | Salaries IN: Naukri + PayScale | 1.5ч | может потребоваться scraping |
| 3.3 | Distressed EU: Companies House API + DE | 2ч | API key для Companies House |
| 3.4 | Distressed IN: IBBI reports | 1.5ч | PDF parsing |

### Фаза 4 — Бенчмарки и бизнесы (день 4)

| # | Задача | Время | Блокеры |
|---|--------|-------|---------|
| 4.1 | Benchmarks: все 4 географии | 3ч | разные форматы данных |
| 4.2 | Businesses for sale: все 4 географии | 3ч | scraping, anti-bot |
| 4.3 | Cases EU + IN | 2ч | нет |

### Фаза 5 — Финализация (день 5)

| # | Задача | Время | Блокеры |
|---|--------|-------|---------|
| 5.1 | Проверка полноты: все chunks имеют метаданные | 1ч | нет |
| 5.2 | Кросс-валидация: зарплаты ↔ бенчмарки (ФОТ/выработка) | 1ч | нет |
| 5.3 | Дедупликация и нормализация форматов | 1ч | нет |
| 5.4 | Генерация embeddings (тест на 10 chunks) | 1ч | нужен API key |

---

## Важные правила (обновлённые)

1. **Каждый документ — с датой актуальности** (`date` в метаданных)
2. **Фильтровать домен**: НЕ включать чисто софтверные компании
3. **Конкретика**: числа, регионы, идентификаторы — не абстрактные описания
4. **Один chunk — одна мысль**: не смешивать разные темы
5. **Язык**: данные по RU — на русском, данные по US/EU/IN — на английском. Метаданные — всегда латиницей
6. **Валюта**: указывать локальную + эквивалент в USD
7. **Отраслевые коды**: указывать локальный код + маппинг (ОКВЭД → NAICS → NACE → NIC)
8. **Не смешивать географии** в одном chunk — каждый документ про одну страну/регион

---

## Риски и митигации

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| fedresurs anti-bot | Высокая | Playwright + ручной fallback |
| PACER платный ($0.10/page) | Средняя | Использовать CourtListener (бесплатный) + web search |
| Eurostat медленный API | Средняя | Bulk download datasets |
| Naukri нет API | Высокая | Web search + PayScale reports |
| NCLT сайт нестабильный | Высокая | IBBI quarterly PDFs как основной источник |
| Данные устаревшие (>1 года) | Средняя | Маркировать date, приоритезировать 2025–2026 |

---

## Блок 7: Позиция фонда — разграничение с робототехникой и hardware AI

Это отдельный chunk для knowledge base. Бот должен чётко объяснять фокус фонда.

### Суть позиции

ScaleWithAI VC видит и признаёт огромный потенциал робототехники, промышленной автоматизации и hardware AI — это мощный тренд, который трансформирует целые отрасли. Но это **не наша зона компетенций**.

Наш фокус — **интеллектуальный капитал**: обучение людей работе с AI-инструментами, повышение выработки на человека, перевод знаний из голов в системы. Это другой тип сделок, другая экспертиза оценки, другая модель создания стоимости.

### Разграничение

| | Робототехника / Hardware AI | ScaleWithAI VC (наш фокус) |
|---|---|---|
| Что меняем | Физические процессы, оборудование | Работу людей с информацией |
| Инвестиция | CapEx: роботы, станки, линии | OpEx: обучение, подписки, инструменты |
| Payback | 2–5 лет | 2–6 месяцев |
| Ключевой актив | Hardware, IP на оборудование | Обученная команда, knowledge systems |
| Риск | Техническая интеграция, обслуживание | Adoption, retention обученных людей |
| Масштабирование | Закупка нового оборудования | Тиражирование программы обучения |

Если к нам приходит компания, где основной потенциал — в замене конвейера роботами, мы честно скажем: "это не наш профиль, вам нужен другой тип инвестора". Мы сильны там, где ценность создаётся людьми за экранами.

### Задача
- Оформить как chunk для `knowledge-base/methodology/fund-focus-robotics-positioning.md`
- Использовать в system prompt чатбота для корректных ответов

---

## Блок 8: Дополнительные географии (Tier 2)

Помимо основных 4 географий (RU, US, EU, IN), имеет смысл рассмотреть:

### 8.1 Бразилия (BR)
- **Почему**: огромный manufacturing sector, высокая доля ручного труда, много distressed-активов (judicial recovery по Lei 11.101). Большие бэк-офисы, низкая AI-adoption
- **Distressed**: Serasa Experian, Econodata, judicial recovery filings
- **Бизнесы на продажу**: OLX Brasil, Empresa à Venda
- **Зарплаты**: Glassdoor BR, Catho, IBGE (PNAD)
- **Бенчмарки**: IBGE (Instituto Brasileiro de Geografia e Estatística)
- **Приоритет**: Tier 2 — собирать после основных 4 географий

### 8.2 Турция (TR)
- **Почему**: мощная производственная база (текстиль, автокомпоненты, пищёвка), дешёвый ФОТ, но низкая productivity per employee. Много компаний в финансовом стрессе из-за инфляции/девальвации лиры. Идеально под модель "купить дёшево, обучить команду"
- **Distressed**: TMSF (Tasarruf Mevduatı Sigorta Fonu), Turkish Trade Registry
- **Зарплаты**: Kariyer.net, Glassdoor TR, TurkStat
- **Бенчмарки**: TurkStat (TUIK)
- **Приоритет**: Tier 2

### 8.3 Мексика (MX)
- **Почему**: nearshoring boom из Китая в US, множество manufacturing SME с ручными процессами. IMMEX/maquila компании с большими бэк-офисами
- **Distressed**: Ley de Concursos Mercantiles, IFECOM
- **Зарплаты**: Indeed MX, OCC Mundial, INEGI
- **Бенчмарки**: INEGI (Instituto Nacional de Estadística y Geografía)
- **Приоритет**: Tier 2

### 8.4 Польша (PL) — выделить из EU
- **Почему**: крупнейший manufacturing hub в CEE, EU-доступ, хорошие данные (KRS registry). BPO-хаб (Kraków, Wrocław). Частично покрыта через EU-блок, но стоит выделить как приоритетную страну
- **Distressed**: KRS (Krajowy Rejestr Sądowy), Monitor Sądowy i Gospodarczy
- **Зарплаты**: Pracuj.pl, GUS (Główny Urząd Statystyczny)
- **Приоритет**: Tier 2 (но данные доступнее, чем BR/TR/MX)

### Сроки
Tier 2 географии — **Фаза 6** (после основных 5 фаз), ориентировочно дни 6–8.

---

## Блок 9: Дополнительные отрасли

Текущий brief покрывает manufacturing, инжиниринг, бэк-офис. Есть пропущенные сегменты с высоким потенциалом для тезиса фонда:

### Высокий приоритет

| Отрасль | Почему подходит | Где искать |
|---------|----------------|------------|
| **BPO / Shared Services Centers** | Сотни людей на типовых "экранных" ролях. Идеальный K2. AI-обучение даёт ×3–5 на человека | IN (Bangalore, Hyderabad), PL (Kraków), PH |
| **Логистика / 3PL** | Диспетчеризация, route planning, документооборот. 30–40% штата — "экранные" роли. Много distressed-активов (маржинальность падает) | RU, US, EU |
| **Медицинский бэк-офис** | Кодирование диагнозов, medical billing, страховые claims. Karpathy score 8–9. В США — огромный рынок (revenue cycle management) | US (основной), EU |
| **Агрохолдинги (управляющие компании)** | Не поля, а управление: планирование, закупки, учёт. Большие бэк-офисы, всё в Excel | RU, BR, IN |

### Средний приоритет

| Отрасль | Почему подходит | Где искать |
|---------|----------------|------------|
| **Страхование** | Андеррайтинг, claims processing, актуарный бэк-офис. Karpathy score 7–9 | US, EU, IN |
| **Образование (edtech operations)** | Не контент, а операционка: enrollment, grading, student support | US, IN |
| **Property management** | Бухгалтерия, tenant relations, maintenance scheduling. Много компаний, типовые роли | US, EU |

### Задача
- Добавить эти отрасли в фильтры по всем блокам (distressed, businesses for sale, salaries, benchmarks, cases)
- Расширить NAICS/NACE фильтры: добавить 62 (Health care), 52 (Finance/Insurance), 53 (Real estate), 11 (Agriculture management)

---

## Блок 10: Ключевые исследовательские вопросы

Помимо сбора данных, knowledge base должна содержать ответы на стратегические вопросы. Их нужно исследовать и оформить как отдельные chunks.

### 10.1 Юридические рамки M&A по странам

| Вопрос | Почему важно |
|--------|-------------|
| Как иностранный фонд покупает активы в каждой стране? | Структура сделок — ключевое для инвесторов |
| Ограничения на foreign ownership | IN — FDI caps по секторам; RU — стратегические отрасли; BR — ограничения на land ownership |
| Структура: прямая покупка vs. SPV vs. JV | Определяет налоги и контроль |
| Tax implications cross-border M&A | Двойное налогообложение, treaty benefits |

**Источники**: Baker McKenzie guides, PwC Worldwide Tax Summaries, Deloitte M&A country guides (публичные)

### 10.2 Unit economics AI-обучения

| Вопрос | Почему важно |
|--------|-------------|
| Стоимость обучения 1 сотрудника AI-инструментам (по ролям, по странам) | Основа financial model фонда |
| Сколько времени занимает? (2 недели vs. 2 месяца) | Определяет скорость трансформации |
| Retention rate после обучения | Риск: обученный сотрудник уходит за +50% зарплаты |
| Какие AI-инструменты используются | ChatGPT Enterprise, Copilot, custom fine-tuned — влияет на OpEx |

**Источники**: LinkedIn Learning reports, Coursera enterprise data, vendor case studies (Microsoft, OpenAI enterprise)

### 10.3 Конкурентный ландшафт

| Вопрос | Почему важно |
|--------|-------------|
| Кто ещё делает "buy & AI-transform"? | Знать конкурентов за активы |
| Search-фонды с AI-тезисом | Прямые конкуренты |
| PE с AI-операционным тезисом | Alpine Investors (people-focused), Tiny Capital, Constellation Software |
| Мультипликаторы для "AI-transformed" vs. обычных компаний | Обоснование exit valuation |

**Источники**: PitchBook, Crunchbase, PE fund websites, LP letters (где публичные)

### 10.4 AI-readiness frameworks

| Вопрос | Почему важно |
|--------|-------------|
| Готовые frameworks для оценки AI-readiness | Обогатить нашу K1–K4 |
| McKinsey AI Quotient, Deloitte AI Maturity Model | Сравнить с нашей методикой |
| Можно ли оценить AI-readiness из открытых данных (hh.ru, LinkedIn, Naukri)? | Скоринг без due diligence |

### 10.5 Failure cases — почему НЕ работает

| Вопрос | Почему важно |
|--------|-------------|
| Кейсы провала AI-обучения (resistance, bad tooling, wrong industry) | Бот должен честно говорить "здесь не сработает" |
| "Долина разочарования" — потратили на AI-трансформацию и не получили ROI | Антипаттерны для скоринга |
| Отрасли/роли где AI-обучение не даёт кратного эффекта | Границы применимости модели |

**Источники**: Gartner Hype Cycle, MIT Sloan "AI failures" research, HBR case studies

### Задача
- Каждый вопрос → web research → chunk 500–1000 токенов в `knowledge-base/strategy/`
- Добавить папку `knowledge-base/strategy/` в структуру

---

## Обновлённая структура папок

```
projects/ai-acquisition-fund/knowledge-base/
├── methodology/           ← нарезка из лендинга и плана (15–20 файлов)
│   └── fund-focus-robotics-positioning.md  ← NEW: позиция по робототехнике
├── strategy/              ← NEW: ответы на ключевые вопросы
│   ├── legal-ma-frameworks/    ← по странам
│   ├── unit-economics/         ← стоимость обучения
│   ├── competitive-landscape/  ← конкуренты
│   ├── ai-readiness/           ← frameworks
│   └── failure-cases/          ← антипаттерны
├── distressed/
│   ├── ru/
│   ├── us/
│   ├── eu/
│   ├── in/
│   ├── br/               ← NEW: Tier 2
│   ├── tr/               ← NEW: Tier 2
│   └── mx/               ← NEW: Tier 2
├── businesses-for-sale/
│   ├── ru/ us/ eu/ in/
│   └── br/ tr/ mx/       ← NEW: Tier 2
├── salaries/
│   ├── ru/ us/ eu/ in/
│   └── br/ tr/ mx/       ← NEW: Tier 2
├── benchmarks/
│   ├── ru/ us/ eu/ in/
│   └── br/ tr/ mx/       ← NEW: Tier 2
└── cases/
    ├── global/
    ├── ru/ us/ eu/ in/
    └── industries/        ← NEW: по доп. отраслям (BPO, logistics, medical billing, agro)
```

---

## Обновлённый порядок выполнения

### Фаза 1–5 — без изменений (основные 4 географии)

### Фаза 6 — Стратегические вопросы (день 6)

| # | Задача | Время |
|---|--------|-------|
| 6.1 | Позиция по робототехнике → chunk | 0.5ч |
| 6.2 | Legal M&A frameworks (RU, US, EU, IN) | 2ч |
| 6.3 | Unit economics AI-обучения | 1.5ч |
| 6.4 | Конкурентный ландшафт | 1.5ч |
| 6.5 | AI-readiness frameworks | 1ч |
| 6.6 | Failure cases | 1.5ч |

### Фаза 7 — Дополнительные отрасли (день 7)

| # | Задача | Время |
|---|--------|-------|
| 7.1 | BPO/Shared Services: кейсы, зарплаты, бенчмарки | 2ч |
| 7.2 | Логистика/3PL: distressed, бенчмарки | 1.5ч |
| 7.3 | Медицинский бэк-офис (US фокус) | 1.5ч |
| 7.4 | Агрохолдинги (RU, BR, IN) | 1ч |

### Фаза 8 — Tier 2 географии (дни 8–9)

| # | Задача | Время |
|---|--------|-------|
| 8.1 | Бразилия: distressed + salaries + benchmarks | 3ч |
| 8.2 | Турция: distressed + salaries + benchmarks | 2.5ч |
| 8.3 | Мексика: distressed + salaries + benchmarks | 2.5ч |
| 8.4 | Польша (выделить из EU): углубление | 1.5ч |

---

## Обновления к оригинальному brief

Что изменилось относительно `knowledge-base-collection-brief.md`:

1. **География**: RU → RU + US + EU + IN (Tier 1) + BR + TR + MX + PL (Tier 2)
2. **Папки**: flat → `{блок}/{country}/`
3. **Источники**: добавлены аналоги для каждой страны
4. **Зарплаты**: единый набор ролей, маппинг на локальные классификаторы (SOC, ISCO, NIC)
5. **Язык данных**: RU русский, остальные английский
6. **Валюта**: всегда локальная + USD
7. **Отраслевые коды**: кросс-маппинг ОКВЭД ↔ NAICS ↔ NACE ↔ NIC
8. **Объём**: ×5–6 от оригинального (8 географий + стратегия + доп. отрасли)
9. **Сроки**: 8–9 рабочих дней вместо 2–3
10. **Новые блоки**: позиция по робототехнике (Блок 7), Tier 2 географии (Блок 8), доп. отрасли (Блок 9), стратегические вопросы (Блок 10)
11. **Новая папка**: `knowledge-base/strategy/` — для legal, unit economics, конкурентов, failure cases
