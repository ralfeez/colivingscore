# CoLivingFurnish — Design Spec
**Date:** 2026-05-01  
**Status:** Approved — ready for implementation planning

---

## Overview

CoLivingFurnish is a standalone web-based furnishing estimator for co-living property operators. The operator enters a property address, specifies beds/baths, selects a tenant type and climate zone, then receives a room-by-room checklist with required and optional items, price ranges, affiliate links, a budget tracker, and a printable checklist export.

---

## Approach

**Enhance the existing prototype directly.** `CoLivingFurnish.html` (the design handoff prototype) is the base. The implementation wires in the real CSV, adds optional-item filtering, adds mobile responsive CSS, and adds the print export. All existing design tokens, component styles, animations, and UI patterns carry over unchanged from the prototype.

---

## Deployment

- **Type:** Standalone static site — independent URL, not part of colivingscore.onrender.com
- **Hosting:** Netlify (free tier) — drag-and-drop deploy, no CI/CD required for v1
- **Files:** Two files in one folder: `index.html` + `furnishings.csv`
- **No backend, no build step, no accounts required**

---

## File Structure

```
colivingfurnish/
├── index.html          # All UI and logic (React via CDN, Babel in-browser)
└── furnishings.csv     # Product data — loaded at runtime via PapaParse fetch
```

---

## Data Layer — CSV Schema

The app fetches `furnishings.csv` on init using PapaParse. The CSV is the single source of truth for all product data.

### Columns used by the app

| Column | Maps to | Notes |
|---|---|---|
| `Room / Area` | Room grouping | Groups items into accordion sections |
| `Item` | Display name | Shown in item row |
| `Notes` | Helper text | Shown below item name in small muted text |
| `Min Quantity per Bedroom` | Bed multiplier | If > 0, price and budget scaled by # of bedrooms |
| `Min Quantity per Bath` | Bath multiplier | If > 0, price and budget scaled by # of bathrooms |
| `Min Quantity per home` | Home qty | Fixed quantity, not scaled by beds/baths |
| `Quantity per window` | Per-window flag | If > 0, item shows price as "$X–$Y per window" (no multiplier applied) |
| `Required` | Show always flag | `Yes` = always visible regardless of selections; `No` = filtered |
| `Affiliate URL` | Product link | "Find →" button opens in new tab |
| `Cost Each` | Base price (low) | Price range = low → low × 1.3. Window items minimum $20. |
| `tenant_types` | Optional filter | **New column.** Required items: leave blank. Optional items: `all` or comma-separated e.g. `seniors,sober` |
| `climate_zones` | Optional filter | **New column.** Required items: leave blank. Optional items: `all` or comma-separated e.g. `cold,temperate` |

### Columns dropped

| Column | Reason |
|---|---|
| `Cost` | App calculates totals live |
| `Number in Pkg` | Already factored into `Cost Each` |
| `Required Cost` / `Optional Cost` | App computes budget from checked state |

### Row IDs

Auto-generated from row index at parse time. No `id` column needed. localStorage state is keyed by `address + row index`.

---

## Filtering Logic

```
Required = Yes  →  always show, regardless of tenant_type or climate_zone
Required = No   →  show only if:
                     (tenant_types is blank OR tenant_types includes "all" OR tenant_types includes selected type)
                     AND
                     (climate_zones is blank OR climate_zones includes "all" OR climate_zones includes selected climate)
```

**Important:** A blank `tenant_types` or `climate_zones` on an optional item means it shows for all selections (i.e. blank = "all"). Operators can leave these blank on optional items they want universally shown.

---

## Optional Item → Tenant Type / Climate Mapping (v1)

These are the initial assignments baked into the CSV. More can be added over time.

### Climate: Cold
- Register booster fan (bedroom)
- Electric tea kettle (kitchen)
- Extra blanket / throw *(new item)*
- Draft stopper *(new item)*
- Space heater *(new item)*

