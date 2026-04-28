# Mobile Version Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone `index-mobile.html` served automatically to phone users via User-Agent routing in `app.py`, covering the full flow: address → 3-step form → free score → payment → 16-page Pro report with swipe navigation.

**Architecture:** `index.html` (desktop) is never touched. `index-mobile.html` is a full standalone copy of `index.html` restructured for phones — 3-step form, swipe-navigable report, touch-friendly layouts. Flask's `/` route detects mobile User-Agent and serves the correct file.

**Tech Stack:** Flask (Python), vanilla HTML/CSS/JS, Stripe, Google Places Autocomplete. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-04-28-mobile-responsive-design.md`

---

## File Map

| File | Action | What changes |
|------|--------|--------------|
| `colivingscore/app.py` | Modify | Add `_is_mobile()` helper; update `/` route to serve correct file |
| `colivingscore/static/index-mobile.html` | Create | Full standalone mobile version — copy of index.html, restructured |

> **Note:** `index.html` is NEVER modified. Every change in this plan is to `index-mobile.html` only (after Task 1 which touches `app.py`).

---

## Task 1: Create Branch + Add `_is_mobile()` Routing to `app.py`

**Files:**
- Modify: `colivingscore/app.py:111-113`

- [ ] **Step 1: Create the mobile-responsive branch**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git checkout -b mobile-responsive
```

Expected: `Switched to a new branch 'mobile-responsive'`

- [ ] **Step 2: Add `_is_mobile()` helper to `app.py`**

In `app.py`, find the line `@app.route("/")` (line 111). Insert this block immediately before it:

```python
def _is_mobile():
    """Return True if request should be served the mobile version.
    ?mobile=1 forces mobile; ?mobile=0 forces desktop; otherwise uses User-Agent."""
    override = request.args.get("mobile")
    if override == "1":
        return True
    if override == "0":
        return False
    ua = request.headers.get("User-Agent", "")
    return any(k in ua for k in ("Android", "iPhone", "iPad", "Mobile"))


```

- [ ] **Step 3: Update the `/` route to use `_is_mobile()`**

Replace:
```python
@app.route("/")
def index():
    return send_from_directory("static", "index.html")
```

With:
```python
@app.route("/")
def index():
    filename = "index-mobile.html" if _is_mobile() else "index.html"
    return send_from_directory("static", filename)
```

- [ ] **Step 4: Verify routing logic manually**

`index-mobile.html` doesn't exist yet — that's fine. Just confirm `app.py` is syntactically valid:

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore/colivingscore"
python -c "import app; print('OK')"
```

Expected output: `OK` (no import errors)

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/app.py
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Add _is_mobile() routing: serve index-mobile.html to phone users"
```

---

## Task 2: Create `index-mobile.html` Base Shell

**Files:**
- Create: `colivingscore/static/index-mobile.html`

- [ ] **Step 1: Copy `index.html` to `index-mobile.html`**

```bash
cp "C:/Users/Public/Documents/AI Apps/colivingscore/colivingscore/static/index.html" \
   "C:/Users/Public/Documents/AI Apps/colivingscore/colivingscore/static/index-mobile.html"
```

- [ ] **Step 2: Update the `<head>` — ensure mobile viewport meta exists**

In `index-mobile.html`, find `<head>` and confirm or add this line after `<meta charset="UTF-8">`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

If a `<meta name="viewport"` tag already exists, replace it with the line above.

- [ ] **Step 3: Add mobile base CSS**

In `index-mobile.html`, find the closing `</style>` tag of the main `<style>` block. Insert the following block immediately before it:

```css
/* ══ MOBILE BASE — applied to all screens ══ */
body { font-size: 15px; }
header { padding: 0 16px; height: 44px; }
.screen { padding: 0; }
input, select, button { font-size: 16px !important; } /* prevent iOS zoom on focus */
.btn-primary, .btn-outline { width: 100%; box-sizing: border-box; padding: 14px; font-size: 15px; }
.card { border-radius: 0; border-left: none; border-right: none; margin: 0; }
.addr-strip { padding: 10px 16px; }
```

