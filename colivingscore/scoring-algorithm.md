# CoLivingScore — Free Score Algorithm Specification

## Model: Penalty-Based (Start at 100)

Every property begins with a perfect score of 100. Points are deducted for
deficiencies in each factor. A property with no deficiencies scores 100.
Scores are clamped to a minimum of 0.

---

## Score Bands

| Range   | Label     | Meaning                                      |
|---------|-----------|----------------------------------------------|
| 85–100  | Excellent | Strong co-living candidate                   |
| 70–84   | Good      | Viable with minor improvements               |
| 50–69   | Fair      | Proceed with caution — review all flags      |
| 30–49   | Poor      | Significant barriers to overcome             |
| 0–29    | No Go     | Not recommended at current inputs            |

---

## Factor Penalty Weights (max points deducted per factor)

| Factor           | Nurses | Tech | Trades | Students | Seniors | Sober | Workforce |
|------------------|--------|------|--------|----------|---------|-------|-----------|
| Bathroom ratio   | 25     | 18   | 18     | 18       | 25      | 18    | 18        |
| Sqft per bed     | 12     | 12   | 12     | 12       | 12      | 12    | 12        |
| Parking          | 12     | 12   | 12     | 6        | 12      | 6     | 12        |
| Transit          | 10     | 8    | 8      | 25       | 15      | 8     | 8         |
| Hospital         | 20     | 4    | 4      | 4        | 14      | 10    | 6         |
| Bed count        | 8      | 8    | 8      | 8        | 8       | 8     | 8         |

Notes:
- Parking max penalty is halved for Students and Sober Living — these tenant
  types are less likely to own vehicles.
- Hospital weight is highest for Nurses (commute) and Seniors (medical access).
- Transit weight is highest for Students, who most commonly rely on public transit.

---

## Factor Scoring Details

### Bathroom Ratio (beds ÷ full baths only — half baths excluded)

| Ratio     | Penalty % |
|-----------|-----------|
| ≤ 1.5     | 0%        |
| ≤ 2.0     | 33%       |
| ≤ 2.5     | 67%       |
| > 2.5     | 100%      |

Deduction = max_penalty × penalty_pct

### Square Footage per Bedroom

| Sqft/bed  | Penalty % |
|-----------|-----------|
| ≥ 350     | 0%        |
| ≥ 250     | 33%       |
| ≥ 180     | 67%       |
| < 180     | 100%      |

### Parking (per-bed quality average)

Each bedroom is assigned the best available parking spot in order:
garage → carport → uncovered → none.

Spot quality values:
- Enclosed garage:         100%
- Carport / covered:        65%
- Uncovered off-street:     40%
- No parking:                0%

Average quality across all bedrooms is computed, then:
  Deduction = max_penalty × (1 − avg_quality)

Example: 5 beds, 1 garage + 4 carport
  Avg quality = (100 + 65 + 65 + 65 + 65) / 5 = 72%
  Deduction   = 12 × (1 − 0.72) = 3 points

### Transit Proximity

| Distance       | Penalty % |
|----------------|-----------|
| Walkable < 0.5 mi | 0%    |
| Close 0.5–1 mi    | 33%   |
| Moderate 1–2 mi   | 67%   |
| Far > 2 mi        | 100%  |

### Hospital Proximity

| Distance    | Penalty % |
|-------------|-----------|
| Close < 1mi | 0%        |
| Moderate    | 50%       |
| Far > 3mi   | 100%      |

### Bed Count

| Beds  | Penalty % | Rationale                      |
|-------|-----------|--------------------------------|
| 4–5   | 0%        | Ideal co-living sweet spot     |
| 6     | 25%       | Manageable but complex         |
| 3     | 50%       | Limited income potential       |
| 7+    | 75%       | High management complexity     |
| 2     | 100%      | Not suited for co-living       |

---

## HOA Modifiers (applied after weighted sum)

| HOA Status           | Effect                                      |
|----------------------|---------------------------------------------|
| No HOA               | No modifier                                 |
| Permits co-living    | −5 points flat                              |
| Rules unclear        | Hard cap at 40 + NO GO flag                 |
| Prohibits rentals    | Hard cap at 20 + NO GO flag (instant gate)  |

---

## Floor Penalties (per floor above 1)

| Tenant Type  | Penalty per extra floor |
|--------------|-------------------------|
| Seniors 55+  | −15 points              |
| Sober Living | −8 points               |
| All others   | −4 points               |

Rationale:
- Seniors: mobility, fall risk, and elevator absence make upper floors a
  serious liability for this demographic.
- Sober Living: structure and safety matter in recovery housing; stairs
  add friction.
- All others: minor inconvenience, noted but not disqualifying.

---

## Mortgage / Cash Flow Factor

The monthly mortgage input is treated as PITI (Principal, Interest, Taxes,
Insurance). Taxes and insurance are therefore NOT separately deducted —
they are already included in the mortgage payment.

Default utility estimates based on property size:
- Under 1,500 sq ft → $400/month
- 1,500–2,000 sq ft → $550/month
- Over 2,000 sq ft  → $700/month

Also assumes: reserves $350/mo, management 10% of effective gross.

Calculation:
  Gross          = beds × rent per room (full potential, no vacancy)
  Effective Gross = Gross × 92% occupancy
  Management     = Effective Gross × 10%
  Operating Exp  = Utilities + Reserves + Management  (no taxes/insurance — in PITI)
  NOI            = Effective Gross − Operating Expenses
  Monthly Net    = NOI − Mortgage (PITI)
  DSCR           = NOI ÷ Mortgage

DSCR-based penalty (max 20 points):
  DSCR ≥ 1.25           → 0 points (meets lender benchmark)
  1.0 ≤ DSCR < 1.25     → 0–10 points (scaled linearly)
  0.75 ≤ DSCR < 1.0     → 10–20 points (scaled linearly)
  DSCR < 0.75           → 20 points (maximum penalty)

No penalty applied if no mortgage is entered.

---

## Improvement Suggestions (Free Score Screen)

Only the top 3 scoring deductions are surfaced as improvement suggestions.
HOA flags are always shown separately as a regulatory notice.
Suggestions are intentionally general — the Pro Analysis phase provides
specific ROI estimates and improvement recommendations.

---

## Pro Analysis Score (Future)

A separate, more accurate score using real market data:
- Rental comps (RentCast API)
- Property value trends (Zillow / Attom)
- Market vacancy rates
- Actual utility costs
- Neighborhood quality indices

Different algorithm entirely — this document covers the Free Score only.

---

## Default Rent Values by Tenant Type

Used when no rent is entered. Users should override with local market rates.

| Tenant Type         | Default Rent/Room |
|---------------------|-------------------|
| Travel Nurses       | $1,100            |
| Tech / Remote       | $1,000            |
| Construction/Trades | $950              |
| Students            | $800              |
| Seniors 55+         | $900              |
| Sober Living        | $850              |
| General Workforce   | $875              |

---

*Last updated: 2026-04-18 — corrected PITI double-count (taxes/insurance removed from opex)*
*Scope: Free Score only. Subject to revision after user testing.*
