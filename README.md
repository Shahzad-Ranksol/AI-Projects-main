# CrewAI Content Generator Agents (FastAPI + Next.js)
CrewAI Content Generator Agents with  Flow


A two-part project for AI-assisted content generation:
- **Backend:** FastAPI service using [CrewAI](https://github.com/joaomdmoura/crewai) and Serper for research + content orchestration.
- **Frontend:** Next.js (TypeScript, Tailwind, shadcn/ui) interface.

> Generated README on 2025-09-17. Keep it updated as the code evolves.

---

## Monorepo Layout

```
├── Content_Generator_Agents_BackEnd_FastApi/
│   ├── .gitignore
│   ├── .python-version
│   ├── example.env
│   ├── main.py
│   ├── pyproject.toml
│   ├── README.md
│   └── uv.lock
└── Content_Generator_Agents_FrontEnd_NextJs/
    ├── public/
    │   ├── file.svg
    │   ├── globe.svg
    │   ├── next.svg
    │   ├── vercel.svg
    │   └── window.svg
    ├── src/
    │   ├── app/
    │   │   ├── favicon.ico
    │   │   ├── globals.css
    │   │   ├── layout.tsx
    │   │   └── page.tsx
    │   ├── components/
    │   │   ├── ui/
    │   │   │   ├── accordion.tsx
    │   │   │   ├── alert-dialog.tsx
    │   │   │   ├── alert.tsx
    │   │   │   ├── aspect-ratio.tsx
    │   │   │   ├── avatar.tsx
    │   │   │   ├── badge.tsx
    │   │   │   ├── breadcrumb.tsx
    │   │   │   ├── button.tsx
    │   │   │   ├── calendar.tsx
    │   │   │   ├── card.tsx
    │   │   │   ├── carousel.tsx
    │   │   │   ├── chart.tsx
    │   │   │   ├── checkbox.tsx
    │   │   │   ├── collapsible.tsx
    │   │   │   ├── command.tsx
    │   │   │   ├── context-menu.tsx
    │   │   │   ├── dialog.tsx
    │   │   │   ├── drawer.tsx
    │   │   │   ├── dropdown-menu.tsx
    │   │   │   ├── form.tsx
    │   │   │   ├── hover-card.tsx
    │   │   │   ├── input-otp.tsx
    │   │   │   ├── input.tsx
    │   │   │   ├── label.tsx
    │   │   │   ├── menubar.tsx
    │   │   │   ├── navigation-menu.tsx
    │   │   │   ├── pagination.tsx
    │   │   │   ├── popover.tsx
    │   │   │   ├── progress.tsx
    │   │   │   ├── radio-group.tsx
    │   │   │   ├── resizable.tsx
    │   │   │   ├── scroll-area.tsx
    │   │   │   ├── select.tsx
    │   │   │   ├── separator.tsx
    │   │   │   ├── sheet.tsx
    │   │   │   ├── sidebar.tsx
    │   │   │   ├── skeleton.tsx
    │   │   │   ├── slider.tsx
    │   │   │   ├── sonner.tsx
    │   │   │   ├── switch.tsx
    │   │   │   ├── table.tsx
    │   │   │   ├── tabs.tsx
    │   │   │   ├── textarea.tsx
    │   │   │   ├── toggle-group.tsx
    │   │   │   ├── toggle.tsx
    │   │   │   └── tooltip.tsx
    │   │   ├── content-generator-form.tsx
    │   │   ├── loading-spinner.tsx
    │   │   ├── made-with-dyad.tsx
    │   │   └── result-card.tsx
    │   ├── hooks/
    │   │   └── use-mobile.tsx
    │   └── lib/
    │       └── utils.ts
    ├── .gitignore
    ├── AI_RULES.md
    ├── components.json
    ├── LICENSE
    ├── next.config.ts
    ├── package.json
    ├── pnpm-lock.yaml
    ├── postcss.config.mjs
    ├── README.md
    ├── tailwind.config.ts
    └── tsconfig.json
```

---

## Tech Stack

- **Backend:** Python 3.13, FastAPI, CrewAI, crewai-tools, Serper API
- **Frontend:** Next.js 14+, TypeScript, Tailwind CSS, shadcn/ui, pnpm lockfile present

---

## Prerequisites

- **Python** 3.13 (see `.python-version`)
- **Node.js** 18+ (LTS recommended) and **pnpm** (`npm i -g pnpm`)

---

## Backend (FastAPI)

**Path:** `Content_Generator_Agents_BackEnd_FastApi`

### Environment
Copy and edit the example env (replace with your keys):
```
GOOGLE_API_KEY=<your_google_api_key>
SerperKey=<your_serper_api_key>
```

### Install
Option A — quick install with `pip` from requirements file:
```bash
cd Content_Generator_Agents_BackEnd_FastApi
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Option B — explicit packages (if you prefer):
```bash
pip install "fastapi[standard]>=0.116.1" crewai>=0.186.1 crewai-tools
```

> This backend uses a `pyproject.toml` with PEP 621 metadata. A `requirements.txt` is also provided for convenience.

### Run (dev)
```bash
# either
fastapi dev main.py          # provided by fastapi[standard]
# or
uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000` with docs at `http://127.0.0.1:8000/docs`.

### API

#### `POST /generate-content`
Generate text content for a given URL and target channel.

**Body (JSON):**
```json
{
  "url": "https://example.com/some-article",
  "content_type": "linkedin"  // one of: blog | newsletter | linkedin | facebook | x
}
```

#### `POST /generate-content-with-image`
Generate text + an AI image suggestion.

**Body (JSON):**
```json
{
  "url": "https://example.com/some-article",
  "content_type": "linkedin",
  "image_prompt_override": null,
  "aspect_ratio": "16:9"  // e.g. "16:9", "1:1", "4:5"
}
```

> Environment variables used: `GOOGLE_API_KEY`, `SerperKey`.

---

## Frontend (Next.js)

**Path:** `Content_Generator_Agents_FrontEnd_NextJs`

### Install & Run
```bash
cd Content_Generator_Agents_FrontEnd_NextJs
pnpm install
pnpm dev
# open http://localhost:3000
```

> The codebase does not currently reference a backend base URL via env. If you introduce API calls, consider using `process.env.NEXT_PUBLIC_API_BASE` and a `.env.local` file.

---

## Development Tips

- Commit a `.env.example` (no secrets) for both apps.
- Keep API keys out of source control; add `.env` to `.gitignore` (already present).
- Prefer `pnpm` for the frontend to match the lockfile.
- Type-check (`tsc`) and lint (`next lint`) before pushing.

---

## Project Scripts (suggested)

- **Backend:** add `dev` script via [`uvicorn`] or `fastapi` in a `Makefile` or `taskfile`.
- **Frontend:** `dev`, `build`, `start`, `lint` are already present in `package.json`.

---

## GitHub Repo Setup (quick checklist)

- [ ] Add a repository description and topics: `fastapi`, `nextjs`, `crewai`, `generative-ai`, `content`.
- [ ] Protect `main` (require PR reviews and status checks).
- [ ] Create GitHub Actions for CI (Python/Node install + lint + type check).
- [ ] Add issue and PR templates (`.github/ISSUE_TEMPLATE/*`, `.github/PULL_REQUEST_TEMPLATE.md`).
- [ ] Choose a license (MIT/Apache-2.0).

---

## Project Structure Details

- **Backend key files**
  - `main.py` — FastAPI app with `/generate-content` and `/generate-content-with-image`
  - `pyproject.toml` — Python 3.13, deps: `crewai`, `crewai-tools`, `fastapi[standard]`
  - `.python-version` — `3.13`
  - `.gitignore` — Python artifacts, virtual envs, `.env`

- **Frontend key files**
  - `package.json` — Next scripts: `dev`, `build`, `start`, `lint`
  - `pnpm-lock.yaml` — lockfile indicates `pnpm`
  - `next.config.ts`, `tsconfig.json`
  - `app/`, `components/` — UI (shadcn/ui components included)

---

## Contributing

1. Create a feature branch: `git checkout -b feat/short-description`
2. Commit changes: `git commit -m "feat: add X"`
3. Push: `git push origin feat/short-description`
4. Open a Pull Request

---

## License

Choose a license for your repository (MIT recommended for open-source).