- [ ] **Step 4: Verify the file loads**

Deploy is not available locally — skip to commit. The file will be verified on Render in Task 9.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/static/index-mobile.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Add index-mobile.html base shell with mobile viewport and base CSS"
```

---

## Task 3: Address Screen — Stack Input Above Button

**Files:**
- Modify: `colivingscore/static/index-mobile.html`

The address screen (`s-address`) has an `.addr-input-row` that lays out the input and button side by side. On mobile these need to stack vertically.

- [ ] **Step 1: Add mobile address screen CSS**

In `index-mobile.html`, find the mobile base CSS block added in Task 2. Append this immediately after it (still inside the same `<style>` block, before `</style>`):

```css
/* ══ SCREEN 0: ADDRESS ══ */
.addr-hero { padding: 32px 20px 40px; }
.addr-hero-title { font-size: 22px; line-height: 1.3; }
.addr-hero-sub { font-size: 13px; margin-bottom: 20px; }
.addr-input-row { flex-direction: column; gap: 10px; }
.addr-input-row input { width: 100%; box-sizing: border-box; font-size: 16px !important; padding: 14px 16px; }
.btn-addr { width: 100%; padding: 14px; font-size: 15px; }
#restore-banner { margin: 0 16px 16px; }
```

- [ ] **Step 2: Verify expected layout**

The address input should stack above the Analyze button with full-width on both. Verified on Render with `?mobile=1` in Task 9.

- [ ] **Step 3: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/static/index-mobile.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Mobile: stack address input above Analyze button"
```

---

## Task 4: Replace Property Form with 3-Step Stepped Form

**Files:**
- Modify: `colivingscore/static/index-mobile.html`

This is the most structural change. The existing `#s-form` has all 15 fields in a single `.field-grid`. We replace the card contents with 3 step containers and add step navigation JS.

- [ ] **Step 1: Add step indicator CSS**

In `index-mobile.html`, append to the mobile CSS block (before `</style>`):

```css
/* ══ SCREEN 1: STEPPED FORM ══ */
.step-indicator { display: flex; align-items: center; padding: 16px 20px 4px; gap: 0; }
.step-dot { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.step-dot.done { background: var(--green); color: #0a2416; }
.step-dot.active { background: white; color: #0a2416; }
.step-dot.future { background: #2a2f2c; color: #666; }
.step-line { flex: 1; height: 2px; }
.step-line.done { background: var(--green); }
.step-line.future { background: #2a2f2c; }
.step-panel { display: none; padding: 16px 20px; }
.step-panel.active { display: block; }
.step-heading { font-size: 17px; font-weight: 800; color: white; margin-bottom: 2px; }
.step-sub { font-size: 12px; color: rgba(255,255,255,0.45); margin-bottom: 16px; }
.step-field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.step-field { display: flex; flex-direction: column; gap: 4px; }
.step-field.full { grid-column: 1 / -1; }
.step-field label { font-size: 12px; color: rgba(255,255,255,0.65); font-weight: 600; }
.step-field select, .step-field input { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; padding: 10px 12px; color: white; font-size: 16px !important; font-family: var(--font); width: 100%; box-sizing: border-box; }
.step-continue { width: 100%; padding: 14px; background: var(--green); color: #0a2416; font-size: 15px; font-weight: 800; border: none; border-radius: 8px; cursor: pointer; font-family: var(--font); margin-top: 8px; }
.step-back { display: block; text-align: center; font-size: 12px; color: rgba(255,255,255,0.4); margin-top: 12px; cursor: pointer; background: none; border: none; width: 100%; font-family: var(--font); }
.step-assumption { font-size: 11px; color: rgba(255,255,255,0.35); line-height: 1.5; padding: 10px 12px; background: rgba(255,255,255,0.04); border-radius: 6px; margin-bottom: 12px; }
```

- [ ] **Step 2: Replace the form card contents in `#s-form`**

