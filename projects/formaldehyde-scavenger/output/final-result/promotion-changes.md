# Promotion Changes — v001

## Назначение
Этот документ сопровождает `current.md` и фиксирует подготовку конкурентного сравнения, происхождение чисел и результат проверки полноты. Само техническое описание не подменяется маркетинговыми оценками.

## Проверенные новые данные
| Продукт | Параметр | Значение | Тип | Источник |
|---|---|---|---|---|
| BASF Loxanol MI 6311 | Активное содержание | ≈75% | TDS производителя | https://download.basf.com/p1/8a8081e18721a79301872315dfa20b42/en/Loxanol_MI_6311_TDS_30756558_EN_Technical_Data_Sheet_English.pdf?view= |
| BASF Loxanol MI 6311 | Плотность при 20 °C | ≈1,31 г/см³ | TDS производителя | тот же TDS |
| BASF Loxanol MI 6311 | pH | ≈10 | TDS производителя | тот же TDS |
| BASF Loxanol MI 6311 | Рекомендованная доля в краске | ≈6% | TDS производителя | https://download.basf.com/p1/8a80824f99704a54019971b21b5b0625/en/Loxanol%25C2%25A0MI_6311 |
| BASF Loxanol MI 6311 | Вязкость | ≈700 мПа·с | Каталог производителя | https://www.basf.com/dam/jcr%3A45da02da-3a48-4134-bda5-56067e694e17/basf/www/us/documents/en/general-business-topics/dispersions/IndustrialCoatings/2025-Industrial-Coatings-Brochure.pdf |
| Speco BlueBond | Фасовки | 2,5 л; 5 л; 20 л | Страница производителя | https://www.speco.sg/collections/shop-products/products/speco-bluebond-gen-3-odourless |

Цифры из TDS характеризуют **сам ингредиент**, а не эффективность обработки свежих срезов ДСП. Они не засчитываются как сопоставимые измерения эмиссии или времени высыхания.

## Аудит количественной заполненности

Определение: знаменатель — применимые **количественные показатели одинакового назначения**, позволяющие сопоставить продукты. Качественные сведения, фасовка и численные данные другой стадии технологического процесса не подменяют результаты обработки среза.

Ключевые общие показатели: расход на площадь, время высыхания, снижение HCHO за 30/90 дней, остаточное набухание, цена обработки на площадь. Для трёх исходных конкурентов сопоставимые открытые измерения по этому протоколу не подтверждены.

| Конкурент | Подтверждённых сопоставимых чисел | Из 5 основных метрик | Покрытие | Порог |
|---|---:|---:|---:|---|
| Speco BlueBond | 0 | 5 | 0% | FAIL |
| BASF Loxanol MI 6311 | 0 | 5 | 0% | FAIL |
| Asta FA1001 | 0 | 5 | 0% | FAIL |
| **Всего** | **0** | **15** | **0%** | **FAIL** |

**Статус пакета: NOT COMPLIANT с правилом ≥51% численно сопоставимых ячеек.** Числа из несопоставимых условий не выдаются за конкурентные преимущества.

## Дальнейшая промо-итерация
1. Проверить дополнительные продуктовые TDS, инструкции и цены; выбирать аналоги с сопоставимыми протоколами.
2. Для каждой вычисляемой оценки указать формулу, исходные данные, допущения, диапазон неопределённости и тест опровержения.
3. Переносить численные оценки в Final Result только после проверки сопоставимости и сохранения provenance.
4. Повторно подсчитать покрытие для каждого конкурента и всей матрицы. Не объявлять compliance до достижения 51%.

## Изменения относительно предыдущего результата
- Создан отдельный прозрачный журнал promotion-обработки.
- Подтверждены новые численные свойства BASF и фасовки Speco.
- Выявлено, что количественные свойства ингредиента BASF не равны измерениям готовой обработки торцов.
- Конкурентная матрица основного документа остаётся прежней до завершения сопоставимого исследования.


## Следующая итерация — восстановление compliance

