# Fortson House Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy a single-page, zero-cost marketing site for Fortson House at fortsonhouse.com that explains Silver Living and Fortson House's certifying role, and collects emails from two audiences (future residents; future operators/investors) via an embedded Google Form.

**Architecture:** A plain static site (`index.html` + `css/styles.css` + `js/main.js` + `assets/`) in the `ralfeez/fortsonhouse` GitHub repo, served free via GitHub Pages with a custom domain. No build step, no framework, no backend. Brand assets (logo, hero banner, collage photo, favicon) come from `C:\Users\Public\Documents\CoLiving Homes\SilverLiving\FortsonHouse\`, optimized for web before use. Email capture is a single external Google Form (created manually by the user) embedded twice with different pre-fill values.

**Tech Stack:** HTML5, CSS3 (custom properties, flexbox), vanilla JS (no dependencies), Google Fonts (Playfair Display + Inter), Python 3 + Pillow for one-time image asset processing, GitHub Pages, GitHub CLI (`gh`) for repo/Pages configuration.

**Reference spec:** `docs/superpowers/specs/2026-07-28-fortson-house-landing-page-design.md`

**Working directory for the site itself:** `C:\Users\Public\Documents\AI Apps\colivingscore\fortsonhouse\` (already cloned from `https://github.com/ralfeez/fortsonhouse.git`, currently empty). All `git` commands in this plan run inside that directory unless stated otherwise.

---

## File Structure

```
fortsonhouse/
├── index.html              # entire single-page site
├── css/
│   └── styles.css          # all styles
├── js/
│   └── main.js             # mobile nav toggle + nav-close-on-click
├── assets/
│   ├── logo-lockup.png     # full Fortson House logo (nav + footer)
│   ├── hero-banner.jpg     # header.png, converted/optimized
│   ├── collage.jpg         # collage image, converted/optimized
│   ├── favicon.png         # source favicon (copied as-is)
│   ├── favicon-32.png      # generated
│   ├── favicon-16.png      # generated
│   └── apple-touch-icon.png # generated (180x180)
├── check-copy.py           # content-safety check (forbidden terms / required sections)
└── CNAME                   # contains "fortsonhouse.com"
```

## Brand Values Locked In (sampled from the source logo, see spec for full copy boundaries)

- Navy: `#0B1E3D`
- Tan/brass: `#8B7458`
- Sage green: `#5F7142`
- Cream background: `#FAF6EF`
- Cream alt (section stripe): `#F1ECE1`
- Body text: `#26241F`
- Headings: Playfair Display (Google Fonts)
- Body: Inter (Google Fonts)

---

### Task 1: Scaffold the repo and prepare image assets

**Files:**
- Create: `fortsonhouse/assets/logo-lockup.png`
- Create: `fortsonhouse/assets/hero-banner.jpg`
- Create: `fortsonhouse/assets/collage.jpg`
- Create: `fortsonhouse/assets/favicon.png`
- Create: `fortsonhouse/assets/favicon-32.png`
- Create: `fortsonhouse/assets/favicon-16.png`
- Create: `fortsonhouse/assets/apple-touch-icon.png`
- Create: `fortsonhouse/.gitignore`

- [ ] **Step 1: Create the folder structure**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore/fortsonhouse"
mkdir -p assets css js
```

- [ ] **Step 2: Process and copy the brand images**

Run this Python script (uses Pillow, already available on this machine as verified during planning):

```bash
python -c "
from PIL import Image
import os

src = r'C:\Users\Public\Documents\CoLiving Homes\SilverLiving\FortsonHouse'
dst = r'C:\Users\Public\Documents\AI Apps\colivingscore\fortsonhouse\assets'

# Logo lockup: keep as PNG (has fine text, needs to stay crisp), just copy
Image.open(os.path.join(src, 'ChatGPT Image Jul 24, 2026, 03_08_17 PM.png')).convert('RGBA').save(os.path.join(dst, 'logo-lockup.png'), optimize=True)