### Climate: Hot
- Tower / portable fan (bedroom) *(new item)*
- Cooling mattress pad *(new item)*
- Blackout shades — heat blocking *(new item)*

### Tenant: Students
- Fabric storage cubes
- Rolling shelving unit
- Under-bed storage
- Whiteboard / corkboard *(new item)*
- Bike hook / storage *(new item)*

### Tenant: Professionals
- WiFi mesh / router upgrade
- Noise monitor
- Monitor stand / riser *(new item)*
- USB-C charging hub *(new item)*
- Desk lamp *(new item)*

### Tenant: Nurses / Trades (shift workers)
- Blackout drapes
- Register booster fan
- White noise machine *(new item)*
- Eye mask + earplugs kit *(new item)*
- Mini fridge — bedroom *(new item)*

### Tenant: Digital Nomads
- WiFi mesh / router upgrade
- Monitor stand / riser *(new item)*
- USB-C charging hub *(new item)*
- Laptop stand *(new item)*
- Ring light *(new item)*

### Tenant: 55+ Seniors
- Side tables (living room)
- Storage ottoman
- Over-door hook organizer
- Puzzles & board games *(new item)*
- Reading / accent chair *(new item)*
- Grab bar — bathroom *(new item)*
- Non-slip bath mat (extra) *(new item)*

### Tenant: Sober Living
- Whiteboard / corkboard
- Storage ottoman
- Puzzles & board games *(new item)*
- Reading / accent chair *(new item)*
- Journaling kit *(new item)*
- Meditation cushion / yoga mat *(new item)*

---

## 4-Step Wizard

State saved to `localStorage` key `clf-project-v1` on completion.

```js
{ address, beds, baths, tenantType, climate }
```

| Step | Input | Validation |
|---|---|---|
| 1 — Address | Free-text input with 📍 icon | Continue enabled after 5+ chars |
| 2 — Beds & Baths | +/− counter widgets | Min 1 bed, 1 bath |
| 3 — Tenant Type | 7-card grid (students, professionals, seniors, nurses, trades, nomads, sober) | One selection required |
| 4 — Climate | 3 vertical cards (Cold, Temperate, Hot) | One selection required |

Step transitions: `fadeUp` animation (opacity 0→1, translateY 20→0, 0.5s ease). All design tokens, card styles, and animations unchanged from prototype.

---

## Dashboard

### Desktop (≥ 768px)
- Sticky top nav: logo left, address pill, Export button (terracotta), New Project button (ghost)
- Hero summary bar: charcoal gradient, beds/baths title, tag pills, progress ring
- 2-column grid: `240px sidebar | 1fr main`
- **Sidebar (sticky):** Room list buttons with mini progress bars + Budget Tracker card
- **Main:** Room accordions — one open at a time; click header to expand/collapse

### Mobile (< 768px)
- Simplified sticky header: property summary + progress %
- Horizontal scrolling room tab strip (replaces sidebar)
- Full-width room accordion below tabs
- Budget Tracker card below accordion
- All touch targets ≥ 44px

### Room Accordion
- **Collapsed:** white card, room icon + name + progress bar + %
- **Expanded header:** charcoal background, white text
- **Expanded body:** cream background, Room Notes card (italic Playfair Display, tenant-type story text), then Required section, then Optional section

### Item Row
- Checkbox (24px) + category color swatch (48px) + name + badge (req/opt) + notes + price range + "Find →" affiliate link
- **Checked state:** sage border + strikethrough name
- **Window items:** price displayed as `$20–$26 per window` (no multiplier)
- **Bed/bath items:** price displayed as `$X–$Y ×N` where N = bed or bath count

### Optional Section
- Collapsed by default; toggle button "OPTIONAL (N)" expands/collapses
- Header shows active filter tags e.g. `🎓 Students` `❄️ Cold`
- Only shows items matching the wizard selections (filtering logic above)

