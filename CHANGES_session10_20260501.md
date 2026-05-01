# Session 10 Changes — 2026-05-01

## Branch: master
## Commits this session:
- 5692f53 Add favicon to desktop and mobile
- 6507bb2 Add Split level option to Stories field — scores as 2 stories
- dce90f0 (merged from mobile-responsive) Add 30-day expiry note to re-access email
- ad9d54c (merged) Fix duplicate re-access email on every /success visit
- be1e7a9 (merged) Fix four medium pre-launch security and code issues
- b0835d3 (merged) Fix three critical security issues
- f371aca (merged) Add 'Score Another Property' button to scorecard screen
- ...and all prior mobile-responsive commits (Sessions 8–9)

---

## 1. Merge mobile-responsive → master

**What happened:** Full merge of the `mobile-responsive` branch into `master`. Fast-forward merge — no conflicts.

**Files changed:**
- `colivingscore/app.py` — mobile routing, security, Redis email dedup, host-relative URLs
- `colivingscore/static/index-mobile.html` — full mobile frontend (new file, 3155 lines)
- `colivingscore/static/index.html` — form field reorder (tenant type above rent/laundry)

**What the merge brought to master:**
- `_is_mobile()` User-Agent routing — phones get `index-mobile.html`, desktops get `index.html`
- `?mobile=1` / `?mobile=0` URL overrides for testing
- `Cache-Control: no-cache` on `/` route — prevents stale HTML on phones
- `create_checkout_session` now gated with `_check_api_key()` (was missing)
- `success_url` and `cancel_url` use `request.host_url` instead of hard-coded `BASE_URL`
- Redirect to `/?paid=true&_t=Date.now()` — cache-busting timestamp
- Email dedup via Redis (30-day TTL) instead of `/tmp` flag (lost on Render restart)
- Re-access email copy updated: 3–4 min wait, desktop recommendation, 30-day expiry note
- Post-payment scorecard screen (stars, Go/No-Go verdict, HOA flag, tenant fit note)
- "Check Your Email" callout on scorecard
- "← Score Another Property" and "View Report on This Device →" buttons
- All session 9 security fixes (XSS, JSON.parse crash guard, double-tap pay button guard)

**Why:** Mobile Pro Report was OOM-crashing on mobile-preview Render service (512MB free tier). Production server has full RAM — merging to master fixes it.

---

## 2. Add Split level to Stories field

**Files:** `colivingscore/static/index.html`, `colivingscore/static/index-mobile.html`
**Commit:** 6507bb2

**What changed:**
- New `<option value="split">Split level</option>` added between 2 stories and 3 stories in both files
- `floorsNum(f)` helper: converts `"split"` → 2, else `parseInt(f)` — used for all scoring math
- `floorsLabel(f)` helper: maps raw value to display string — `"split"` → `"Split level"`, etc.
- `floors` stored as raw string (not `parseInt`) so `"split"` value is preserved through the pipeline
- Scoring uses `floorsNum()` for penalty calculation — split level scores identically to 2 stories
- Review screen, AI prompt, and Pro Report all receive `floorsLabel()` output — shows "Split level" correctly
- Seniors `singleStory` check updated to use `floorsNum()`

**Why:** Beta tester feedback — split level homes common in Southeast US markets.

---

## 3. Favicon

**Files:** `colivingscore/static/favicon.png` (new), `index.html`, `index-mobile.html`
**Commit:** 5692f53

**What changed:**
- `favicon.png` added to `colivingscore/static/`
- Both HTML files now include:
  ```html
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/favicon.png">
  ```
- `apple-touch-icon` enables logo display when added to iPhone home screen

---

## Pending Before Live Launch

1. **Switch Stripe to live keys** — in Render → Environment Variables:
   - `STRIPE_SECRET_KEY` → replace `sk_test_...` with `sk_live_...`
   - `STRIPE_PUBLISHABLE_KEY` → replace `pk_test_...` with `pk_live_...`
   - `STRIPE_WEBHOOK_SECRET` → update to live webhook secret
2. **Reactivate RentCast subscription** — at app.rentcast.io (was paused)
3. **End-to-end phone test** at colivingscore.onrender.com

## Post-Launch Code Improvements (deferred)
- S5: AI markdown table cell content not HTML-escaped
- S6: /success inlines JSON into script block — use data- attribute instead
- S8: In-memory rate limiter per-worker (not global across gunicorn workers)
- C7: Loading screen setInterval leaked if startLoadingScreen called twice
- C8: No back navigation from restored Pro Report on mobile
- C9: SC_PROFILES duplicates TENANT_PROFILES — will drift
- C10: generateProAnalysis(null) fragile DOM-read fallback
- U1: s-pro-result screen has no back navigation on mobile
- U2: Calculate Score button not guarded against double-tap
- U3: Outer step indicator Address dot calls goToStep(1) instead of showScreen('s-address')
- U4: Send My Score error resets button to wrong text string
- B1: Address interpolated into email subject — potential header injection
- B2: topFlags.factor from POST body embedded in email HTML
- B3: Stripe webhook is no-op — payment side effects only in /success GET
