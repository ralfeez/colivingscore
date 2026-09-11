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

| Factor         | Nurses | Young Pros | Digital Nomads | Students | Seniors | Sober | Workforce |
|----------------|--------|------------|-----------------|----------|---------|-------|-----------|
| Bathroom ratio | 25     | 18         | 18              | 18       | 25      | 18    | 18        |
| Sqft per bed   | 12     | 12         | 12              | 12       | 12      | 12    | 12        |
| Parking        | 12     | 8          | 8               | 6        | 12      | 6     | 12        |
| Transit        | 10     | 15         | 5               | 25       | 15      | 8     | 8         |
| Hospital       | 20     | 4          | 2               | 4        | 14      | 10    | 6         |
| Laundry        | 10     | 10         | 10              | 10       | 10      | 10    | 10        |
| Tenant churn   | 8      | 4          | 6               | 3        | 0       | 2     | 5         |

Tenant types follow the seven guest types defined in
`CoLiving_Guest_Types_WhitePaper.docx`. "Tech / Remote Workers" was split into
**Young Professionals** and **Digital Nomads / Remote Workers** — the
whitepaper treats these as distinct guest types with different needs (young
professionals: walkable neighborhoods, aesthetics, moderate transit reliance;
digital nomads: internet/workspace quality, low reliance on local transit or
parking, frequent travel). "Construction / Trades" was folded into
**Workforce & Essential Workers**, matching the whitepaper's broader
definition of that segment.

Notes:
- Parking max penalty is reduced for Students, Sober Living, Young
  Professionals, and Digital Nomads — these tenant types are less likely to
  be car-dependent (whitepaper: "many in this segment are car-light").
- Hospital weight is highest for Nurses (commute) and Seniors (medical
  access); lowest for Digital Nomads (not mentioned as a factor at all in
  the whitepaper).
- Transit weight is highest for Students, who most commonly rely on public
  transit. Young Professionals also weight transit relatively high (walkable/
  transit-corridor markets are an explicit green flag in the whitepaper).
  Digital Nomads weight it low — the whitepaper's mobility concern for this
  segment is airport access, not local transit.
- Laundry is a flat penalty regardless of tenant type — all midterm renters
  expect in-home laundry as a baseline amenity.
- Tenant churn penalty reflects the real operational cost of frequent tenant
  turnover: cleaning, re-listing, gap weeks, and management burden. Seniors
  receive no penalty as the most stable tenant type. Nurses receive the
  highest penalty due to standard 3-month travel contracts. Digital Nomads
  are weighted above Young Professionals — the whitepaper describes typical
  nomad stays as 3-6 months versus a young professional's longer tenure.

---

## Factor Scoring Details

### Bathroom Ratio (shared beds ÷ shared full baths — half baths excluded)

A bedroom with its own private (en suite) bathroom doesn't draw on the
bathrooms the rest of the household shares, so en suite bedrooms — and an
equal number of full bathrooms — are removed from the ratio calculation
before scoring:

  shared_beds  = beds − ensuites
  shared_baths = full_baths − ensuites

| Shared ratio (shared_beds ÷ shared_baths) | Penalty % |
|--------------------------------------------|-----------|
| ≤ 1.5                                       | 0%        |
| ≤ 2.0                                       | 33%       |
| ≤ 2.5                                       | 67%       |
| > 2.5                                       | 100%      |

Deduction = max_penalty × penalty_pct

Two edge cases:
- **shared_beds ≤ 0** (every bedroom is en suite): 0% penalty — nobody needs
  to share a bathroom at all.
- **shared_beds > 0 but shared_baths ≤ 0** (en suites consumed every
  bathroom, but shared bedrooms remain): 100% penalty, **plus** a dedicated,
  always-shown red flag — "No shared bathroom available" — independent of
  whether the deduction alone would rank in the top-3 flags shown to the user.

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

| Tenant Type               | Penalty | Rationale                                              |
|---------------------------|---------|--------------------------------------------------------|
| Seniors 55+               | 0       | Most stable, long stays, very low churn                |
| Sober Living              | −2      | Program-structured, medium stay, reliable income       |
| Students                  | −3      | Long academic-year stays, but seasonal vacancy risk    |
| Young Professionals       | −4      | Longer tenures, but in career/life transition          |
| Workforce & Essential Wkrs| −5      | Variable stay length, job-dependent instability        |
| Digital Nomads            | −6      | Typical 3–6 month stays, though some extend or return  |
| Travel Nurses             | −8      | Highest churn — 3-month contracts standard; turnover   |
|                           |         | cost is real and frequent                              |

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

| Tenant Type                 | Default Rent/Room |
|------------------------------|-------------------|
| Travel Nurses                | $1,100            |
| Young Professionals          | $1,150            |
| Digital Nomads / Remote Wkrs | $1,100            |
| Students                     | $800              |
| Seniors 55+                  | $900              |
| Sober Living                 | $850              |
| Workforce & Essential Wkrs   | $875              |

Young Professionals and Digital Nomads defaults come from the whitepaper's
own cited figures: young professionals "$950 to $1,300/month all-inclusive"
(midpoint-ish, rounded), and the whitepaper's own nomad marketing example
("Live in [City] for $1,100/month all-inclusive").

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

### 2026-09-11
- **Changed:** Tenant types now match the seven guest types in
  `CoLiving_Guest_Types_WhitePaper.docx`. "Tech / Remote Workers" split into
  "Young Professionals" and "Digital Nomads / Remote Workers" (distinct
  weights, default rents, and copy per the whitepaper). "Construction /
  Trades" removed and folded into "Workforce" (relabeled "Workforce &
  Essential Workers" to reflect the broader scope).

### 2026-09-10
- **Changed:** Bathroom ratio factor now subtracts en suite bedrooms (and an
  equal number of full bathrooms) from both counts before computing the
  ratio, since a private en-suite bath isn't available to the rest of the
  household. Same penalty tiers as before, applied to the reduced counts.
  Added a new "En Suite Bedrooms" input (property-details step, capped at
  min(beds, baths)) to capture this.
- **Added:** Dedicated always-shown red flag ("No shared bathroom
  available") for the edge case where en suites consume every bathroom but
  shared bedrooms remain — distinct from, and in addition to, the ordinary
  100%-penalty bathroom-ratio deduction.

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
