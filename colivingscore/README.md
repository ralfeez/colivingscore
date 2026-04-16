# CoLivingScore.com

Property Score & Analysis tool for co-living investment decisions.

## What it does

- Free tier: Scores any residential property for co-living suitability (0–100)
- Pro Analysis ($29): Full market narrative, itemized expense model, financial ratios, tenant type comparison, improvement ROI, and a lender-ready PDF report

## Stack

- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Backend**: Python + Flask
- **PDF generation**: ReportLab
- **Payments**: Stripe
- **Email capture**: Kit
- **Hosting**: Render

## Local development

```bash
# Clone the repo
git clone https://github.com/ralfeez/colivingscore.git
cd colivingscore

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your keys (never commit this)
cp .env.example .env

# Run locally
python app.py
# Visit http://localhost:5000
```

## Environment variables

Set these in Render dashboard under Environment:

| Variable | Description |
|---|---|
| `STRIPE_SECRET_KEY` | Stripe secret key (sk_live_...) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (pk_live_...) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `KIT_API_KEY` | Kit (formerly ConvertKit) API key |

## Deployment

Push to `main` branch. Render auto-deploys on every commit.

```bash
git add .
git commit -m "your message"
git push origin main
```

## API endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the scoring tool |
| `/generate-pdf` | POST | Accepts JSON inputs, returns PDF |
| `/health` | GET | Health check for Render |

## Pre-launch spec notes

- **Half-bath logic**: Input allows 0.5 increments. Floor value used for ratio scoring. Half-bath triggers improvement suggestion with lower cost estimate ($8k–$12k vs $15k–$22k for full addition).
- **Market narrative**: At launch, AI-generated via Claude API per report. Phase 2 enriches with RentCast and Google Places live data.
- **Free analysis improvements**: NOI orphan row fix, P&L donut sizing — documented for free tier build.
- **DSCR gauge**: Needle pivot and zone label rendering needs rebuild before launch.
- **Live data (Phase 2)**: RentCast for rent comps, Google Places for proximity scoring, Census for demographics.
