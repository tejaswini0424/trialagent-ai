# TrialAgent AI

A Multi-Agent Framework for Automated Clinical Trial Protocol Analysis and Regulatory Documentation Review.

TrialAgent AI is a local academic research application that screens protocol documents for explicit information, missing documentation and potential inconsistencies. It supports human reviewers; it does not determine clinical validity, grant approval, or certify regulatory compliance.

## Problem and objectives

Manual protocol review requires comparing design, eligibility, safety and documentation across sections. This project separates those tasks into seven inspectable agents, preserves evidence, and combines their outputs in a user-specific review workspace. Objectives are reproducible offline screening, transparent agent execution, traceable findings, and downloadable documentation.

## Installation and execution

Python 3.11 or 3.12 is the intended environment. This workstation supplied Python 3.14.6, on which the project was also tested. No API key, paid service or model download is required.

```powershell
cd "C:\Users\LENOVO\OneDrive\Documents\ChatGPT\trialagent AI\TrialAgent_AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m compileall -q .
pytest -v
streamlit run app.py
```

Open http://localhost:8501. If the `streamlit` command is not on PATH, use `python -m streamlit run app.py`. Register any non-empty username and password, log in, then select **Upload Clinical Protocol**. Enable the synthetic demonstration checkbox and click **Analyze protocol**, or upload PDF, DOCX or UTF-8 TXT. Select the document on review pages to inspect results and download reports. Logout clears the Streamlit session.

Optional configuration: copy `.env.example` to `.env`. `TRIALAGENT_DB` sets the SQLAlchemy SQLite URL, `MAX_UPLOAD_MB` sets the ingestion limit, and `APP_TIMEZONE` selects the header timezone (default Asia/Kolkata). The uploader/server default is 20 MB; adjust `.streamlit/config.toml` as well when changing that limit. The default database is created in the working directory. Run commands from this project directory.

## Methodology and architecture

1. Validate file format, size, content and hash; extract text and source PDF pages.
2. Extract explicit protocol fields using local rules and Pydantic validation.
3. Run design, eligibility, safety and configurable documentation reviews.
4. Compare explicit enrollment totals, dates, primary endpoints and references.
5. Consolidate findings and grounded narrative summaries.
6. Persist latest analysis and append review history in a single database transaction.
7. Explore findings and export PDF, CSV or JSON.

| Agent | Responsibility |
|---|---|
| Protocol Extraction | Title, phase, objectives, sponsor, population, eligibility, enrollment mentions, duration, endpoints, treatment and dose text |
| Study Design | Allocation, masking, control, endpoint and sample-size-justification screening |
| Eligibility | Duplicate and ambiguous criteria, potential inclusion/exclusion overlaps, TF-IDF similarity suggestions |
| Safety Review | Safety monitoring, AE/SAE reporting, stopping rules and committee documentation |
| Regulatory Review | Versioned, configurable topic-level research checklist with evidence and status |
| Consistency | Enrollment mismatch, start/end ordering, differing primary endpoints, explicit outcome-term mismatch, eligibility overlap and missing section targets |
| Report Generation | Structured local explanations, executive summary and human-review priorities |

Each agent is a separate module with a `run(document, context)` interface. The orchestrator records inputs, output, attempts, duration, errors and status. It retries once on error; independent agents continue after failure. Eligibility is skipped if extraction is unavailable. Report consolidation continues with available outputs. A partial review is labeled Partial, never Completed. Pending/Running states appear during execution; final records distinguish Completed, Failed and Skipped.

The workflow graph is a processing-order visualization; it is not a distributed execution engine. Execution is synchronous within the user's Streamlit session. Agents use deterministic rules; no autonomous language model reasoning is claimed. TF-IDF cosine similarity provides basic machine-learning-assisted eligibility wording review without training or downloading a model.

## Dashboard and features

Fourteen functional pages cover overview metrics, upload, protocol analysis, agent activity, study design, eligibility, safety, regulatory review, consistency, findings, document viewer, downloads, history and settings. The navy/teal interface includes Plotly charts, NetworkX workflow visualization, execution cards, document selection and evidence details. Overview values aggregate the user's latest persisted document analyses; history separately lists each saved review run. Present checklist records count toward total findings but are excluded from issue severity charts and review-signal counts.

