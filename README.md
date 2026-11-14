<div align="center">

# CodeGraphy Lite

### Local-First Visual Architecture Canvas & MCP Server for AI-First Developers

**Understand your architecture. Give AI the right context.**

[Quick Start](https://www.google.com/search?q=%23-en-quickstart) · [Lite vs Pro](https://www.google.com/search?q=%23-en-compare) · [Get CodeGraphy Pro](https://github.com/Vindettobkb/codegraphy-pro)

</div>

## Table of Contents / Содержание

### English

* [Feature Showcase](https://www.google.com/search?q=%23en-showcase)

* [Problems CodeGraphy Solves](https://www.google.com/search?q=%23en-problems)

* [Quick Start](https://www.google.com/search?q=%23en-quickstart)

* [Lite vs Pro](https://www.google.com/search?q=%23en-compare)

* [CodeGraphy Markdown Format (.cg.md)](https://www.google.com/search?q=%23en-format)

* [AI Prompt for Architecture Generation](https://www.google.com/search?q=%23en-prompt)

* [Contacts](https://www.google.com/search?q=%23en-contacts)

### Русский

* [Демонстрация возможностей](https://www.google.com/search?q=%23ru-showcase)

* [Какие проблемы решает CodeGraphy](https://www.google.com/search?q=%23ru-problems)

* [Быстрый старт](https://www.google.com/search?q=%23ru-quickstart)

* [Lite и Pro](https://www.google.com/search?q=%23ru-compare)

* [Формат CodeGraphy Markdown (.cg.md)](https://www.google.com/search?q=%23ru-format)

* [AI-промпт для генерации архитектуры](https://www.google.com/search?q=%23ru-prompt)

* [Контакты](https://www.google.com/search?q=%23ru-contacts)

# English

<a id="en-showcase"></a>

## Feature Showcase

### 1. Auto-Discovery & Living Architecture Map

Automatically scans repositories, discovers modules, extracts dependencies, and generates a reactive architecture graph.

<p align="center">
<img src="https://github.com/user-attachments/assets/115c3574-b887-4214-befb-fdb27c5a76b4" alt="Scan and Living Architecture Graph" width="850">
</p>

### 2. Layer Filtering & IDE Deep Linking

Filter architectural layers (`Frontend / UI`, `Backend / API & Services`, `Split Layers`) and jump directly to the corresponding file and line in PyCharm, VS Code, or Cursor.

<p align="center">
<img src="https://github.com/user-attachments/assets/67355e0c-ab08-4b67-898f-ee6171afbc63" alt="Layer Filtering and IDE Integration" width="850">
</p>

### 3. AI-Powered Architectural Context

Connect Claude Code, Cursor, Windsurf, or local models using structured graph context instead of dumping raw files.

<p align="center">
<img src="https://github.com/user-attachments/assets/ca3fc0fe-44fd-4f0a-a64e-5aa5c91e3756" alt="AI Architecture Analysis" width="850">
</p>

<a id="en-problems"></a>

## Problems CodeGraphy Solves

1. **Context Window Bloat** — Sending entire source files to LLMs wastes tokens, slows down responses, and dilutes attention on the architecture that matters.

2. **AI Hallucinations** — Without clear module boundaries and dependency direction, coding assistants invent non-existent interfaces and break layer rules.

3. **Fragmented Architectural Knowledge** — Real features span UI components, API routes, services, and storage. CodeGraphy keeps the whole map interactive in one place.

<a id="en-quickstart"></a>

## Quick Start

Install **CodeGraphy Lite** locally (requires Python 3.10+):

```
pip install codegraphy-lite

```

Or install directly from GitHub:

```
git clone https://github.com/Vindettobkb/codegraphy-lite.git
cd codegraphy-lite
pip install -e .

```

Launch the local workspace UI:

```
codegraphy-lite --port 8000

```

Then open `http://127.0.0.1:8000` in your browser.

<a id="en-compare"></a>

## Lite (Open Source) vs Pro

**CodeGraphy Lite** gives you the interactive architecture canvas, layer views, `.cg.md` import/export, and core MCP tools for repositories up to 35 files. [**CodeGraphy Pro**](https://github.com/Vindettobkb/codegraphy-pro) unlocks full-repository scale, AST Smart Context compression, and static drift analysis.

| Capability | CodeGraphy Lite | CodeGraphy Pro | 
| ----- | ----- | ----- | 
| Interactive Architecture Canvas & Split Layers | Included | Included | 
| Direct Neighbors (1-Hop) & IDE Deep Linking | Included | Included | 
| `.cg.md` Workspace Export & Import | Included | Included | 
| Project Scan Limit | Up to 35 files | Unlimited | 
| STDIO MCP Server Tools | 3 core tools | Full 11 tools | 
| AST Smart Context (\~82.8% token savings) | — | Included | 
| Hybrid Context Inspector (`Full / AST / Off`) & Secret Redaction | — | Included | 
| Architecture Analysis (`Tarjan O(V+E)`), Blast Radius & Git Diff | — | Included | 

<a id="en-format"></a>

## CodeGraphy Markdown Format (.cg.md)

CodeGraphy uses a declarative Markdown format for sharing software architecture across developers, Git repositories, and AI tools. Each `.cg.md` file has three sections:

* **Lanes** — architectural layers or areas.

* **Tasks** — development tasks.

* **Topics** — modules and their `[[Topic Name]]` connections.

<a id="en-prompt"></a>

## AI Prompt for Architecture Generation

Copy the prompt below into ChatGPT, Claude, Gemini, or DeepSeek to generate an import-ready `.cg.md` file:

```
Generate a complete software architecture for my project using the CodeGraphy Markdown format.

Requirements:
- Include YAML frontmatter: format: codegraphy-workspace, version: 2.0, workspace_id, name
- Include three sections: ## Lanes, ## Tasks, ## Topics
- Lanes format: - [lane_id] **Title** | order=0 | color=#38bdf8 | expanded
- Tasks format: ### Task: Title `task_id` with status, lane, linked_topics, description
- Topics format: ### Topic: Title `topic_id` with status, lane, task, position, description, connects_to, files
- Use [[Topic Name]] for topic connections and indented list items for file paths.
- Derive the architecture strictly from actual source files without inventing modules.

```

<a id="en-contacts"></a>

## Contacts

* **Pro Edition:** [github.com/Vindettobkb/codegraphy-pro](https://github.com/Vindettobkb/codegraphy-pro)

* **Telegram:** [@Methyienedloxymethamphetamine](https://t.me/Methyienedloxymethamphetamine)

* **Discord:** `nevindetto`

# Русский

<a id="ru-showcase"></a>

## Демонстрация возможностей

### 1. Auto-Discovery & Living Architecture Map

Автоматически сканирует репозиторий, находит модули, извлекает зависимости и строит интерактивный граф архитектуры.

<p align="center">
<img src="https://github.com/user-attachments/assets/115c3574-b887-4214-befb-fdb27c5a76b4" alt="Scan and Living Architecture Graph" width="850">
</p>

### 2. Layer Filtering & IDE Deep Linking

Позволяет разделять архитектурные слои (`Frontend / UI`, `Backend / API & Services`, `Split Layers`) и открывать нужный файл и строку прямо в PyCharm, VS Code или Cursor.

<p align="center">
<img src="https://github.com/user-attachments/assets/67355e0c-ab08-4b67-898f-ee6171afbc63" alt="Layer Filtering and IDE Integration" width="850">
</p>

### 3. AI-Powered Architectural Context

Подключайте Claude Code, Cursor, Windsurf или локальные модели через структурированный контекст графа вместо отправки сырых файлов.

<p align="center">
<img src="https://github.com/user-attachments/assets/ca3fc0fe-44fd-4f0a-a64e-5aa5c91e3756" alt="AI Architecture Analysis" width="850">
</p>

<a id="ru-problems"></a>

## Какие проблемы решает CodeGraphy

1. **Переполнение контекстного окна** — отправка целых исходников в LLM сжигает токены и ухудшает точность модели.

2. **Галлюцинации AI** — без понимания границ слоёв и зависимостей ассистент начинает придумывать несуществующие интерфейсы.

3. **Разрозненная архитектура** — фичи затрагивают UI, API, сервисы и хранилище сразу. CodeGraphy держит всю карту связей перед глазами.

<a id="ru-quickstart"></a>

## Быстрый старт

Установите **CodeGraphy Lite** (требуется Python 3.10+):

```
pip install codegraphy-lite

```

Или из репозитория GitHub:

```
git clone https://github.com/Vindettobkb/codegraphy-lite.git
cd codegraphy-lite
pip install -e .

```

Запуск локального интерфейса:

```
codegraphy-lite --port 8000

```

После запуска откройте `http://127.0.0.1:8000` в браузере.

<a id="ru-compare"></a>

## Lite и Pro

**CodeGraphy Lite** — бесплатная open-source версия с интерактивным графом, слоями, форматом `.cg.md` и базовыми MCP-инструментами (до 35 файлов). [**CodeGraphy Pro**](https://github.com/Vindettobkb/codegraphy-pro) снимает лимит файлов и добавляет AST-сжатие контекста, инспектор токенов и статический анализ архитектуры.

| Возможность | CodeGraphy Lite | CodeGraphy Pro | 
| ----- | ----- | ----- | 
| Интерактивный граф архитектуры и Split Layers | Есть | Есть | 
| Direct Neighbors (1-Hop) и переходы в IDE | Есть | Есть | 
| Экспорт и импорт `.cg.md` | Есть | Есть | 
| Лимит сканирования проекта | До 35 файлов | Без ограничений | 
| MCP-сервер (STDIO) | 3 базовых инструмента | Все 11 инструментов | 
| AST Smart Context (\~82.8% экономии токенов) | — | Есть | 
| Hybrid Context Inspector (`Full / AST / Off`) и скрытие секретов | — | Есть | 
| Architecture Analysis (`Tarjan O(V+E)`), Blast Radius и Git Diff | — | Есть | 

<a id="ru-format"></a>

## Формат CodeGraphy Markdown (.cg.md)

Декларативный Markdown-формат для описания архитектуры проекта в Git и передачи контекста AI. Документ состоит из трёх секций:

* **Lanes** — архитектурные слои и направления.

* **Tasks** — задачи разработки.

* **Topics** — модули и связи между ними через `[[Topic Name]]`.

<a id="ru-prompt"></a>

## AI-промпт для генерации архитектуры

```
Создай полную архитектуру моего проекта в формате Markdown CodeGraphy.

Требования:
- Добавь YAML frontmatter: format: codegraphy-workspace, version: 2.0, workspace_id, name
- Добавь три раздела: ## Lanes, ## Tasks, ## Topics
- Формат Lanes: - [lane_id] **Название** | order=0 | color=#38bdf8 | expanded
- Формат Tasks: ### Task: Название `task_id` (status, lane, linked_topics, description)
- Формат Topics: ### Topic: Название `topic_id` (status, lane, task, position, description, connects_to, files)
- Используй [[Название темы]] для связей и вложенный список для путей к файлам.
- Строй архитектуру строго по реальным файлам проекта, не выдумывая модули.

```

<a id="ru-contacts"></a>

## Контакты

* **Pro-версия:** [github.com/Vindettobkb/codegraphy-pro](https://github.com/Vindettobkb/codegraphy-pro)

* **Telegram:** [@Methyienedloxymethamphetamine](https://t.me/Methyienedloxymethamphetamine)

* **Discord:** `nevindetto`
