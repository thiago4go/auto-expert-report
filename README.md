
# AI‑Powered Study‑Guide Generator

Generate comprehensive, five‑chapter study guides on any subject—complete with tables, charts, and **responsive HTML output** ready for static hosting.

---

## ✨ Key Features

| Capability                              | Tech / Library | Notes |
|-----------------------------------------|----------------|-------|
| **CLI**                                 | Typer          | Beautiful `--help`, auto‑completion | citeturn0search4
| **Async Perplexity API**                | httpx + asyncio| Connection pooling, HTTP/2 | citeturn0search1
| **Retry Logic**                         | tenacity       | Exponential back‑off | citeturn0search3
| **Data Models**                         | Pydantic v2    | Type‑safe parsing | citeturn0search2
| **Caching**                             | aiocache       | In‑memory / Redis back‑ends | citeturn0search5
| **Markdown → HTML**                     | Markdown‑it‑py | Fast conversion | citeturn0search0
| **Templating & Layout**                 | Jinja2         | Componentised pages | citeturn0search2
| **Styling**                             | Tailwind CSS   | Utility‑first; built once via `npm` | citeturn0search4turn0search9
| **Static Site Build**                   | MkDocs (optional) | `mkdocs build` → `site/` | citeturn0search1turn0search6
| **HTML Minification**                   | `minify-html`  | Tiny payloads | citeturn0search3turn0search8

---

## Architecture

```text
CLI (Typer) / UI (Streamlit)
            │
            ▼
   ┌─────────────────────┐
   │ Task Scheduler      │
   │  • httpx.AsyncClient│
   │  • tenacity retries │
   └────────┬────────────┘
            ▼
   ┌─────────────────────┐
   │ Perplexity Sonar    │  (cost‑aware model choice)
   └────────┬────────────┘
            ▼
   ┌─────────────────────┐
   │ Post‑Processor      │  Pydantic → pandas
   └────────┬────────────┘
            ▼
   ┌─────────────────────┐
   │ Renderer            │  Markdown → HTML (Jinja2 + Tailwind)
   │  • minify-html      │
   └─────────────────────┘
            ▼
        site/<topic>/index.html
```

---

## Getting Started

### Prerequisites

* **Python 3.11+**
* **Node >= 18** for Tailwind build (only when styling changed) citeturn0search4
* Perplexity API key (`PPLX_API_KEY`)

### Installation

```bash
git clone https://github.com/<you>/study‑guide‑generator.git
cd study‑guide‑generator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# build Tailwind once (if you customize CSS)
npm install && npm run build:css
```

### CLI Usage

```bash
python -m studyguide "Machine Learning Basics" --audience beginner
# ⇒ static files under site/machine-learning-basics/
```

### Streaming Preview (Live‑reload)

```bash
streamlit run app/preview.py
```

---

## Configuration

| Variable            | Description                | Default |
|---------------------|----------------------------|---------|
| `PPLX_API_KEY`      | Your Perplexity token      | – |
| `TOKEN_BUDGET_USD`  | Max spend per run          | `0.25` |
| `SITE_DIR`          | Output root for HTML pages | `site` |

---

## Development Workflow

1. **Format & lint** – `ruff format && ruff check .` citeturn0search4  
2. **Tests** – `pytest -q` (coroutines via pytest‑asyncio). citeturn0search5  
3. **Docs** – `mkdocs serve` for live preview. citeturn0search6  
4. **Pre‑commit** – hooks run Black, Ruff, and tests before each push.

---

## Roadmap (Excerpt)

| Phase | Focus                              | ETA |
|-------|------------------------------------|-----|
| 3     | Tailwind + Jinja2 templates        | T + 21 d |
| 4     | mkdocs static build + sitemap      | T + 30 d |
| 5     | S3/CloudFront deploy script        | T + 38 d |

---

## Contributing

Please review `.clinerules` before starting work—style, testing, and review expectations live there.

---

## License

MIT
```