**Причина отказа:** 0 из 15 сопоставимых количественных ячеек заполнены. Для порога не менее 51% при пяти метриках на конкурента необходимо минимум **3 из 5** по каждому конкуренту, то есть **9 из 15** всего. Дефицит: Speco 3, BASF 3, Asta 3, суммарно 9.

### Гипотеза A — существующая метрика: время и трудоёмкость обработки

**Проверяемое утверждение:** при обработке свежего среза ДСП/МДФ локальное нанесение губчатым аппликатором требует меньше подготовительных операций, чем применение BASF Loxanol MI 6311 через приготовление функциональной краски.

**Основание:** Loxanol MI 6311 — ингредиент рецептуры краски, а не готовый ручной состав для монтажника. Сравнивается полный цикл подготовки и обработки одинакового среза, а не только время одного мазка.

**Измерение:** минуты на подготовку 100 мл рабочего состава + секунды на обработку 1 м открытого среза; n≥5 операторов, одинаковые образцы. Раздельно фиксировать время до продолжения монтажа.

**Критерий опровержения:** если полный цикл с нашим составом не быстрее либо разница исчезает после нормирования на объём/оператора, маркетинговое преимущество отвергается.

**Статус:** конструктивное преимущество по сценарию применения; численный выигрыш ещё не измерен. В количественное покрытие не засчитывается.

### Гипотеза B — новая метрика: удельный расход на обработку среза

**Проверяемое утверждение:** наш состав обеспечивает равномерную обработку свежего среза одним проходом при расходе 30–60 г/м², тогда как распыление Speco BlueBond на ту же узкую открытую кромку приводит к большему непроизводительному расходу вне целевой зоны.

**Основание:** геометрия распыления и локального контактного нанесения различается. Это проверяемая гипотеза, а не отрицательный отзыв о продукте.

**Измерение:** г состава на 1 м среза толщиной 16 мм, доля массы на целевой поверхности (%), потери на соседние поверхности (%), коэффициент вариации между операторами; n≥5. Для нашего состава 30–60 г/м² соответствует **0,48–0,96 г на 1 м** среза толщиной 16 мм (геометрический пересчёт без учёта торцевых потерь).

**Критерий опровержения:** если Speco обеспечивает равный или меньший фактический расход на целевой поверхности при не худшем покрытии и без лишних следов, заявленное преимущество отвергается.

**Статус:** геометрический пересчёт для нашего состава выполнен; сравнительное значение Speco не измерено. В покрытие competitor numeric cells не засчитывается.

### Приоритеты маркетинговых метрик

1. **Потери состава при нанесении на узкий срез** — наглядный тест и прямая экономика.
2. **Полное время обработки одного погонного метра** — важно монтажнику.
3. **Стоимость обработки одного метра среза** — понятна мебельной компании.
4. **Изменение толщины и загрязнение ламинации** — критерии пригодности.
5. **Интегральная эмиссия HCHO за 90 суток** — главный технический эффект, но наиболее дорогая проверка.

### Compliance после двух проверок

Две гипотезы сформулированы и снабжены тестами опровержения. Новых **сопоставимых измеренных чисел конкурентов нет**: покрытие остаётся **0/15 = 0%**, порог **9/15** не достигнут. Для следующей итерации нужны измерения или опубликованные сопоставимые количественные данные.


## Iterations 3–5 — deeper manufacturer-source research (2026-10-09)

### Iteration 3: BASF primary technical data
Verified in manufacturer TDS: Loxanol MI 6311 active content approximately 75%, density approximately 1.31 g/cm³ at 20°C, pH approximately 10, recommended incorporation approximately 6% of total waterborne paint formulation, storage 0–40°C. Manufacturer coatings guide gives viscosity approximately 700 cP. These are useful **ingredient-level numbers**, not comparable cut-treatment efficacy results.

Sources:
- https://download.basf.com/p1/8a8081e18721a79301872315dfa20b42/en/Loxanol_MI_6311_TDS_30756558_EN_Technical_Data_Sheet_English.pdf?view=
- https://www.basf.com/dam/jcr%3A45da02da-3a48-4134-bda5-56067e694e17/basf/www/us/documents/en/general-business-topics/dispersions/IndustrialCoatings/2025-Industrial-Coatings-Brochure.pdf

