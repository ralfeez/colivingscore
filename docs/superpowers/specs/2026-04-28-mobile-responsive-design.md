# Mobile Responsive Version — Design Spec
**Date:** 2026-04-28  
**Branch:** `mobile-responsive` (off `master`)  
**Status:** Approved, ready for implementation

---

## Goal

Build a fully standalone mobile version of CoLivingScore that covers the complete user flow — address entry, property form, free score, payment, and 16-page Pro report — optimized for phone screens. The live desktop site (`index.html`) must remain completely untouched.

---

## Architecture

### Files

| File | Change |
|------|--------|
| `colivingscore/static/index.html` | **No changes** — desktop site untouched |
| `colivingscore/static/index-mobile.html` | **New file** — full standalone mobile version |
| `colivingscore/app.py` | **Small addition** — User-Agent routing on the `/` route (~8 lines) |

### Routing Logic (`app.py`)

A shared helper `_is_mobile(request)` checks the `User-Agent` header for known mobile indicators (Android, iPhone, iPad, Mobile) and the `?mobile` override param:
- `?mobile=1` — forces mobile regardless of device
- `?mobile=0` — forces desktop regardless of device

Two routes use this helper:
- `/` — serves `index-mobile.html` to mobile, `index.html` to desktop (existing behavior)
- `/success` — post-payment redirect also serves the correct file based on device, so users landing back from Stripe on their phone get the mobile report view

### Branch & Deployment

- Development branch: `mobile-responsive` (off `master`)
- Second Render service points at `mobile-responsive` branch
- Preview URL is separate from the live site — beta testing on `master` is unaffected
- Merge to `master` only when beta is complete and mobile is fully tested

---

## Screens

### Screen 0 — Address Entry (`s-address`)

- Dark hero layout, full-width on mobile
- Address input stacks above the Analyze button (no side-by-side)
- Restore banner (saved report) stacks below input
- No structural changes from desktop — existing layout already works well at narrow widths

### Screen 1 — Property Form (`s-form`) — 3 Steps

The single-page form is split into 3 sequential steps with a progress indicator (filled dots + connecting lines) at the top. Each step has a Continue button and a Back link.

**Step 1 — Property Basics**
- Bedrooms, Bathrooms, Half Baths
- Square Footage, Stories, Laundry
- 2-column grid layout for paired fields

**Step 2 — Parking & Location**
- Garage, Carport, Uncovered parking
- HOA Status, Transit Proximity, Hospital Proximity
- 2-column grid layout

**Step 3 — Financials & Tenant**
- Monthly Mortgage (PITI)
- Target Tenant Type
- Rent Per Room / Month
- Assumption notice (condensed)
- Final button: "Calculate Score →"

All field values are collected in the same `window._inputs` object as the desktop — scoring and API calls are identical.

### Screen 2 — Free Score Result (`s-result`)

- Score circle centered at top
- Go/No-Go verdict chip below circle
- 2×2 KPI grid (Gross Revenue, Cash Flow, DSCR, Cap Rate)
- "Get My Pro Analysis →" full-width CTA button
- Edit Inputs and Score Another as text links below the button (saves space vs. buttons)

### Screen 3 — Pro Form / Upsell (`s-pro-form`)

- Same content as desktop
- Inputs stack to single column
- Sample Report PDF link retained

### Screen 4 — Review Screen (`s-review`)

- Summary of inputs in a scrollable list
- Email field and Pay button full-width
- "Confirm these are correct" label made prominent (larger, colored)

### Screen 5 — Loading Screen (`s-loading`)

- No changes needed — already full-screen overlay with centered content

### Screen 6 — Pro Report (`s-pro-report`)

**Navigation bar replaced with:**
- `← Prev` button | `Page N of 16` + page name | `Next →` button
- Swipe hint: "swipe left or right to navigate" (shown in small text below counter)
- Sticky to top of report area

**Swipe gestures:**
- `touchstart` / `touchend` event listeners on the report container
- Horizontal swipe > 50px triggers `nextReportPage()` or `prevReportPage()`
- Vertical scrolling within a page is unaffected

**Page content:**
- All 16 pages render the same content as desktop
- Financial tables scroll horizontally on overflow (CSS: `overflow-x: auto`)
- Font sizes slightly reduced for dense sections (11px → 10px for table cells)

---

## Data & Logic

- All JS logic (scoring, API calls, report generation, Stripe flow) is copied verbatim from `index.html` into `index-mobile.html`
- No shared JS file — mobile file is fully self-contained
- All API endpoints are shared: `/api/pro-data-fast`, `/api/market-analysis`, `/create-checkout-session`, `/success`, `/save-email`
- `window._inputs`, `window._proInputs`, `window._fastData`, `window._aiData` globals work identically
- localStorage persistence and restore banner work identically
- Upstash Redis cache, API key gating, and rate limiting all apply equally
- Post-payment re-access email link is device-agnostic (`/?session_id=cs_xxx`) — tapping on phone serves mobile view, clicking on desktop serves desktop view automatically

---

## Testing

| Scenario | How to test |
|----------|-------------|
| Mobile view on desktop | Add `?mobile=1` to any URL on the preview Render service |
| Desktop view on phone | Add `?mobile=0` to URL |
| Full flow on phone | Open preview URL on phone — address → form → score → pay → report |
| Desktop regression | Open live site (`master` Render service) on desktop — must be unchanged |

---

## Out of Scope

- PDF download on mobile (same `window.print()` as desktop — mobile browsers handle this variably, acceptable for now)
- Tablet-specific layouts (phones only; tablets get desktop version)
- Push notifications or PWA features
- Any changes to `index.html`