---

## Budget Tracker

Two progress bars in sidebar card (budget card stacks below accordion on mobile):

| Bar | Tracks | Color |
|---|---|---|
| Required (10px) | Required items only, scaled by beds/baths | Terracotta gradient |
| Optional Upgrades (6px) | Optional checked items | Sage gradient |

- **Right label:** "$X still needed" (terracotta) or "✓ Required complete" (sage)
- **Total committed** below divider: sum of all checked items (required + optional)
- Progress animates with `transition: width 0.4s ease`

---

## Export — Print Checklist

A **"Print Checklist"** button (alongside the Export clipboard button in the nav) opens a print-optimized view via `window.print()`.

### Print layout
- Clean single-column layout — no sidebar, no nav chrome
- Property header: address, beds/baths, tenant type, climate, date generated
- Rooms listed sequentially with:
  - **Required items:** name, price range, affiliate URL (printed as short URL or full)
  - **Selected optional items:** same format (only checked items included)
  - **Unchecked optional items:** omitted from print
- Budget summary at end: Required total range, Optional committed, Total committed
- Uses `@media print` CSS — `display:none` on nav, sidebar, wizard, modals

### Clipboard export (existing prototype behavior — unchanged)
- Copies formatted text list: STILL NEEDED (with links) + COMPLETED sections + budget summary

---

## State Management

| Key | Contents |
|---|---|
| `clf-project-v1` | `{ address, beds, baths, tenantType, climate }` |
| `clf-checked-{address}` | `{ [rowIndex]: boolean }` — checked state per property |

- "New Project" button: `window.confirm()` before clearing state
- On load: if `clf-project-v1` exists, skip wizard and restore dashboard

---

## Design Tokens

All unchanged from `CoLivingFurnish.html` prototype. Key values for reference:

```css
--cream: #faf7f2;  --charcoal: #1e1c18;  --terracotta: #c0603a;
--sage: #6b8c6e;   --amber: #e8a84a;     --text-muted: #7a7570;
```

Fonts: Playfair Display (headings, room notes) + DM Sans (body, labels) via Google Fonts CDN.

---

## Room Notes (Stories)

Each room accordion shows a short narrative card at the top when expanded. These are per-tenant-type text blurbs (e.g. a different tone for Students vs Nurses vs Seniors). For v1, the prototype's existing story text is kept as-is for all rooms. Stories live as a JS object in `index.html` — no separate CSV needed.

---

## Item Color Swatches

The prototype assigns swatches by a `category` field (Sleeping, Storage, Work, etc.). The user's CSV has no `category` column. For v1: swatches are assigned by **room** — each room gets a fixed color pair from the prototype's category palette (e.g. Bedroom → Sleeping colors `#e8d5c4 / #c4a882`, Kitchen → Appliances colors, etc.). This removes per-category variation but keeps the visual feel. A `category` column can be added to the CSV in v2 to restore full per-item swatch differentiation.

Room → swatch color mapping:
| Room | Swatch (light / dark) |
|---|---|
| Bedroom | `#e8d5c4` / `#c4a882` (Sleeping) |
| Shared kitchen | `#d8dce4` / `#7888a0` (Appliances) |
| Shared living room | `#e0d4c4` / `#a08060` (Seating) |
| Shared bathroom(s) | `#cce0e4` / `#5890a0` (Bath) |
| Laundry area | `#dce0e8` / `#7880a0` (Laundry) |
| Tech & safety | `#d0d8e8` / `#6878a8` (Tech) |
| Common area | `#dce4e0` / `#70a090` (Cleaning) |

---

## Out of Scope for v1

- Per-bedroom checklist instances (all bedrooms share one checklist)
- Shareable project URLs (URL encoding of project state)
- Auth / multi-project saving
- Image thumbnails in item rows
- Per-item category swatches (room-level swatches used instead)
- Google Places autocomplete on address field