### Iteration 4: Asta manufacturer product and process scope
FA1001 is listed for MDF/PB/OSB/plywood, glue-mix, MDF/PB blowline and plywood post-treatment. Manufacturer lists industrial packaging: IBC, tanker, drums and 25 kg bags. No validated numeric dosage, 90-day emission curve, swelling or post-install drying time was found in the public FA1001 product listing. Do **not** transfer numbers from unrelated ASTAPLY CR500 resin TDS to FA1001.

Source: https://www.astachemicals.com/product/supporting-products/

### Iteration 5: comparison suitability and numerical recovery
The three original alternatives belong to different product stages: consumer spray, paint additive, and industrial panel scavenger. Five end-use cut-treatment metrics (g/m², ready time, 30/90-day HCHO, swelling, cost/m²) cannot be fairly populated from manufacturer ingredient TDS alone. Counting BASF's 75%, 1.31 g/cm³, pH 10, 6%, and 700 cP as comparable cut-treatment outcomes would falsely pass the gate.

**Compliance:** still 0/15 comparable end-use quantitative competitor cells; minimum required 9/15, with at least 3/5 for each competitor. Three iterations did not establish compliant values. Status: **FAIL**, not a manufactured pass.

### Two follow-on falsifiable opportunities
1. **Existing metric — application overhead:** record minutes of preparation + application per metre for ready-to-use edge treatment versus paint-formulation additive workflows. This tests a meaningful operational distinction, not an invented competitor duration.
2. **New metric — waste fraction on narrow edges:** weigh sprayed vs contact-applied mass on a 16 mm exposed edge and adjacent finished surfaces. Report grams applied, grams reaching edge, percentage overspray and cleanup time. This may support an economically useful advantage, but no competitor value is asserted until tested.

### Recommendation for next numeric-compliance attempt
Use a shortlist of products with actual published TDS for the **same stage of use** (finished edge coating / post-install surface treatment) and request comparative measurements from vendors or run a standardized independent head-to-head test. Keep the original three as market-context analogues if useful, but do not misrepresent their manufacturing parameters as end-use metrics.


## Iterations 6–8 — scenario bounds, qualitative advantage, final promotion gate

### Iteration 6 — favorable vs adverse scenarios
Baseline engineering targets: 36 g/m² application, 9 min ready time, 0.060 mm dimensional change, ≥70% integrated 90-day HCHO reduction. On a 16-mm cut, nominal applied mass is **0.576 g per metre**. These are engineering specification values, not observations.

Three scenario types are required for future comparison: central, favorable to us, adverse to us. Competitor numeric uncertainty ranges cannot be established from missing manufacturer data; **no numeric competitor upper/lower bounds are asserted**. Favorable extreme selection therefore does not count toward quantitative competitor coverage.

### Iteration 7 — qualitative differentiators
- Fresh-cut-specific process and dose control are explicit in our design.
- Speco is a ready-to-use furniture spray; fresh-cut dose and 90-day cut-specific results are not publicly specified in the cited product material.
- BASF Loxanol is a paint additive; its 6% recommended incorporation rate describes formulation, not cut application.
- Asta FA1001 is marketed for panel production; its use is a different process stage.

**Interpretation:** these are design/use-case distinctions, not claims that competitors lack undocumented features. Most persuasive laboratory demonstration: weigh overspray vs contact dose and measure process-ready time, swelling and HCHO emissions under one shared protocol.

### Iteration 8 — promotion/compliance audit
- Final Result comparison matrix updated with specific qualitative differentiation and our 40%-stress engineering targets.
- Quantitatively comparable competitor end-use cells remain 0/15 for the five core metrics; required minimum 9/15.
- **Compliance: FAIL (0%).** No fabricated numerical bounds or cherry-picked estimates were inserted.
- Next falsification priority: head-to-head application to 16-mm cuts, gravimetric mass balance, operator time and 90-day emission tests. Report all outcomes, including reversals where competitors outperform.