In `index-mobile.html`, find the `<div class="screen" id="s-form">` block. Keep the `.addr-strip` div at the top unchanged. Replace everything from `<div class="card">` through its closing `</div>` (which ends just before `</div>  <!-- end s-form -->`) with:

```html
    <div class="step-indicator" id="form-step-indicator">
      <div class="step-dot active" id="sdot-1">1</div>
      <div class="step-line future" id="sline-1"></div>
      <div class="step-dot future" id="sdot-2">2</div>
      <div class="step-line future" id="sline-2"></div>
      <div class="step-dot future" id="sdot-3">3</div>
    </div>

    <!-- Step 1: Property Basics -->
    <div class="step-panel active" id="step-1">
      <div class="step-heading">Property Basics</div>
      <div class="step-sub">Rooms, size, and layout</div>
      <div class="step-field-grid">
        <div class="step-field">
          <label>Bedrooms <span class="req">*</span></label>
          <select id="f-beds">
            <option value="1">1</option><option value="2">2</option><option value="3">3</option>
            <option value="4">4</option><option value="5" selected>5</option><option value="6">6</option>
            <option value="7">7</option><option value="8">8</option><option value="9">9</option>
            <option value="10">10</option><option value="11">11</option><option value="12">12</option>
          </select>
        </div>
        <div class="step-field">
          <label>Bathrooms <span class="req">*</span></label>
          <select id="f-baths">
            <option value="1">1</option><option value="2">2</option><option value="3" selected>3</option>
            <option value="4">4</option><option value="5">5</option><option value="6">6</option>
            <option value="7">7</option><option value="8">8</option><option value="9">9</option>
            <option value="10">10</option><option value="11">11</option><option value="12">12</option>
          </select>
        </div>
        <div class="step-field">
          <label>Half Baths</label>
          <select id="f-halfbaths">
            <option value="0" selected>None</option><option value="1">1</option>
            <option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option>
          </select>
        </div>
        <div class="step-field">
          <label>Sq Footage <span class="req">*</span></label>
          <input type="number" id="f-sqft" value="2480" min="500" max="10000">
        </div>
        <div class="step-field">
          <label>Stories</label>
          <select id="f-floors">
            <option value="1" selected>1 story</option>
            <option value="2">2 stories</option>
            <option value="3">3 stories</option>
          </select>
        </div>
        <div class="step-field">
          <label>Laundry</label>
          <select id="f-laundry">
            <option value="provided" selected>In-home W/D</option>
            <option value="pay">In-home coin-op</option>
            <option value="none">None</option>
          </select>
        </div>
      </div>
      <button class="step-continue" onclick="goToStep(2)">Continue →</button>
      <button class="step-back" onclick="showScreen('s-address')">← Back to address</button>
    </div>

    <!-- Step 2: Parking & Location -->
    <div class="step-panel" id="step-2">
      <div class="step-heading">Parking &amp; Location</div>
      <div class="step-sub">Parking, HOA, and proximity</div>
      <div class="step-field-grid">
        <div class="step-field">
          <label>Garage</label>
          <select id="f-garage">
            <option value="0">None</option><option value="1">1 car</option>
            <option value="2" selected>2 car</option><option value="3">3 car</option>
          </select>
        </div>
        <div class="step-field">
          <label>Carport</label>
          <select id="f-carport">
            <option value="0" selected>None</option><option value="1">1</option><option value="2">2</option>
          </select>
        </div>
        <div class="step-field">
          <label>Uncovered</label>
          <select id="f-uncovered">
            <option value="0" selected>None</option><option value="1">1</option>
            <option value="2">2</option><option value="3">3+</option>
          </select>
        </div>
        <div class="step-field">
          <label>HOA Status <span class="req">*</span></label>
          <select id="f-hoa">
            <option value="none" selected>No HOA</option>
            <option value="permits">HOA — permits</option>
            <option value="unclear">HOA — unclear</option>
            <option value="prohibits">HOA — prohibits</option>
          </select>
        </div>
        <div class="step-field">
          <label>Transit</label>
          <select id="f-transit">
            <option value="walkable" selected>Under 0.5 mi</option>
            <option value="close">0.5 – 1 mi</option>
            <option value="moderate">1 – 3 mi</option>
            <option value="far">Over 3 mi</option>
          </select>
        </div>
        <div class="step-field">
          <label>Hospital</label>
          <select id="f-hospital">
            <option value="close" selected>Under 2 mi</option>
            <option value="moderate">2 – 5 mi</option>
            <option value="far">Over 5 mi</option>
          </select>
        </div>
      </div>
      <button class="step-continue" onclick="goToStep(3)">Continue →</button>
      <button class="step-back" onclick="goToStep(1)">← Back</button>
    </div>

    <!-- Step 3: Financials & Tenant -->
    <div class="step-panel" id="step-3">
      <div class="step-heading">Financials &amp; Tenant</div>
      <div class="step-sub">Mortgage and target market</div>
      <div class="step-field-grid">
        <div class="step-field full">
          <label>Monthly Mortgage (PITI)</label>
          <input type="number" id="f-mortgage" value="2850" min="0">
        </div>
        <div class="step-field full">
          <label>Target Tenant Type <span class="req">*</span></label>
          <select id="f-tenant" onchange="updateRentDefault()">
            <option value="nurses" selected>Travel Nurses</option>
            <option value="tech">Tech / Remote Workers</option>
            <option value="trades">Construction / Trades</option>
            <option value="students">Students</option>
            <option value="seniors">Seniors 55+</option>
            <option value="sober">Sober Living</option>
            <option value="workforce">General Workforce</option>
          </select>
        </div>
        <div class="step-field full">
          <label>Rent Per Room / Month <span class="req">*</span></label>
          <input type="number" id="f-rent" value="1100" min="0">
          <div class="field-hint" style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:4px">Default based on tenant type — adjust for your market</div>
        </div>
        <div class="step-field full" id="f-tenant-note" style="display:none"></div>
      </div>
      <div class="step-assumption">Results assume you have already verified local zoning and occupancy requirements and that the home is in good to excellent condition.</div>
      <button class="step-continue" id="btn-calculate" onclick="calculateScore()">Calculate Score →</button>
      <button class="step-back" onclick="goToStep(2)">← Back</button>
    </div>
```

