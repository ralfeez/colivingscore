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
| Laundry          | 10     | 10   | 10     | 10       | 10      | 10    | 10        |
| Tenant churn     | 8      | 4    | 5      | 3        | 0       | 2     | 5         |

Notes:
- Parking max penalty is halved for Students and Sober Living — these tenant
  types are less likely to own vehicles.
- Hospital weight is highest for Nurses (commute) and Seniors (medical access).
- Transit weight is highest for Students, who most commonly rely on public transit.
- Laundry is a flat penalty regardless of tenant type — all midterm renters
  expect in-home laundry as a baseline amenity.
- Tenant churn penalty reflects the real operational cost of frequent tenant
  turnover: cleaning, re-listing, gap weeks, and management burden. Seniors
  receive no penalty as the most stable tenant type. Nurses receive the highest
  penalty due to standard 3-month travel contracts.

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

**Improvement suggestion:** Adding a bedroom may seem like an easy path to more
income, but tenants in co-living homes place high value on bathroom access. An
extra bedroom without an extra bathroom can make the home harder to rent and may
offset any gain in revenue. Focus on maintaining a strong bed-to-bath ratio first.

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

### Laundry (flat penalty — not tenant-type dependent)

| Status                  | Penalty |
|-------------------------|---------|
| In-home W/D provided    | 0       |
| In-home pay / coin-op   | −3      |
| None                    | −10     |

Rationale: Co-living tenants are midterm renters without personal appliances.
Provided laundry is a baseline expectation. Pay laundry is a minor inconvenience.
No laundry is a genuine detriment that limits the tenant pool and justifies a
meaningful penalty.

**Improvement suggestion:** Installing an in-home washer and dryer can be a
relatively low-cost improvement that recovers up to 10 points and broadens your
tenant pool. If space does not exist, plumbing will not support it, or other
factors are present, this might be an expensive addition.

### Tenant Churn / Turnover (flat penalty by tenant type)

| Tenant Type         | Penalty | Rationale                                              |
|---------------------|---------|--------------------------------------------------------|
| Seniors 55+         | 0       | Most stable, long stays, very low churn                |
| Sober Living        | −2      | Program-structured, medium stay, reliable income       |
| Students            | −3      | Long academic-year stays, but seasonal vacancy risk    |
| Tech / Remote       | −4      | Medium stay, market-driven, moderate churn             |
| General Workforce   | −5      | Variable stay length, job-dependent instability        |
| Construction/Trades | −5      | Project-based work, variable duration                  |
| Travel Nurses       | −8      | Highest churn — 3-month contracts standard; turnover   |
|                     |         | cost is real and frequent                              |

Rationale: Churn affects profitability beyond rent rate. Frequent turnover means
cleaning costs, re-listing time, gap weeks between tenants, and higher management
burden. This penalty is intentionally modest (max 8) since nurses already face
other penalties if the property isn't near medical facilities.

**Improvement suggestion:** Consider a more stable tenant type — switching to
Sober Living or Seniors can recover points and reduce management burden. Use the
tenant type selector to see how the score changes.

### Bed Count

Bed count is NOT a scored factor. There is no penalty for any number of bedrooms.
The score is determined by the bed-to-bath ratio, profitability (DSCR), and all
other factors above.

**Informational flag (no score impact):** Properties with 3 or fewer bedrooms
display a flag: "Properties with 3 or fewer bedrooms have limited income
potential for co-living. In markets with low acquisition costs, the numbers may
still work — let your monthly net income and cash flow be the guide."

Rationale: More bedrooms with proper bathroom ratios is better for co-living
profitability. A 10-bed/10-bath home is an excellent co-living candidate. Penalizing
bed count would penalize success. The DSCR and bathroom ratio factors already
handle properties that are too small to be viable.

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

---

## Mortgage / Cash Flow Factor

The monthly mortgage input is treated as PITI (Principal, Interest, Taxes,
Insurance). Taxes and insurance are therefore NOT separately deducted —
they are already included in the mortgage payment.

Default utility estimates based on property size:
- Under 1,500 sq ft → $400/month
- 1,500–2,000 sq ft → $550/month
- Over 2,000 sq ft  → $700/month

Also assumes: reserves $350/mo, management 15% of effective gross.

Calculation:
  Gross          = beds × rent per room (full potential, no vacancy)
  Effective Gross = Gross × 92% occupancy
  Management     = Effective Gross × 15%
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

## Improvement Suggestions

The free score surfaces the **top 3 scoring deductions** as improvement suggestions.
The Pro Analysis surfaces the **top 4–5**.

Factors that cannot be changed (transit, hospital proximity, floor count) are
framed as tenant-type pivot suggestions rather than property fixes.

HOA flags are always shown separately as a regulatory notice.

---

## Pro Analysis Score

Uses real market data from external APIs:
- Rental comps and market estimate (RentCast API)
- Walkability, transit, and bike scores (WalkScore API)
- Neighborhood demographics — population, renter %, median income, median rent (Census ACS)
- Tenant-type specific amenity proximity (Google Places API)
- Competitive landscape and market intelligence (Claude AI + web search)

The Pro Analysis financial model uses user-provided inputs (actual mortgage,
taxes, insurance, utilities, management rate) rather than the free score defaults.

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

## Management Rate

Default: **15%** of effective gross income.

In the Pro Analysis, this is a user-editable input. Co-living operations
typically run 15–25% due to higher turnover and per-room lease management
complexity. Self-managed operators still incur significant time costs.

The free score uses a fixed 15% assumption.

---

*Scope: Free Score and Pro Analysis financial model.*

---

## Changelog

### 2026-04-20
- **Removed:** Bed count penalty factor (was max 8 pts). Replaced with an
  informational flag for ≤3 beds. Rationale: bed count alone is not a reliable
  indicator of co-living viability. The DSCR and bathroom ratio factors already
  penalize properties that are too small or poorly configured.
- **Added:** Laundry factor (flat penalty, not tenant-type dependent).
  Provided = 0, Pay/coin-op = −3, None = −10. Rationale: midterm renters
  expect in-home laundry as a baseline amenity.
- **Added:** Tenant churn factor (flat penalty by tenant type). Max −8 pts
  (Travel Nurses). Rationale: turnover cost is a real profitability variable
  independent of rent rate.
- **Changed:** Free score management rate from 10% to 15% default.
  Rationale: 10% reflects single-family property management rates; co-living
  is significantly more management-intensive.
- **Changed:** Pro Analysis management rate input default from 10% to 15%.
  Field remains user-editable.
- **Added:** Google Places tenant-type amenity lookup in /api/nearby.
  Returns tenant-specific nearby places alongside existing transit/hospital data.
- **Added:** "Use This In Your Listing" marketing copy block in Pro Analysis
  Location Intelligence section.
- **Added:** Score Improvement Suggestions card in Pro Analysis report (top 4–5).
- **Added:** Be Aware section in Pro Analysis report.
- **Added:** Assumptions notation on property form, financial inputs form,
  and in Pro Analysis report body.
- **Added:** Legal callout banners for Sober Living and Seniors 55+ tenant types.
- **Added:** Room size tooltip on Bedrooms field (70 sq ft min, 7 ft ceiling,
  legal egress, local regulations).
- **Added:** Sqft per tenant hover tooltip on results screen.
- **Added:** Insurance tooltip on Pro Analysis financial form.