# Hero banner: convert to JPEG to shrink file size, resize to max 1600px wide
hero = Image.open(os.path.join(src, 'header.png')).convert('RGB')
hero.thumbnail((1600, 1600 * hero.size[1] // hero.size[0]))
hero.save(os.path.join(dst, 'hero-banner.jpg'), quality=82, optimize=True)

# Collage image: same treatment
collage = Image.open(os.path.join(src, 'ChatGPT Image Jul 25, 2026, 07_08_11 AM.png')).convert('RGB')
collage.thumbnail((1600, 1600 * collage.size[1] // collage.size[0]))
collage.save(os.path.join(dst, 'collage.jpg'), quality=82, optimize=True)

# Favicon: copy source, then generate standard sizes
fav = Image.open(os.path.join(src, 'favicon.png')).convert('RGBA')
fav.save(os.path.join(dst, 'favicon.png'))
fav.resize((32, 32), Image.LANCZOS).save(os.path.join(dst, 'favicon-32.png'))
fav.resize((16, 16), Image.LANCZOS).save(os.path.join(dst, 'favicon-16.png'))
fav.resize((180, 180), Image.LANCZOS).save(os.path.join(dst, 'apple-touch-icon.png'))

print('done')
"
```

Expected output: `done`, and 7 files present in `fortsonhouse/assets/`.

- [ ] **Step 3: Verify file sizes are reasonable for a web page**

```bash
ls -la "C:/Users/Public/Documents/AI Apps/colivingscore/fortsonhouse/assets"
```

Expected: `hero-banner.jpg` and `collage.jpg` each well under 400KB (down from ~1.8-2.5MB as PNGs). If either is still over ~500KB, lower `quality=82` to `quality=72` and re-run Step 2 for that file.

- [ ] **Step 4: Add a minimal .gitignore**

```
.DS_Store
Thumbs.db
```

Write this to `fortsonhouse/.gitignore`.

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore/fortsonhouse"
git add assets .gitignore
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "chore: add optimized brand assets"
```

---

### Task 2: HTML shell, global CSS, and fonts

**Files:**
- Create: `fortsonhouse/index.html`
- Create: `fortsonhouse/css/styles.css`

- [ ] **Step 1: Write `index.html`** with the full document shell, head metadata, and empty section containers (content filled in later tasks):

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fortson House — Certifying the Silver Living Co-Living Model</title>
<meta name="description" content="Fortson House certifies and audits Silver Living homes — shared housing where independent adults 55+ split costs and build real community. Join our list as a future resident or operator/investor.">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/styles.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="#top" class="brand">
      <img src="assets/logo-lockup.png" alt="Fortson House" class="brand-logo">
    </a>
    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="site-nav">
      <span></span><span></span><span></span>
    </button>
    <nav class="site-nav" id="site-nav">
      <a href="#what-is-silver-living">What is Silver Living</a>
      <a href="#how-certification-works">How Certification Works</a>
      <a href="#founder">Founder</a>
      <a href="#residents">For Residents</a>
      <a href="#operators">For Operators</a>
    </nav>
  </div>
</header>

<main>
<!-- HERO -->
<!-- WHAT-IS-SILVER-LIVING -->
<!-- WHAT-FORTSON-HOUSE-DOES -->
<!-- HOW-CERTIFICATION-WORKS -->
<!-- FOUNDER -->
<!-- COLLAGE -->
<!-- RESIDENTS -->
<!-- OPERATORS -->
</main>

<!-- FOOTER -->

<script src="js/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write `css/styles.css`** with resets, variables, and header/nav styles:

```css
:root {
  --navy: #0B1E3D;
  --tan: #8B7458;
  --sage: #5F7142;
  --cream: #FAF6EF;
  --cream-alt: #F1ECE1;
  --white: #FFFFFF;
  --text: #26241F;
  --font-heading: 'Playfair Display', serif;
  --font-body: 'Inter', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: var(--font-body); color: var(--text); background: var(--cream); line-height: 1.6; }
img { max-width: 100%; display: block; }
a { color: inherit; }

.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--cream);
  box-shadow: 0 1px 0 rgba(0,0,0,0.06);
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1.5rem;
}
.brand-logo { height: 56px; }
.site-nav { display: flex; gap: 1.5rem; }
.site-nav a { font-weight: 500; font-size: 0.95rem; text-decoration: none; color: var(--navy); }
.site-nav a:hover { color: var(--tan); }
.nav-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
}
.nav-toggle span { width: 24px; height: 2px; background: var(--navy); display: block; }

@media (max-width: 800px) {
  .site-nav {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--cream);
    flex-direction: column;
    padding: 1rem 1.5rem;
    display: none;
    gap: 1rem;
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
  }
  .site-nav.open { display: flex; }
  .nav-toggle { display: flex; }
}
```

- [ ] **Step 3: Verify the shell renders**

Open `fortsonhouse/index.html` directly in a browser (double-click, or `start index.html` on Windows). Expected: cream background, sticky header with logo on the left, nav links on the right (desktop width), no console errors about missing files other than the Google Fonts request succeeding.

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore/fortsonhouse"
git add index.html css/styles.css
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add HTML shell, header/nav, and global styles"
```

---

### Task 3: Hero section

**Files:**
- Modify: `fortsonhouse/index.html` (replace `<!-- HERO -->`)
- Modify: `fortsonhouse/css/styles.css` (append)

- [ ] **Step 1: Replace `<!-- HERO -->` in `index.html`** with:

```html
<section class="hero" id="top" style="background-image:url('assets/hero-banner.jpg')">
  <div class="hero-overlay">
    <div class="hero-content">
      <h1>Living Independently, Without Living Alone.</h1>
      <p class="hero-sub">Fortson House sets the standard for Silver Living — the open co-living model built for independent adults 55 and older who want real community, not more square footage to maintain alone.</p>
      <div class="hero-ctas">
        <a href="#residents" class="btn btn-primary">I'm Looking for a Home</a>
        <a href="#operators" class="btn btn-secondary">I Certify or Invest in Homes</a>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Append hero styles to `css/styles.css`**

```css
.hero {
  position: relative;
  background-size: cover;
  background-position: center;
  min-height: 70vh;
  display: flex;
  align-items: center;
}
.hero-overlay {
  width: 100%;
  background: linear-gradient(180deg, rgba(11,30,61,0.15), rgba(11,30,61,0.7));
  padding: 4rem 1.5rem;
}
.hero-content { max-width: 700px; margin: 0 auto; text-align: center; color: var(--white); }
.hero-content h1 { font-family: var(--font-heading); font-size: 2.75rem; margin-bottom: 1rem; }
.hero-sub { font-size: 1.15rem; margin-bottom: 2rem; }
.hero-ctas { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.btn {
  display: inline-block;
  padding: 0.85rem 1.75rem;
  border-radius: 4px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}
.btn-primary { background: var(--tan); color: var(--navy); }
.btn-primary:hover { background: #a08765; }
.btn-secondary { background: transparent; border: 2px solid var(--white); color: var(--white); }
.btn-secondary:hover { background: rgba(255,255,255,0.15); }

@media (max-width: 800px) {
  .hero-content h1 { font-size: 2rem; }
}
```

- [ ] **Step 3: Verify in browser**

Reload `index.html`. Expected: full-bleed hero photo with a dark gradient overlay, centered white headline/subhead, two buttons ("I'm Looking for a Home" filled tan, "I Certify or Invest in Homes" outlined white). Clicking either button jumps down the page (targets don't exist yet, so it'll jump to bottom of `<main>` — that's expected until later tasks add the target sections).

- [ ] **Step 4: Commit**

```bash
git add index.html css/styles.css
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add hero section"
```

---

### Task 4: "What Silver Living Is" and "What Fortson House Does" sections

**Files:**
- Modify: `fortsonhouse/index.html` (replace `<!-- WHAT-IS-SILVER-LIVING -->` and `<!-- WHAT-FORTSON-HOUSE-DOES -->`)
- Modify: `fortsonhouse/css/styles.css` (append)

- [ ] **Step 1: Replace `<!-- WHAT-IS-SILVER-LIVING -->`** with:

```html
<section class="content-section" id="what-is-silver-living">
  <div class="section-inner">
    <h2>What Silver Living Is</h2>
    <p>Silver Living is a free, open concept: a shared home where independent adults 55 and older each have their own room, split the cost of the house, and build a real household together instead of living out their years alone. Anyone can open a Silver Living home — it isn't owned by any single company, and it never will be. It's a category, the same way "sober living" describes a type of home rather than one company's product.</p>
    <p>What makes a house a Silver Living home isn't the address. It's whether the people living there run it the way the model intends: residents in charge of their own daily life, real cost-sharing, and a genuine say in who joins the household next.</p>
  </div>
</section>
```

- [ ] **Step 2: Replace `<!-- WHAT-FORTSON-HOUSE-DOES -->`** with:

```html
<section class="content-section alt-bg" id="what-fortson-house-does">
  <div class="section-inner">
    <h2>What Fortson House Does</h2>
    <p>Fortson House is the certifying and chartering organization behind Silver Living. We don't own a single property, and we never provide care of any kind. What we do is set the standard a home has to meet, certify the homes that meet it, and audit them on an ongoing basis to keep them accountable.</p>
    <p>That's what makes certification worth something. Anyone can call a house "Silver Living." A Fortson House charter means a real, outside organization checked the home against a written standard — and keeps checking.</p>
    <p>Certification tells residents, families, and investors exactly what a certified home means before they ever walk in the door.</p>
  </div>
</section>
```

- [ ] **Step 3: Append shared content-section styles to `css/styles.css`**

```css
.content-section { padding: 5rem 1.5rem; }
.content-section.alt-bg { background: var(--cream-alt); }
.section-inner { max-width: 760px; margin: 0 auto; }
.content-section h2 {
  font-family: var(--font-heading);
  color: var(--navy);
  font-size: 2rem;
  margin-bottom: 1.5rem;
}
.content-section p { margin-bottom: 1.25rem; font-size: 1.05rem; }
.content-section p:last-child { margin-bottom: 0; }
```

- [ ] **Step 4: Verify in browser**

Reload. Expected: two stacked text sections, the second on a slightly darker cream stripe (`--cream-alt`) to visually separate it, headings in navy serif type.

- [ ] **Step 5: Content-safety spot check**

```bash
grep -iE "nonprofit|non-profit|franchise|™|®" "C:/Users/Public/Documents/AI Apps/colivingscore/fortsonhouse/index.html"
```

Expected: no output (no matches). This check gets automated fully in Task 9, but running it now catches problems early while the section is fresh.

- [ ] **Step 6: Commit**

```bash
git add index.html css/styles.css
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add What Silver Living Is and What Fortson House Does sections"
```

---

### Task 5: "How Certification Works" and "Founder Story" sections

**Files:**
- Modify: `fortsonhouse/index.html` (replace `<!-- HOW-CERTIFICATION-WORKS -->` and `<!-- FOUNDER -->`)

- [ ] **Step 1: Replace `<!-- HOW-CERTIFICATION-WORKS -->`** with:

```html
<section class="content-section" id="how-certification-works">
  <div class="section-inner">
    <h2>How Certification Works</h2>
    <p>Every certified home splits its decisions into two clear domains. The Operator runs the business of the home — the finances, maintenance, vendor relationships, and who gets considered for an open room. The Residents run their own daily life — house norms, shared meals, quiet hours, and the rhythm of the household.</p>
    <p>Neither side reaches into the other's decisions. Residents are independent, capable adults; what they need is a real voice in their day-to-day life, not the burden of running a house like a business. That split, and the outside audit that keeps it honest, is the core of what a Fortson House charter certifies.</p>
  </div>
</section>
```

- [ ] **Step 2: Replace `<!-- FOUNDER -->`** with:

```html
<section class="content-section alt-bg" id="founder">
  <div class="section-inner">
    <h2>Founded by Someone Who Lives It</h2>
    <p>Fortson House was founded by Ralph Pombo, who built the Silver Living model as someone in the very demographic it serves — and who operates a Silver Living home himself. This isn't a concept designed from the outside. It's a standard built by someone living inside the model he's asking other homes to meet.</p>
  </div>
</section>
```

- [ ] **Step 3: Verify in browser**

Reload. Expected: two more stacked sections continuing the alternating cream/cream-alt background pattern (this section should land on `alt-bg` again — check visually that it doesn't accidentally match the section immediately above it; if Task 4's second section was already `alt-bg`, this Founder section being `alt-bg` too means two darker stripes in a row, which is fine here since "How Certification Works" in between is plain `cream`).

- [ ] **Step 4: Commit**

```bash
git add index.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add How Certification Works and Founder sections"
```

---

### Task 6: Collage image section

**Files:**
- Modify: `fortsonhouse/index.html` (replace `<!-- COLLAGE -->`)
- Modify: `fortsonhouse/css/styles.css` (append)

- [ ] **Step 1: Replace `<!-- COLLAGE -->`** with:

```html
<section class="collage-section">
  <img src="assets/collage.jpg" alt="Illustrative scenes of daily life in a Silver Living home — shared meals, games, and conversation" class="collage-img">
</section>
```

Note: the alt text is deliberately generic/illustrative — the people and home in this image are AI-generated, not real residents or a real certified home, per the design spec's copy boundaries.

- [ ] **Step 2: Append styles**

```css
.collage-section { padding: 0; }
.collage-img { width: 100%; }
```

- [ ] **Step 3: Verify in browser**

Reload. Expected: full-width photo collage banner between the Founder section and the Residents CTA (added next task), no padding/gap around it.

- [ ] **Step 4: Commit**

```bash
git add index.html css/styles.css
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add collage image section"
```

---

### Task 7: "For Future Residents" and "For Future Operators & Investors" CTA sections

The Google Form doesn't exist yet (the user creates it separately). This task builds both sections with a real, complete, deployable fallback state — not a broken placeholder — so the page is fully functional before the form exists. Task 11 replaces the fallback with the real embed once the form is created.

**Files:**
- Modify: `fortsonhouse/index.html` (replace `<!-- RESIDENTS -->` and `<!-- OPERATORS -->`)
- Modify: `fortsonhouse/css/styles.css` (append)

- [ ] **Step 1: Replace `<!-- RESIDENTS -->`** with:

```html
<section class="cta-section" id="residents">
  <div class="section-inner">
    <h2>For Future Residents</h2>
    <p>If the idea of a shared, independent household sounds better than either living alone or giving up your independence, tell us where you'd like to live and we'll keep you posted as certified Silver Living homes open near you.</p>
    <div class="form-embed" id="resident-form-embed">
      <p class="form-pending">Sign-up form launching shortly. Check back soon, or follow us on <a href="https://www.facebook.com/profile.php?id=61591933082838" target="_blank" rel="noopener">Facebook</a> for updates.</p>
    </div>
  </div>
</section>
```

- [ ] **Step 2: Replace `<!-- OPERATORS -->`** with:

```html
<section class="cta-section alt-bg" id="operators">
  <div class="section-inner">
    <h2>For Future Operators &amp; Investors</h2>
    <p>Anyone with a home and a real commitment to community can open a Silver Living house. Fortson House certifies homes that meet the standard and keeps them accountable to it — without ever taking an ownership stake in your property. If you're considering opening a home, or looking to support the people who do, we'd like to hear from you.</p>
    <div class="form-embed" id="operator-form-embed">
      <p class="form-pending">Sign-up form launching shortly. Check back soon, or follow us on <a href="https://www.facebook.com/profile.php?id=61591933082838" target="_blank" rel="noopener">Facebook</a> for updates.</p>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Append CTA section styles**

```css
.cta-section { padding: 5rem 1.5rem; }
.cta-section.alt-bg { background: var(--cream-alt); }
.cta-section .section-inner { max-width: 640px; }
.cta-section h2 {
  font-family: var(--font-heading);
  color: var(--navy);
  font-size: 2rem;
  margin-bottom: 1rem;
  text-align: center;
}
.cta-section p { text-align: center; margin-bottom: 2rem; font-size: 1.05rem; }
.form-embed {
  background: var(--white);
  border-radius: 8px;
  padding: 2rem 1.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.form-pending { text-align: center; font-style: italic; color: var(--navy); margin: 0; }
.form-embed iframe { border: none; width: 100%; }
```

- [ ] **Step 4: Verify in browser**

Reload, click the two hero buttons. Expected: each jumps to its matching section; both show a white card with an italic "launching shortly" message and a working Facebook link.

- [ ] **Step 5: Commit**

```bash
git add index.html css/styles.css
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add resident and operator/investor CTA sections with sign-up placeholder"
```

---

### Task 8: Footer

**Files:**
- Modify: `fortsonhouse/index.html` (replace `<!-- FOOTER -->`)
- Modify: `fortsonhouse/css/styles.css` (append)

- [ ] **Step 1: Replace `<!-- FOOTER -->`** with:

```html
<footer class="site-footer">
  <div class="footer-inner">
    <img src="assets/logo-lockup.png" alt="Fortson House" class="footer-logo">
    <div class="footer-social">
      <a href="https://www.facebook.com/profile.php?id=61591933082838" target="_blank" rel="noopener">Facebook</a>
      <a href="https://www.youtube.com/@FortsonHouse" target="_blank" rel="noopener">YouTube</a>
    </div>
    <p class="footer-copy">&copy; 2026 Fortson House. Silver Living is an open model; Fortson House certifies homes that meet its standard.</p>
  </div>
</footer>
```

- [ ] **Step 2: Append footer styles**

```css
.site-footer { background: var(--navy); color: var(--cream); padding: 3rem 1.5rem; }
.footer-inner { max-width: 1100px; margin: 0 auto; text-align: center; }
.footer-logo { height: 70px; margin: 0 auto 1.5rem; filter: brightness(0) invert(1); }
.footer-social { display: flex; gap: 1.5rem; justify-content: center; margin-bottom: 1.5rem; }
.footer-social a {
  text-decoration: none;
  font-weight: 500;
  color: var(--cream);
  border-bottom: 1px solid var(--tan);
  padding-bottom: 2px;
}
.footer-copy { font-size: 0.85rem; opacity: 0.8; max-width: 600px; margin: 0 auto; }
```

- [ ] **Step 3: Verify in browser**

Reload and scroll to the bottom. Expected: navy footer band, white-silhouette logo (via the `brightness(0) invert(1)` filter — since the logo is multicolor, this intentionally renders it as a flat white mark, not maintaining its original colors), Facebook/YouTube links, and the copyright line.

- [ ] **Step 4: Commit**

```bash
git add index.html css/styles.css
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add footer with social links"
```

---

### Task 9: Mobile nav toggle JavaScript

**Files:**
- Create: `fortsonhouse/js/main.js`

- [ ] **Step 1: Write `js/main.js`**

```javascript
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');

  toggle.addEventListener('click', function () {
    var isOpen = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  nav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
});
```

- [ ] **Step 2: Verify in browser at mobile width**

Resize the browser window to under 800px wide (or use dev tools device emulation). Expected: nav links disappear, a 3-line hamburger icon appears next to the logo. Clicking it reveals the nav links in a dropdown; clicking any nav link closes the dropdown and scrolls to that section.

- [ ] **Step 3: Commit**

```bash
git add js/main.js
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: add mobile nav toggle"
```

---

### Task 10: Automated content-safety check and full-page browser verification

**Files:**
- Create: `fortsonhouse/check-copy.py`

- [ ] **Step 1: Write `check-copy.py`**

```python
"""Guards against copy that oversteps Fortson House's current legal position.
Run any time index.html changes. See docs/superpowers/specs/2026-07-28-fortson-house-landing-page-design.md
for why these terms are excluded.
"""
import re
import sys

FORBIDDEN = [
    r"non[\s-]?profit",
    r"franchise",
    r"™",
    r"®",
]

REQUIRED_IDS = [
    "what-is-silver-living",
    "what-fortson-house-does",
    "how-certification-works",
    "founder",
    "residents",
    "operators",
]

def main():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    failures = []

    for pattern in FORBIDDEN:
        if re.search(pattern, html, re.IGNORECASE):
            failures.append(f"Forbidden term found matching /{pattern}/")

    for section_id in REQUIRED_IDS:
        if f'id="{section_id}"' not in html:
            failures.append(f"Missing required section id: {section_id}")

    if failures:
        print("FAIL:")
        for f_ in failures:
            print(" -", f_)
        sys.exit(1)

    print("PASS: no forbidden terms, all required sections present")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore/fortsonhouse"
python check-copy.py
```

Expected: `PASS: no forbidden terms, all required sections present`. If it fails, fix the flagged copy in `index.html` before continuing.

- [ ] **Step 3: Full visual verification in a real browser**

Add a launch config so the site can be previewed properly (matters for the `hero-banner.jpg` background-image and iframe placeholder rendering, which can behave slightly differently under `file://` vs an actual HTTP server). Create `.claude/launch.json` at the repo root (`C:/Users/Public/Documents/AI Apps/colivingscore/.claude/launch.json` — check if it already exists first and add to it rather than overwrite):

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "fortsonhouse",
      "runtimeExecutable": "python",
      "runtimeArgs": ["-m", "http.server", "8090", "--directory", "fortsonhouse"],
      "port": 8090
    }
  ]
}
```

Then start it and check the page: use the preview tool to start the `fortsonhouse` server, navigate to it, and check:
- Desktop width (1280px): header, hero, all six content/CTA sections, footer render with no layout breaks
- Mobile width (375px): hamburger nav works, hero text doesn't overflow, CTA cards stack cleanly
- All nav links and hero buttons scroll to the correct section
- No 404s in the network panel for any asset (logo, hero banner, collage, favicon, fonts)

- [ ] **Step 4: Fix any issues found**, re-run Steps 2-3 until clean.

- [ ] **Step 5: Commit**

```bash
git add check-copy.py
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "test: add automated copy-safety check"
```

(If `.claude/launch.json` in the parent `colivingscore` repo was modified, that's a separate repo/commit — mention it to the user rather than committing it silently, since `colivingscore` has its own commit discipline.)

---

### Task 11: Deploy to GitHub Pages with the custom domain

**Files:**
- Create: `fortsonhouse/CNAME`

- [ ] **Step 1: Add the CNAME file**

Write the single line `fortsonhouse.com` (no protocol, no trailing slash) to `fortsonhouse/CNAME`.

- [ ] **Step 2: Commit and push**

```bash
cd "C:/Users/Public/Documents/AI Apps/colivingscore/fortsonhouse"
git add CNAME
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "chore: configure custom domain"
git push -u origin main
```

- [ ] **Step 3: Enable GitHub Pages via the GitHub CLI**

```bash
gh api repos/ralfeez/fortsonhouse/pages -X POST -f "source[branch]=main" -f "source[path]=/"
```

Expected: JSON response describing the new Pages site (or a 409 if Pages is somehow already enabled — in that case skip to Step 4).

- [ ] **Step 4: Set the custom domain on the Pages site**

```bash
gh api repos/ralfeez/fortsonhouse/pages -X PUT -f "cname=fortsonhouse.com"
```

Expected: 204 No Content on success.

- [ ] **Step 5: Confirm Pages status**

```bash
gh api repos/ralfeez/fortsonhouse/pages
```

Expected: JSON showing `"cname": "fortsonhouse.com"` and `"status": "building"` (or `"built"` after a minute). HTTPS enforcement (`https_enforced`) may not be settable yet if the TLS certificate hasn't been issued — that depends on the Namecheap DNS records having propagated. If so, tell the user to check back and enable "Enforce HTTPS" in the repo's Settings → Pages once GitHub shows the certificate as ready.

- [ ] **Step 6: Verify the live site**

Once DNS has propagated (may not be immediate), navigate to `https://fortsonhouse.com` and confirm it loads the deployed page, not a GitHub 404 or the Namecheap parking page.

---

### Task 12 (follow-up, blocked on the user creating the Google Form): Wire up the real Google Form embeds

This task cannot be completed until the user has created the Google Form described in the design spec (name field, email field, a required "I'm interested as a…" dropdown with options "Future Resident" and "Future Operator or Investor") and shared its link.

**Files:**
- Modify: `fortsonhouse/index.html` (replace both `.form-pending` blocks)

- [ ] **Step 1: Get the pre-fill base URL and entry IDs**

In the created Google Form, click the ⋮ menu → "Get pre-filled link." Fill in the dropdown with "Future Resident," fill dummy values in the other fields, click "Get link," and copy it. Repeat with "Future Operator or Investor" selected. Each copied link looks like:

```
https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform?usp=pp_url&entry.123456789=Future+Resident&entry.987654321=Jane&entry.111222333=jane%40example.com
```

The `entry.123456789=Future+Resident` part is what matters — that's the dropdown's entry ID.

- [ ] **Step 2: Replace the resident placeholder** in `index.html` — swap:

```html
<p class="form-pending">Sign-up form launching shortly. Check back soon, or follow us on <a href="https://www.facebook.com/profile.php?id=61591933082838" target="_blank" rel="noopener">Facebook</a> for updates.</p>
```

for:

```html
<iframe src="https://docs.google.com/forms/d/e/{FORM_ID}/viewform?embedded=true&entry.{DROPDOWN_ENTRY_ID}=Future+Resident" width="100%" height="900" title="Fortson House resident sign-up form">Loading…</iframe>
```

substituting the real `{FORM_ID}` and `{DROPDOWN_ENTRY_ID}` values found in Step 1.

- [ ] **Step 3: Replace the operator/investor placeholder** the same way, using `entry.{DROPDOWN_ENTRY_ID}=Future+Operator+or+Investor` (URL-encoded space as `+`).

- [ ] **Step 4: Verify in browser**

Reload both CTA sections, confirm each embedded form loads with the dropdown pre-set correctly, and submit one real test entry per form to confirm responses land in the Form's linked Google Sheet.

- [ ] **Step 5: Commit and push**

```bash
git add index.html
PRE_COMMIT_ALLOW_NO_CONFIG=1 git commit -m "feat: wire up live Google Form embeds"
git push
```

GitHub Pages auto-deploys from `main`, so the live site updates within a minute or two of the push.

---

## Post-Launch Checklist (not part of this plan's tasks, for the user)

- Confirm Namecheap DNS changes (A records + www CNAME) were saved, per the earlier conversation
- Set up `fortsonhouse.org` to forward to `fortsonhouse.com` in Namecheap's domain forwarding settings
- Create the Google Form and hand off its link so Task 12 can run