- [ ] **Step 3: Add `goToStep()` JS function**

In `index-mobile.html`, find the JS section near the bottom (inside the main `<script>` tag, after the `DOMContentLoaded` block). Add this function:

```javascript
function goToStep(n) {
  // Hide all panels
  document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
  // Show target panel
  const panel = document.getElementById('step-' + n);
  if (panel) panel.classList.add('active');

  // Update step indicator dots and lines
  for (let i = 1; i <= 3; i++) {
    const dot  = document.getElementById('sdot-' + i);
    const line = document.getElementById('sline-' + i);
    if (!dot) continue;
    dot.classList.remove('done', 'active', 'future');
    if (i < n)       { dot.classList.add('done');   dot.textContent = '✓'; }
    else if (i === n){ dot.classList.add('active');  dot.textContent = String(i); }
    else             { dot.classList.add('future');  dot.textContent = String(i); }
    if (line) {
      line.classList.remove('done', 'future');
      line.classList.add(i < n ? 'done' : 'future');
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
```

- [ ] **Step 4: Remove the old desktop form wiring for `btn-calculate`**

In `index-mobile.html`, find the existing event listener that wires up `btn-calculate`. It will look like:

```javascript
wire('btn-calculate', function(){ calculateScore(); });
```

or similar. Remove it — Step 3's button already calls `calculateScore()` via its `onclick` attribute.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/static/index-mobile.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Mobile: replace property form with 3-step stepped form"
```

---

## Task 5: Score Result Screen — Mobile Layout

**Files:**
- Modify: `colivingscore/static/index-mobile.html`

The score result screen (`s-result`) currently has a horizontal score ring + score info side by side. On mobile, stack vertically and simplify secondary actions.

- [ ] **Step 1: Add score result mobile CSS**

Append to the mobile CSS block in `index-mobile.html` (before `</style>`):

```css
/* ══ SCREEN 2: SCORE RESULT ══ */
.score-hero { flex-direction: column; align-items: center; text-align: center; padding: 24px 20px 16px; gap: 16px; }
.score-ring { flex-shrink: 0; }
.score-info { width: 100%; }
.score-tier { font-size: 16px; }
.spectrum { max-width: 100% !important; }
.fin-grid { grid-template-columns: 1fr 1fr; gap: 10px; padding: 0 16px 16px; }
.email-gate { margin: 0 16px 16px; }
.email-row { flex-direction: column; gap: 10px; }
.email-row input { width: 100%; box-sizing: border-box; }
#r-audit { margin: 0 16px 16px; }
/* Secondary actions as text links */
.mobile-secondary-actions { display: flex; justify-content: center; gap: 24px; padding: 8px 16px 20px; }
.mobile-secondary-actions a { font-size: 13px; color: rgba(255,255,255,0.5); cursor: pointer; text-decoration: none; }
```

- [ ] **Step 2: Add mobile secondary actions row below the Pro gate**

In `index-mobile.html`, find `<div id="r-pro-gate"></div>` in `#s-result`. Immediately after it, add:

