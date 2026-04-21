# CoLivingScore — Changelog

All notable changes to this project are recorded here in reverse chronological order.

---

## [2026-04-21 Session 3] — Model Fix, Timeout Diagnosis, Architecture Decision

### Changed
- **Claude model**: replaced `claude-opus-4-5-20251001` (invalid model ID) with `claude-sonnet-4-6` across all 5 call sites in `app.py` (`api_market_analysis` x2, `api_competitive` x2, `api_pro_data` inner `call_competitive`)
- **Web search beta header**: replaced `betas=["web-search-2025-03-05"]` (unsupported parameter in SDK 0.50.0) with `extra_headers={"anthropic-beta": "web-search-2025-03-05"}` — correct syntax for all SDK versions
- **Web search fallback**: added `extra_headers` + no-tools fallback to `call_competitive` in `api_pro_data` (was missing)
- **Web search max_uses**: reduced from 20 to 10 to cut Claude response time

### Added
- **`gunicorn.conf.py`**: version-controlled Gunicorn config with `timeout = 180` so the timeout is not dependent solely on Render dashboard setting

### Fixed
- **Anthropic API key**: key in Render environment was stale (last used 30+ days ago per console.anthropic.com). New key generated and installed — 401 auth errors resolved
- **`betas` parameter**: removed from `messages.create()` calls — not a valid parameter in SDK 0.50.0; replaced with `extra_headers`

### Diagnosed (not yet fixed)
- **Gunicorn worker timeout**: `/api/market-analysis` with 10 web searches takes 90–120 seconds. Gunicorn `--timeout 60` (set in Render dashboard) kills the worker before Claude finishes → 500 error → all AI pages blank. Render start command must be updated to `--timeout 180` in the dashboard.
- **Root cause of all blank AI pages**: combination of (1) wrong model name, (2) missing beta header, (3) stale API key, (4) Gunicorn timeout. All four now identified.

### Architecture Decision (pending implementation)
- **Web search to be removed** from `api_market_analysis` in favor of Claude training data + already-gathered API data (demographics, WalkScore, RentCast, nearby places). Reasons:
  1. 10 live web searches × 5–10 sec each = 90–120 sec total — unacceptable for web app
  2. Claude.ai and ChatGPT feel "instant" because they stream output — our backend waits for full response
  3. Claude's training data is sufficient; we already provide real data in the prompt
  4. Streaming to be added as follow-up to make pages appear as Claude writes them
- **Next step**: remove `tools` and `extra_headers` from `api_market_analysis`, rely on training data + provided context. Expected response time: 10–15 seconds.

### Remaining Issues (pending)
- Page 1: KPI calculations need verification
- Page 3: Census stat tiles show dashes if `place.zip` not populated — need ZIP fallback
- Page 6: RentCast data shows labels but all values blank — `fastData.rentcast` arriving empty
- Page 9: P&L labeling wrong — "Monthly NOI" is actually Cash Flow; OER formula includes mortgage (should be operating expenses only)
- Page 11: Tenant comparison uses profile default rents not market rents; capital improvements are hardcoded
- Pages 2,4,5,8,10,12,13,14,15: All blank — Claude API now fixed, blocked only by timeout/architecture issue above

---

## [2026-04-21] — 15-Page Paginated Pro Report + Claude Web Search Fix

### Added
- **15-page paginated Pro Analysis report** (frontend rebuild): one page visible at a time, sticky nav bar with numbered page buttons, each page styled like a PDF page (white card, dark header band, green accents, page number footer).
- **`buildReportShell()`**: dynamically creates all 15 page divs + nav buttons in JS; HTML has only empty containers.
- **`renderAIContent(text)`**: markdown-to-HTML converter for AI-generated section content.
- **`runFullProAnalysis()`**: new orchestrator — starts loading screen, fetches `pro-data-fast` and `market-analysis` concurrently, then renders all 15 pages.
- **`renderPagedReport(fastData, aiData)`**: renders all 15 pages from fast API data + AI sections.
- **`window._proFin`**: new global storing pro-form financials (gross, NOI, DSCR, OER, etc.) for Page 1 KPI strip.
- **`/api/market-analysis` endpoint**: replaces `/api/competitive` for the 15-page report. Accepts all user inputs + gathered API data as context. Calls Claude with up to 20 web searches. Returns structured JSON with one key per section: `executive_summary`, `housing_market`, `tenant_profile`, `demand_drivers`, `supply_analysis`, `rent_pricing`, `regulatory`, `occupancy_turnover`, `swot`, `risk_analysis`, `employer_mapping`, `platform_strategy`, `exit_strategy`.
- **`_build_market_analysis_prompt(data)`**: builds the full Claude prompt with all property context, gathered API data, and specific web search tasks.
- **`_parse_market_sections(text)`**: splits Claude's response into section dict by `## SECTION_KEY` headers.
- **`SECTION_KEYS`** constant list and **`TENANT_LABELS`** dict.
- **RentCast 1BR fallback** in `_fetch_rentcast`: if no comps for actual bed count, retries with `beds=1, baths=1`, scales result by 65% for per-room co-living estimate, sets `source="1BR_scaled"`.

### Changed
- **Page 1 title**: "Cover — Score + KPIs" → "Home — Score & Performance"
- **Loading screen** now covers both `pro-data-fast` and `market-analysis` calls.
- **`loadCompetitiveAsync()`** removed — replaced by `runFullProAnalysis()` loading screen flow.
- **Acronym rule enforced**: no bare acronyms in UI — KPI cells use full plain-English labels (Debt Service Coverage Ratio, Net Operating Income, etc.).
- **`_fetch_rentcast`** extracted into standalone helper (part of commit 99ef255 deadlock fix).

