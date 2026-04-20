# CoLivingScore.com

Property scoring and analysis tool for co-living investment decisions.

## What it does

- **Free Score**: Scores any residential property for co-living suitability (0–100) using a penalty-based algorithm across six weighted factors
- **Pro Analysis ($29)**: Full P&L, DSCR breakdown, 5-year projection, tenant type comparison, improvement ROI table, and a downloadable PDF report

## Stack

- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Backend**: Python + Flask
- **PDF generation**: ReportLab
- **Payments**: Stripe Checkout
- **Email**: Resend (score report to user) + Google Sheets (data capture)
- **Hosting**: Render (auto-deploy from `master`)

## Local development

```bash
git clone https://github.com/ralfeez/colivingscore.git
cd colivingscore

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Place your Google service account JSON one level above colivingscore/
# e.g. colivingscore-1e18ab77fce0.json

python app.py
# Visit http://localhost:5000
```

## Environment variables

Set in Render dashboard → Environment:

| Variable | Description |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_live_...`) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (`pk_live_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `GOOGLE_SHEETS_CREDS` | Minified single-line JSON of Google service account credentials |
| `RESEND_API_KEY` | Resend API key for transactional email |
| `BASE_URL` | Production URL (default: `https://colivingscore.onrender.com`) |

## Deployment

Push to `master`. Render auto-deploys on every commit.

```bash
git add .
git commit -m "your message"
git push origin master
```

## API endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the scoring tool |
| `/health` | GET | Health check for Render |
| `/config` | GET | Returns Stripe publishable key |
| `/save-email` | POST | Saves lead to Google Sheets + sends score report email |
| `/generate-pdf` | POST | Accepts Pro Analysis JSON, returns PDF |
| `/create-checkout-session` | POST | Creates Stripe Checkout session |
| `/success` | GET | Post-payment redirect; retrieves session data |
| `/stripe-webhook` | POST | Stripe webhook handler |

## Scoring overview

See [scoring-algorithm.md](scoring-algorithm.md) for the full Free Score specification.

**Short version**: Start at 100, deduct points for deficiencies in six factors (bathroom ratio, sqft/bed, parking, transit, hospital proximity, bed count). Factor weights vary by tenant type. HOA status can cap or disqualify. A DSCR-based cash flow penalty (max 20 pts) applies when a mortgage is entered.

Score bands: 85–100 Excellent · 70–84 Good · 50–69 Fair · 30–49 Poor · 0–29 No Go