```html
    <div class="mobile-secondary-actions">
      <a onclick="showScreen('s-form')">← Edit Inputs</a>
      <a onclick="window.open(window.location.origin+'/','_blank')">Score Another →</a>
    </div>
```

- [ ] **Step 3: Hide the existing desktop button row in mobile**

In `index-mobile.html`, find the `.btn-row` div at the bottom of `#s-result` (the one with the "← Score another property" button). Add `style="display:none"` to that div so it doesn't show on mobile:

```html
    <div class="btn-row" style="display:none">
```

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/static/index-mobile.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Mobile: score result screen — stacked layout and text-link secondary actions"
```

---

## Task 6: Pro Form + Review Screens — Mobile Layout

**Files:**
- Modify: `colivingscore/static/index-mobile.html`

- [ ] **Step 1: Add Pro form + review screen mobile CSS**

Append to the mobile CSS block in `index-mobile.html` (before `</style>`):

```css
/* ══ SCREEN 3: PRO FORM ══ */
.util-group { margin: 0 16px 12px; }
.field-grid { grid-template-columns: 1fr; }
#s-pro-form .card { padding: 20px 16px; }
#s-pro-form .btn-row { padding: 0 16px 20px; }

/* ══ SCREEN 4: REVIEW ══ */
#s-review .card { padding: 20px 16px; }
/* Make the yellow confirm banner larger and full-bleed on mobile */
#s-review > div[style*="fef3c7"] {
  margin: 0 0 8px;
  border-left: none;
  border-right: none;
  border-radius: 0;
  padding: 16px 20px;
}
#s-review > div[style*="fef3c7"] div[style*="font-size:14px"] {
  font-size: 16px !important;
  font-weight: 800 !important;
}
#s-review .btn-row { flex-direction: column; gap: 10px; padding: 0 16px 20px; }
#s-review .btn-row button { width: 100%; }
```

- [ ] **Step 2: Verify the banner element exists**

In `index-mobile.html`, the review screen (`#s-review`) has a yellow banner at the top (starting around the line after `.addr-strip`):

```html
<div style="background:#fef3c7;border:1px solid #fcd34d; ...">
  ...
  <div style="font-size:14px;font-weight:700;color:#92400e;...">Review your inputs before paying</div>
  ...
</div>
```

No HTML change needed — the CSS selectors in Step 1 target this existing element. Confirm this div is present in `index-mobile.html`; if it was removed by any earlier edit, restore it from `index.html`.

