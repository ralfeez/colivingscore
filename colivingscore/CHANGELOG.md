# CoLivingScore — Changelog

All notable changes to this project are recorded here in reverse chronological order.

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
