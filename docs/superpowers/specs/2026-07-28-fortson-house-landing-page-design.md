# Fortson House Landing Page — Design Spec

**Date:** 2026-07-28
**Status:** Approved, ready for implementation plan

## Purpose

A zero-expense marketing landing page for Fortson House, the certifying/chartering organization behind the Silver Living co-living model (independent adults 55+ sharing a home). The page introduces Fortson House and Silver Living, and collects email addresses from two audiences: future residents, and future operators/investors.

## Hosting & Domains

- New GitHub repo: `ralfeez/fortsonhouse` (already created, public, empty). Cloned locally to `colivingscore/fortsonhouse/` (sibling working copy alongside the other project folders in `AI Apps/colivingscore`).
- **GitHub Pages**, serving a plain static site from the `main` branch root. No build step, no framework.
- `fortsonhouse.com` is the canonical domain (`CNAME` file in repo root). DNS: A records at the registrar pointing the apex domain to GitHub Pages' IPs, plus a `www` CNAME.
- `fortsonhouse.org` forwards (registrar-level domain forwarding) to `fortsonhouse.com`. No separate hosting.
- Both domains already owned by the user; GitHub Pages and the repo are free — the whole build has zero recurring cost.

## Email Capture

- One Google Form, created manually by the user (not scriptable), with a required "I'm interested as a…" dropdown: **Future Resident** / **Future Operator or Investor**, plus a name and email field.
- Embedded twice on the page via `<iframe>`, once under each audience's pitch section, using Google Forms' pre-fill URL parameters so the dropdown already matches the section the visitor is reading (visitor can still change it).
- All responses land in one Google Form response Sheet; the dropdown value is the segment column.
- User will create the form and hand over the base form URL + the entry ID for the dropdown field so pre-fill links can be constructed.

## Page Structure (single scroll page, `index.html`)

1. **Header** — logo, sticky anchor nav (What is Silver Living / How Certification Works / Founder / For Residents / For Operators)
2. **Hero** — logo lockup, tagline "Living independently, without living alone," one-line description, two CTA buttons jumping to the two audience sections
3. **What Silver Living Is** — the open, free co-living concept: shared homes, independent adults 55+, split costs, real community. Anyone can open a Silver Living home — it's an unowned category term, not a Fortson House product.
4. **What Fortson House Does** — sets the standard, certifies homes that meet it, audits to keep them accountable. Does not own property, does not provide care.
5. **How Certification Works** — plain-language explanation of the two-domain concept from the Standard (Part 1.4): the Operator runs the business of the home (finances, maintenance, vendor selection, admission screening); Residents self-govern daily life (house norms, common space, quiet hours). Certification means a home is audited against this and other conditions.
6. **Founder Story** — Ralph Pombo's bio, text-only (no photo yet): built this model as someone in the demographic it serves, operates a Silver Living home himself.
7. **For Future Residents** — pitch + pre-filled Google Form embed (dropdown set to Future Resident)
8. **For Future Operators & Investors** — pitch + pre-filled Google Form embed (dropdown set to Future Operator or Investor)
9. **Footer** — logo mark, Facebook (facebook.com/profile.php?id=61591933082838) and YouTube (@FortsonHouse) links, copyright line

## Copy Boundaries (hard constraints, derived from `FortsonHouse/Fortson_House_Status_and_Open_Items.md` and `fortson_house_legal_summary.md`)

These exist because the LLC isn't formed yet, the Standard isn't finalized, and trademark filing is deferred — the page must not create legal exposure ahead of attorney review:

- Never describe Fortson House as a nonprofit. It's planned as a for-profit LLC (not yet formed); the page doesn't state a legal entity type at all.
- Never imply Fortson House or a Silver Living home provides, funds, or coordinates care of any kind, including end-of-life care. Residents are independent, capable adults; homes are not care facilities.
- No trademark symbols (™/®) anywhere — filing is deferred.
- Never use the word "franchise" or describe the certification/payment relationship in a way that reads as a franchise structure.
- No specific legal, financial, or compliance claims (e.g., no Fair Housing Act compliance claims, no insurance guarantees) — those are still open items pending attorney and broker review.
- Tone is descriptive/aspirational ("Fortson House sets the standard and certifies homes that meet it"), never contractual or legally binding language.

## Visual Design

Derived from existing brand assets in `C:\Users\Public\Documents\CoLiving Homes\SilverLiving\FortsonHouse\` (logo file, header banner):

- **Colors:** navy (~`#16264A`, headings/nav), warm tan/brass (~`#9C8153`, accents, "House" wordmark styling), sage green (~`#7C9459`, small accents echoing the oak leaves), cream background (~`#FAF7F0`)
- **Type:** Playfair Display (serif, Google Fonts, free) for headings to match the logo's serif; Inter (sans-serif, Google Fonts, free) for body text
- **Imagery:** `header.png` banner used for the hero section (as-is or cropped); the collage image used further down as supporting/illustrative imagery, captioned generically — never presented as real residents or a real home, since the people/homes in it are AI-generated
- No JS framework; a small vanilla-JS file handles mobile nav toggle and smooth-scroll to anchors only

## Out of Scope

- Founder photo (deferred — text-only bio for now)
- Any legal-entity disclosure, insurance claims, or Standard/Charter details beyond the two-domain concept
- Analytics, cookie banners, or third-party trackers beyond the Google Form embed itself
- A dedicated contact email address (none confirmed to exist yet — social links only in the footer)