- [ ] **Step 3: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/static/index-mobile.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Mobile: pro form and review screens — single column, prominent confirm label"
```

---

## Task 7: Replace Report Tab Bar with Page Counter Navigation

**Files:**
- Modify: `colivingscore/static/index-mobile.html`

The desktop report has a `.rpt-nav` tab bar populated by `buildReportShell()`. On mobile, replace it with a counter bar (`← Prev | Page N of 16 | Next →`).

- [ ] **Step 1: Add mobile report navigation CSS**

Append to the mobile CSS block in `index-mobile.html` (before `</style>`):

```css
/* ══ SCREEN 6: PRO REPORT ══ */
.rpt-nav { display: none !important; }
.mobile-rpt-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px 6px;
  background: white;
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1px solid var(--gray-100);
}
.mobile-rpt-nav-arrow {
  font-size: 13px;
  font-weight: 700;
  color: var(--dark);
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font);
  padding: 6px 10px;
}
.mobile-rpt-nav-arrow:disabled { color: var(--gray-300); cursor: default; }
.mobile-rpt-counter { text-align: center; flex: 1; }
.mobile-rpt-counter-text { font-size: 13px; font-weight: 700; color: var(--gray-900); }
.mobile-rpt-counter-name { font-size: 10px; color: var(--gray-400); margin-top: 1px; }
.mobile-rpt-swipe-hint { text-align: center; font-size: 10px; color: var(--gray-300); padding-bottom: 4px; background: white; }
.rpt-page-body { overflow-x: auto; }
```

- [ ] **Step 2: Add the mobile nav bar HTML inside `#s-pro-report`**

In `index-mobile.html`, find `<div class="screen" id="s-pro-report">`. Immediately after the opening tag (before any existing children), insert:

```html
    <div class="mobile-rpt-nav" id="mobile-rpt-nav">
      <button class="mobile-rpt-nav-arrow" id="mobile-rpt-prev" onclick="prevReportPage()" disabled>← Prev</button>
      <div class="mobile-rpt-counter">
        <div class="mobile-rpt-counter-text" id="mobile-rpt-counter-text">Page 1 of 16</div>
        <div class="mobile-rpt-counter-name" id="mobile-rpt-counter-name">Overview</div>
      </div>
      <button class="mobile-rpt-nav-arrow" id="mobile-rpt-next" onclick="nextReportPage()">Next →</button>
    </div>
    <div class="mobile-rpt-swipe-hint">swipe left or right to navigate</div>
```

- [ ] **Step 3: Update `showReportPage()` to sync the mobile counter**

In `index-mobile.html`, find the `showReportPage(n)` function. Add this block at the end of the function, just before the closing `}`:

```javascript
  // Mobile counter sync
  const counterText = document.getElementById('mobile-rpt-counter-text');
  const counterName = document.getElementById('mobile-rpt-counter-name');
  const prevBtn     = document.getElementById('mobile-rpt-prev');
  const nextBtn     = document.getElementById('mobile-rpt-next');
  const pageData    = RPT_PAGES.find(p => p[0] === n);
  if (counterText) counterText.textContent = `Page ${n} of 16`;
  if (counterName && pageData) counterName.textContent = pageData[2]; // full page title
  if (prevBtn) prevBtn.disabled = (n === 1);
  if (nextBtn) nextBtn.disabled = (n === 16);
```

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/static/index-mobile.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Mobile: replace 16-tab report nav with Page N of 16 counter + Prev/Next"
```

---

## Task 8: Add Swipe Gestures to Pro Report

**Files:**
- Modify: `colivingscore/static/index-mobile.html`

- [ ] **Step 1: Add swipe gesture JS**

In `index-mobile.html`, find the `DOMContentLoaded` event listener block. At the end of that block (just before its closing `}`), add:

```javascript
  // Swipe gestures on Pro report
  (function() {
    let touchStartX = 0;
    let touchStartY = 0;
    const rpt = document.getElementById('s-pro-report');
    if (!rpt) return;
    rpt.addEventListener('touchstart', function(e) {
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
    }, { passive: true });
    rpt.addEventListener('touchend', function(e) {
      const dx = e.changedTouches[0].clientX - touchStartX;
      const dy = e.changedTouches[0].clientY - touchStartY;
      if (Math.abs(dx) < 50) return;          // too short
      if (Math.abs(dy) > Math.abs(dx)) return; // vertical scroll, ignore
      if (dx < 0) nextReportPage();
      else        prevReportPage();
    }, { passive: true });
  })();