Findings can be filtered by severity, agent, category and status, searched, inspected and exported. Document selection scopes review pages. PDF source pages are retained; TXT and DOCX deliberately have no invented page numbers. The viewer highlights literal evidence where practical. PDF reports include protocol overview, agent summaries, severity distribution, checklist findings, evidence, review actions and limitations; JSON contains the complete structured output.

## Checklist source and configuration

`data/regulatory_checklist.json` contains research checklist v1.0 with 12 categories. Each item includes an ID, requirement, source, source version, guidance and local matching patterns. The configured topic-level source is [ICH E6(R3), Principles and Annex 1, final adopted 6 January 2025](https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf). This is a pinned research source, not a complete jurisdiction-specific or continuously updated checklist. No invented regulatory section numbers are used.

Settings validates edited checklist JSON for future analyses in the current session. To change the persistent default, edit the local JSON file. All required patterns found -> Present; some found -> Unclear; none found -> Missing. A configured `not_applicable: true` yields Not Applicable. Free-form comparison signals use Needs Human Review. Present indicates text detection only, not adequacy or compliance. Negated documentation statements are excluded from positive matches. Each analysis embeds its checklist to retain provenance.

## Storage and authentication

SQLite/SQLAlchemy tables: users, documents, agent_results, findings and analysis_history. All document reads/writes are scoped to the authenticated user. Duplicate detection uses SHA-256 per user; reanalysis updates latest findings and appends history. Uploaded bytes are processed in memory; extracted text, metadata and analysis are stored in SQLite, not original binary documents. Empty, encrypted, corrupted, oversized and unsupported files produce visible errors.

Passwords are SHA-256 prehashed and then bcrypt-hashed, allowing arbitrary non-empty Unicode/long passwords without bcrypt's 72-byte limitation. Plaintext passwords are never persisted. Usernames are exact and case-sensitive. Authentication state is session-local. This is a local research system, without enterprise identity management, account recovery, rate limiting, database encryption or formal production hardening. Keep real sensitive data out of a demonstration installation.

## Folder structure

```text
TrialAgent_AI/
  app.py, requirements.txt, README.md, .env.example, .gitignore, pytest.ini
  .streamlit/config.toml
  config/                 settings and checklist loader
  backend/
    authentication/       bcrypt authentication
    database/             models, connection, ownership-scoped operations
    document_processing/  PDF/DOCX/TXT extraction and evidence helpers
    agents/               seven specialized agent modules
    orchestration/        execution tracking, retries and workflow
    analysis/             finding schema and local explanations
    reports/              PDF and CSV generation
  frontend/               dashboard, components and theme
  data/                   synthetic protocol and research checklist
  uploads/                reserved local directory
  reports/                generated demonstration artifacts (ignored by git)
  tests/                  authentication, extraction, agents, reports, UI and isolation
```

## Technologies and dependencies

Streamlit, Pandas, NumPy (via analytical dependencies), scikit-learn, NetworkX, PyMuPDF, python-docx, Pydantic, SQLAlchemy, bcrypt, Plotly, ReportLab, pytest and python-dotenv. A lightweight custom orchestrator replaces LangChain. Exact resolved versions for this verification are in `requirements-tested.txt`; `requirements.txt` supplies compatible minimums and the Streamlit major bound.

## Testing

```powershell
python -m compileall -q .
pytest -v
```

Tests isolate SQLite in `.pytest-tmp` and cover registration, bcrypt storage, duplicate usernames, arbitrary non-empty credentials, access denial, duplicate documents, PDF/DOCX/TXT extraction, invalid files, extraction fields, study-design/safety/eligibility checks, checklist applicability and negative text, consistency, retries, failed/skipped agents, reports, CSV formula escaping, all fourteen pages, and registration/login/logout/sample-upload UI workflows. `pytest.ini` keeps temporary test files inside the project because this workstation's sandbox blocks some system temporary-directory operations.

## Limitations and future enhancements