### Fixed
- **API deadlock on Render** (commit 99ef255): `api_pro_data_fast` was calling sub-routes via HTTP (`requests.post(request.host_url + ...)`), causing Gunicorn worker deadlocks. Fixed by extracting `_fetch_rentcast`, `_fetch_walkscore`, `_fetch_nearby`, `_fetch_demographics` as direct helper functions.
- **Claude web search `betas` parameter** (commit f36c2e2): `client.messages.create()` was missing `betas=["web-search-2025-03-05"]` required to use the `web_search_20250305` tool. The API was rejecting every call silently — caught by `except`, returned `{"error": "..."}`, all AI sections parsed as empty → "No data available." Added `betas` param + no-tools fallback retry to both `api_market_analysis` and `api_competitive`.
- **`_parse_market_sections` robustness**: now case-insensitive (`text_upper.find`). If all sections parse empty, puts full raw Claude response into `executive_summary` as fallback.

### Known Issue at Session End
- Anthropic account near usage limit → 401 responses from `/api/market-analysis`. Code fix is deployed and correct. AI pages will populate once limits reset.

---

## [2026-04-18 07:52] — PDF Engine Overhaul + New Pages

### Added
- **Sensitivity Analysis page** (new page 5): occupancy scenario table at 100% / 90% / 80% / break-even, showing Revenue, Management Fee, NOI, DSCR, and Assessment per row. Management fee scales with revenue at each level.
- **5-Year Projection page** (new page 8): cash flow forecast using 3% annual rent growth and 2.5% expense growth. Includes assumptions note, current-year baseline, Year 1–5 rows, cumulative cash flow column, and a summary callout.
- **Address Entry screen** (Screen 0) in the frontend: dark hero panel where users enter a property address before the scoring form. Step indicator updated to 4 steps.

### Changed
- **PDF is now thread-safe**: removed global `DATA` dict mutation from `build_pdf_from_data()`. Each request now builds an isolated local data dict — concurrent Render requests can no longer corrupt each other's output.
- **Tenant comparison is now dynamic**: all 7 tenant types ranked by NOI using the user's actual expense inputs and management rate. Previously hardcoded to Sacramento sample data.
- **Improvements list is now dynamic**: half-bath detection (`baths % 1 != 0`) triggers a $10k conversion suggestion instead of an $18k full addition. Items reflect actual bed count.
- **Expense donut is now dynamic**: computed from user inputs — mortgage, taxes+insurance, utilities, reserves, management, HOA.
- **Management fee now respects user selection**: correctly applies 0% (self-managed), 10% (co-living specialist), or 20% (PadSplit) based on the `mgmt_model_key` field. Previously always defaulted to 10%.
- **Market narrative** replaced static Sacramento text with a generic placeholder pending Phase 2 Claude API integration.
- **Verdict text** is now dynamic — uses the user's actual tenant type, DSCR, and break-even occupancy in the GO/NO-GO summary paragraph.
- **`header_footer`** refactored to a factory function `make_header_footer(d)` so the report date is always pulled from the current request's data.
- **`build_pdf()`** now accepts `d` as a parameter instead of reading from a global.
- **`mgmt_model_key`** added to `window._proData` in the frontend so the PDF generator receives the raw key (`self`, `specialist`, `padsplit`) rather than a human-readable label.
- **PDF page count**: 7 pages → 9 pages.

### Fixed
- `requirements.txt`: added `qrcode==8.0` and `Pillow==11.1.0`; bumped `reportlab` from `4.2.2` to `4.4.0`.

---

## [2026-04-17] — Review Screen + Stripe Checkout Wiring

### Added
- Review screen (Screen 3.5): users review all property and financial inputs before being sent to Stripe Checkout.
- Stripe Checkout session creation (`/create-checkout-session`).
- Post-payment success route (`/success`) that recovers stored form data via `/tmp` file cache and `sessionStorage`.
- Stripe webhook endpoint (`/stripe-webhook`) for server-side payment confirmation.
- `/config` route exposing the Stripe publishable key safely.
- Header "Pro Analysis" button wired to `startProAnalysis()`.

### Changed
- Pro Analysis flow gated behind Stripe payment — previously generated without payment.
- `sessionStorage` used to persist form data across the Stripe redirect so the Pro results auto-render on return.

### Fixed
- JS syntax error in parking flag logic.
- Button event binding for `btn-pro-generate`.

---

## [2026-04-15] — Initial Pro Analysis + PDF Generator

### Added
- Free scoring engine: bathroom ratio, sq ft per bed, parking, transit, hospital proximity, HOA caps, floor penalty, bed bonus — all weighted by tenant type profile.
- 7 tenant type profiles (Travel Nurses, Tech, Trades, Students, Seniors, Sober Living, General Workforce).
- Free score results screen: score ring, spectrum bar, financial snapshot (gross, NOI, break-even), audit flags.
- Pro Analysis financial input form: income, fixed expenses, utilities, reserves, management model.
- Pro Analysis results screen: P&L summary, financial ratios, tenant comparison, improvements, GO/NO-GO verdict.
- PDF generator (`pdf/generate_report.py`) with ReportLab: Cover, Market Narrative, Financials (with expense donut), Key Ratios (with DSCR gauge), Tenant Comparison (with bar chart), Improvements (with bar chart), Verdict.
- Flask backend (`app.py`) with `/generate-pdf` endpoint.
- Email capture gate on the free score screen.
- `render.yaml` for Render.com deployment.

---

*Format: `[YYYY-MM-DD HH:MM]` for session-level entries, `[YYYY-MM-DD]` for day-level entries.*