```

- [ ] **Step 2: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git add colivingscore/static/index-mobile.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "Mobile: add swipe left/right gesture for report page navigation"
```

---

## Task 9: Deploy to Second Render Service

**Files:** None (user action)

- [ ] **Step 1: Push the `mobile-responsive` branch to GitHub**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore"
git push -u origin mobile-responsive
```

- [ ] **Step 2: Create a second Render Web Service**

In the Render dashboard (render.com):
1. Click **New → Web Service**
2. Connect the same GitHub repo (`ralfeez/colivingscore`)
3. Set **Branch** to `mobile-responsive`
4. Set **Root Directory** to `colivingscore`
5. Set **Build Command** to `pip install -r requirements.txt`
6. Set **Start Command** to `gunicorn app:app`
7. Copy all environment variables from the live service (STRIPE keys, API keys, etc.) — or set `STRIPE_SECRET_KEY` to the test key for now
8. Give it a name like `colivingscore-mobile-preview`
9. Deploy

The preview service gets a URL like `colivingscore-mobile-preview.onrender.com`.

- [ ] **Step 3: Note the preview URL**

Record the preview URL for testing in Task 10.

---

## Task 10: Full Flow Verification

**Files:** None (manual testing)

Use the preview Render service URL from Task 9. Test with `?mobile=1` appended to force mobile view on desktop.

- [ ] **Step 1: Address screen**

Open `https://<preview-url>/?mobile=1`

Expected:
- Address input is full-width
- "Analyze →" button is directly below the input, full-width
- No horizontal overflow

- [ ] **Step 2: 3-step form — Step 1**

Enter an address and click Analyze.

Expected:
- Step indicator shows dot 1 active (white), dots 2 and 3 grey
- 6 fields visible in 2-column grid
- Continue button is full-width green
- "← Back to address" link below

- [ ] **Step 3: 3-step form — Step 2**

Click Continue.

Expected:
- Step indicator shows dot 1 checked (green ✓), dot 2 active, dot 3 grey
- Line between dot 1 and 2 is green
- 6 location/parking fields visible

- [ ] **Step 4: 3-step form — Step 3**

Click Continue.

Expected:
- Dots 1 and 2 green ✓, dot 3 active
- Mortgage, tenant type, rent fields visible
- "Calculate Score →" button at bottom

- [ ] **Step 5: Score result**

Click Calculate Score.

Expected:
- Score ring centered at top
- Tier label below ring
- 2×2 financial grid
- "Get My Pro Analysis →" full-width button (or Pro gate box)
- "← Edit Inputs" and "Score Another →" as text links at bottom

- [ ] **Step 6: Pro report navigation**

Complete payment on the preview Render service (using Stripe test card `4242 4242 4242 4242`) and load the Pro report.

Expected:
- No tab bar visible
- "← Prev | Page 1 of 16 | Next →" bar sticky at top
- "swipe left or right to navigate" hint below bar
- "← Prev" button is disabled on page 1
- Clicking "Next →" advances to Page 2, counter updates to "Page 2 of 16"
- "← Prev" button becomes enabled on page 2

- [ ] **Step 7: Swipe gestures**

On an actual phone (or Chrome DevTools device emulation), load the Pro report.

Expected:
- Swiping left advances to next page
- Swiping right goes to previous page
- Vertical scrolling within a page works normally (does not trigger page change)

- [ ] **Step 8: Desktop regression check**

Open the live site `https://colivingscore.onrender.com` on a desktop browser.

Expected:
- Desktop version loads exactly as before — no changes

- [ ] **Step 9: Email re-access link**

After completing a test payment, check the re-access email. Click the link in the email.

Expected:
- On phone: mobile version of the report loads
- On desktop: desktop version of the report loads