Rules depend on recognizable English labels and formatting and can miss paraphrases, tables with broken reading order, complex eligibility logic and semantic contradictions. Evidence absence means text was not located, not proof of omission or violation. Committee names, dates and dosage information are extracted only when detectable. Sample-size counts can differ legitimately by cohort; endpoint descriptions may differ legitimately by context. Every signal needs interpretation. No clinical or regulatory expert evaluation, benchmark accuracy study, OCR, scanned-document support, semantic LLM, production deployment, encryption-at-rest or cross-document version comparison is included.

Future work: expert-labeled evaluation with precision/recall, richer heading/table parsing, jurisdiction-specific checklists reviewed by professionals, OCR, optional grounded local models, protocol-version comparison and independently reviewed security hardening.

## Verification performed

On 7 November 2026: all direct requirements were available, `python -m compileall -q .` passed, and `pytest -q` passed **39 tests in 23.45 seconds** on Python 3.14.6. The Streamlit server started at 127.0.0.1:8501 and its `/_stcore/health` endpoint returned `ok`. Streamlit AppTest exercised all 14 pages plus registration/login/logout and the synthetic upload workflow. The synthetic protocol completed all seven agents and produced 23 finding records. Its eight-page PDF was rendered with PyMuPDF and visually inspected. Python 3.11/3.12 were not installed on this workstation, so those versions were not executed here. Earlier sandbox temporary-directory cleanup warnings were resolved for the final test run by configuring workspace-local test temporary storage.

## Vercel web deployment

Production URL: https://trialagent-ai.vercel.app

The hosted edition uses the same seven Python analysis agents behind a FastAPI API and a responsive browser dashboard in `web/`. Authentication uses bcrypt plus HTTP-only, Secure, SameSite=Strict signed session cookies. Sessions expire after eight hours. State persists in a dedicated Neon PostgreSQL database on the free plan, in Singapore. Browser clients never receive the database URL or signing key. Database connection URLs and SESSION_SECRET are managed as Vercel environment variables. The hosted database starts separately from the local SQLite installation; existing local accounts/documents are not uploaded or migrated.

The web edition supports all fourteen review views, registration/login/logout, drag/drop upload, synthetic analysis, reanalysis with a session-specific checklist, findings filters and CSV export, PDF source pages and evidence highlighting, execution logs, history, and PDF/CSV/JSON downloads. The hosted request/upload limit is 4 MB. Optional scikit-learn TF-IDF near-duplicate suggestions are omitted from the smaller deployment bundle; deterministic eligibility duplicate, ambiguity and overlap checks remain enabled. Native browser severity charts replace Plotly in the cloud UI. For text-based extraction, evidence provenance and human-review limitations, the same research caveats apply.

Run the web edition locally:

```powershell
pip install -r requirements-web.txt
python -m uvicorn web.api:app --host 127.0.0.1 --port 8503
```

For local web development SQLite is supported and a temporary signing key is generated at process start unless SESSION_SECRET is configured. Production refuses to start with SQLite or without a signing key.

Deployment packages are generated from shared source into the ignored `.deploy/` directory; local SQLite files, credentials, uploads, tests, and generated reports are excluded. The deployment Python target is 3.12.

```powershell
python scripts/package_vercel.py
$env:NODE_OPTIONS="--use-system-ca"
npm.cmd exec --yes --package=vercel -- vercel deploy --prod --yes --cwd .deploy --scope tejaswini0424b-3241
```

The Node option uses Windows system certificates and is only needed on machines where the normal Node CA store cannot validate the network certificate chain. No certificate validation is disabled. First-time setup requires linking `.deploy/` to the Vercel project and configuring PostgreSQL DATABASE_URL and a cryptographically random SESSION_SECRET; do not commit or print those values. The deployment uses the account's existing Neon integration and a dedicated free-tier `trialagent-db` resource. No paid plan was selected. Free-tier quotas and cold starts can affect response times.

### Cloud verification

The Vercel production build reached READY on 7 November 2026. `/api/health` returned `ok` and PostgreSQL. With explicit user authorization, the synthetic-only `deployment-check-20261107` account was created for deployment verification; sign-in succeeded, all seven agents completed the sample review, and the PDF downloaded successfully. The combined regression suite passed **43 tests in 25.27 seconds** with one third-party AnyIO deprecation warning. The production test account is separate from the user's own account; create a new account for personal use. Registration and sign-in do not migrate local SQLite users.
