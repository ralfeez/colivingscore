import os
import io
import json
import math
import resend
import stripe
import gspread
import requests
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from flask import Flask, send_from_directory, request, send_file, jsonify, redirect
from pdf.generate_report import build_pdf_from_data

app = Flask(__name__, static_folder="static")

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
BASE_URL = os.environ.get("BASE_URL", "https://colivingscore.onrender.com")
SHEET_ID = "14JS4z9w5S1Ar0oNhusxegVMz-jdf1e55dbGh1UqBXyc"
resend.api_key = os.environ.get("RESEND_API_KEY", "")
GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
RENTCAST_API_KEY      = os.environ.get("RENTCAST_API_KEY", "")
ANTHROPIC_API_KEY     = os.environ.get("ANTHROPIC_API_KEY", "")
WALKSCORE_API_KEY     = os.environ.get("WALKSCORE_API_KEY", "")


def _get_sheet():
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDS")
    if creds_json:
        creds_info = json.loads(creds_json.strip())
    else:
        local_key = os.path.join(os.path.dirname(__file__), "..", "colivingscore-1e18ab77fce0.json")
        with open(local_key) as f:
            creds_info = json.load(f)
    client = gspread.service_account_from_dict(creds_info)
    return client.open_by_key(SHEET_ID).sheet1


# ── Static tool ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── PDF generation endpoint ───────────────────────────────────────────────────

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    """
    Accepts JSON body with all Pro Analysis inputs.
    Returns a PDF file download.
    """
    try:
        data = request.get_json(force=True)

        # Write PDF to an in-memory buffer
        buffer = io.BytesIO()
        build_pdf_from_data(data, buffer)
        buffer.seek(0)

        address_slug = (
            data.get("address", "property")
            .replace(" ", "_")
            .replace(",", "")[:40]
        )
        filename = f"CoLivingScore_Report_{address_slug}.pdf"

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Email capture → Google Sheets + Resend ───────────────────────────────────

def _build_score_email(email, data):
    address  = data.get("address", "—")
    beds     = data.get("beds", "—")
    baths    = data.get("baths", "—")
    halfbaths= data.get("halfbaths", 0)
    sqft     = data.get("sqft", "—")
    tenant   = data.get("tenantLabel", "—")
    score    = data.get("score", "—")
    band     = data.get("band", "—")
    gross    = data.get("gross", 0)
    net      = data.get("net", 0)
    dscr     = data.get("dscr", 0)
    flags    = data.get("topFlags", [])

    band_color = {"Excellent":"#1D9E75","Good":"#1D9E75","Fair":"#D97706",
                  "Poor":"#E24B4A","No Go":"#E24B4A"}.get(band, "#555")

    bath_str = f"{baths} full" + (f" / {halfbaths} half" if halfbaths else "")

    flags_html = "".join(
        f'<tr><td style="padding:6px 0;border-bottom:1px solid #eee;font-size:14px;color:#333">'
        f'{f.get("factor","")}</td>'
        f'<td style="padding:6px 0;border-bottom:1px solid #eee;font-size:14px;color:#E24B4A;text-align:right">−{f.get("deduction",0)} pts</td></tr>'
        for f in flags[:3]
    ) if flags else '<tr><td colspan="2" style="color:#666;font-size:14px">No significant deductions</td></tr>'

    net_color = "#1D9E75" if net >= 0 else "#E24B4A"
    dscr_str  = f"{dscr:.2f}" if isinstance(dscr, (int, float)) and dscr else "N/A"
    gross_str = f"${gross:,.0f}" if isinstance(gross, (int, float)) else "—"
    net_str   = f"${net:,.0f}" if isinstance(net, (int, float)) else "—"

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:32px 16px">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;max-width:600px;width:100%">

        <!-- Header -->
        <tr><td style="background:#0f172a;padding:28px 36px">
          <div style="font-size:22px;font-weight:700;color:#fff;letter-spacing:-0.5px">CoLiving<span style="color:#1D9E75">Score</span></div>
          <div style="font-size:13px;color:#94a3b8;margin-top:4px">Your Free Property Score Report</div>
        </td></tr>

        <!-- Score block -->
        <tr><td style="padding:32px 36px 0">
          <div style="text-align:center;background:#f8fafc;border-radius:10px;padding:24px">
            <div style="font-size:64px;font-weight:800;color:{band_color};line-height:1">{score}</div>
            <div style="font-size:18px;font-weight:700;color:{band_color};margin-top:4px">{band.upper()}</div>
            <div style="font-size:13px;color:#64748b;margin-top:8px">{address}</div>
          </div>
        </td></tr>

        <!-- Property summary -->
        <tr><td style="padding:24px 36px 0">
          <div style="font-size:13px;font-weight:700;color:#94a3b8;letter-spacing:0.5px;margin-bottom:12px">PROPERTY DETAILS</div>
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="font-size:14px;color:#333;padding:5px 0;width:50%">Bedrooms</td>
              <td style="font-size:14px;color:#0f172a;font-weight:600;text-align:right">{beds}</td>
            </tr>
            <tr>
              <td style="font-size:14px;color:#333;padding:5px 0">Bathrooms</td>
              <td style="font-size:14px;color:#0f172a;font-weight:600;text-align:right">{bath_str}</td>
            </tr>
            <tr>
              <td style="font-size:14px;color:#333;padding:5px 0">Square Footage</td>
              <td style="font-size:14px;color:#0f172a;font-weight:600;text-align:right">{sqft:,} sq ft</td>
            </tr>
            <tr>
              <td style="font-size:14px;color:#333;padding:5px 0">Target Tenant</td>
              <td style="font-size:14px;color:#0f172a;font-weight:600;text-align:right">{tenant}</td>
            </tr>
          </table>
        </td></tr>

        <!-- Cash flow -->
        <tr><td style="padding:24px 36px 0">
          <div style="font-size:13px;font-weight:700;color:#94a3b8;letter-spacing:0.5px;margin-bottom:12px">CASH FLOW SNAPSHOT</div>
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td style="font-size:14px;color:#333;padding:5px 0">Est. Gross Monthly</td>
              <td style="font-size:14px;color:#0f172a;font-weight:600;text-align:right">{gross_str}</td>
            </tr>
            <tr>
              <td style="font-size:14px;color:#333;padding:5px 0">Est. Monthly Net</td>
              <td style="font-size:14px;font-weight:600;color:{net_color};text-align:right">{net_str}</td>
            </tr>
            <tr>
              <td style="font-size:14px;color:#333;padding:5px 0">DSCR</td>
              <td style="font-size:14px;color:#0f172a;font-weight:600;text-align:right">{dscr_str}</td>
            </tr>
          </table>
        </td></tr>

        <!-- Property audit flags -->
        <tr><td style="padding:24px 36px 0">
          <div style="font-size:13px;font-weight:700;color:#94a3b8;letter-spacing:0.5px;margin-bottom:12px">TOP SCORE FACTORS</div>
          <table width="100%" cellpadding="0" cellspacing="0">
            {flags_html}
          </table>
          <p style="font-size:13px;color:#64748b;margin-top:12px;line-height:1.6">
            These are the highest-impact factors affecting your score. Improving any one of these
            could meaningfully raise your CoLivingScore and the property's income potential.
          </p>
        </td></tr>

        <!-- CTA -->
        <tr><td style="padding:28px 36px">
          <div style="background:#f0fdf4;border-radius:10px;padding:24px;text-align:center">
            <div style="font-size:16px;font-weight:700;color:#0f172a;margin-bottom:8px">Ready for a deeper look?</div>
            <p style="font-size:14px;color:#475569;margin:0 0 20px;line-height:1.6">
              Our <strong>Pro Analysis</strong> unlocks a full P&amp;L, DSCR breakdown, 5-year projection,
              and a downloadable PDF report — all for $29.
            </p>
            <a href="https://colivingscore.onrender.com" style="display:inline-block;background:#1D9E75;color:#fff;font-size:14px;font-weight:600;padding:12px 28px;border-radius:8px;text-decoration:none">
              Run Pro Analysis →
            </a>
          </div>
        </td></tr>

        <!-- Footer -->
        <tr><td style="padding:20px 36px;border-top:1px solid #e2e8f0;text-align:center">
          <p style="font-size:12px;color:#94a3b8;margin:0;line-height:1.6">
            Thank you for using CoLivingScore. Best of luck with your co-living investment!<br>
            <a href="https://colivingscore.onrender.com" style="color:#1D9E75;text-decoration:none">colivingscore.com</a>
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


@app.route("/save-email", methods=["POST"])
def save_email():
    try:
        data = request.get_json(force=True)
        email   = data.get("email", "").strip()
        address = data.get("address", "").strip()
        if not email or "@" not in email:
            return jsonify({"error": "invalid email"}), 400

        # Save to Google Sheets (full data row)
        sheet = _get_sheet()
        sheet.append_row([
            datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            email,
            address,
            data.get("beds", ""),
            data.get("baths", ""),
            data.get("halfbaths", ""),
            data.get("sqft", ""),
            data.get("tenantLabel", ""),
            data.get("rent", ""),
            data.get("mortgage", ""),
            data.get("score", ""),
            data.get("band", ""),
            data.get("gross", ""),
            data.get("net", ""),
            data.get("dscr", ""),
        ])

        # Send score report email via Resend
        resend.Emails.send({
            "from": "CoLivingScore <hello@colivingscore.com>",
            "to": [email],
            "subject": f"Your CoLivingScore Report — {address or 'Property Analysis'}",
            "html": _build_score_email(email, data),
        })

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"save-email error: {e}")
        return jsonify({"error": str(e)}), 500


# ── Health check (Render uses this) ──────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ── Stripe publishable key (safe to expose to frontend) ───────────────────────

@app.route("/config")
def get_config():
    return jsonify({
        "publishable_key": STRIPE_PUBLISHABLE_KEY,
        "google_places_key": GOOGLE_PLACES_API_KEY,
    })


# ── Pro Analysis data routes ──────────────────────────────────────────────────

@app.route("/api/rentcast", methods=["POST"])
def api_rentcast():
    try:
        data    = request.get_json(force=True)
        address = data.get("address", "")
        beds    = data.get("beds", 3)
        baths   = data.get("baths", 2)
        resp = requests.get(
            "https://api.rentcast.io/v1/avm/rent/long-term",
            params={"address": address, "bedrooms": beds, "bathrooms": baths, "propertyType": "Single Family"},
            headers={"X-Api-Key": RENTCAST_API_KEY},
            timeout=10
        )
        if resp.status_code != 200:
            return jsonify({"error": f"RentCast {resp.status_code}"}), 502
        d = resp.json()
        return jsonify({
            "rent_estimate": d.get("rent"),
            "rent_low":      d.get("rentRangeLow"),
            "rent_high":     d.get("rentRangeHigh"),
            "comparables":   d.get("comparables", [])[:5],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/walkscore", methods=["POST"])
def api_walkscore():
    try:
        data    = request.get_json(force=True)
        address = data.get("address", "")
        lat     = data.get("lat")
        lng     = data.get("lng")
        resp = requests.get(
            "https://api.walkscore.com/score",
            params={
                "format": "json",
                "address": address,
                "lat": lat,
                "lon": lng,
                "transit": 1,
                "bike": 1,
                "wsapikey": WALKSCORE_API_KEY,
            },
            timeout=10
        )
        d = resp.json()
        return jsonify({
            "walk_score":    d.get("walkscore"),
            "walk_desc":     d.get("description"),
            "transit_score": d.get("transit", {}).get("score"),
            "transit_desc":  d.get("transit", {}).get("description"),
            "bike_score":    d.get("bike", {}).get("score"),
            "bike_desc":     d.get("bike", {}).get("description"),
            "logo_url":      d.get("logo_url"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _haversine_miles(lat1, lng1, lat2, lng2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


@app.route("/api/nearby", methods=["POST"])
def api_nearby():
    try:
        data = request.get_json(force=True)
        lat  = data.get("lat")
        lng  = data.get("lng")
        if not lat or not lng:
            return jsonify({"error": "lat/lng required"}), 400

        def nearest(place_type, radius=8000):
            resp = requests.get(
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                params={"location": f"{lat},{lng}", "rankby": "distance",
                        "type": place_type, "key": GOOGLE_PLACES_API_KEY},
                timeout=10
            )
            results = resp.json().get("results", [])
            if not results:
                return None
            r   = results[0]
            rlat = r["geometry"]["location"]["lat"]
            rlng = r["geometry"]["location"]["lng"]
            dist = _haversine_miles(lat, lng, rlat, rlng)
            return {"name": r.get("name"), "distance_miles": round(dist, 2),
                    "vicinity": r.get("vicinity")}

        transit  = nearest("transit_station")
        hospital = nearest("hospital")

        def transit_band(d):
            if d is None: return "far"
            if d < 0.5:   return "walkable"
            if d < 1.0:   return "close"
            if d < 2.0:   return "moderate"
            return "far"

        def hospital_band(d):
            if d is None: return "far"
            if d < 1.0:   return "close"
            if d < 3.0:   return "moderate"
            return "far"

        t_dist = transit["distance_miles"]  if transit  else None
        h_dist = hospital["distance_miles"] if hospital else None

        return jsonify({
            "transit":       transit,
            "hospital":      hospital,
            "transit_band":  transit_band(t_dist),
            "hospital_band": hospital_band(h_dist),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/demographics", methods=["POST"])
def api_demographics():
    try:
        data = request.get_json(force=True)
        zip_code = data.get("zip", "")
        if not zip_code:
            return jsonify({"error": "zip required"}), 400

        variables = ",".join([
            "B01003_001E",  # total population
            "B25003_001E",  # total occupied housing units
            "B25003_002E",  # owner occupied
            "B25003_003E",  # renter occupied
            "B19013_001E",  # median household income
            "B25064_001E",  # median gross rent
        ])
        resp = requests.get(
            "https://api.census.gov/data/2023/acs/acs5",
            params={"get": variables, "for": f"zip code tabulation area:{zip_code}"},
            timeout=10
        )
        if resp.status_code != 200:
            return jsonify({"error": "Census data unavailable"}), 502
        rows = resp.json()
        if len(rows) < 2:
            return jsonify({"error": "No data for this zip"}), 404
        headers, values = rows[0], rows[1]
        d = dict(zip(headers, values))

        pop        = int(d.get("B01003_001E", 0) or 0)
        total_hu   = int(d.get("B25003_001E", 1) or 1)
        renter_hu  = int(d.get("B25003_003E", 0) or 0)
        income     = int(d.get("B19013_001E", 0) or 0)
        med_rent   = int(d.get("B25064_001E", 0) or 0)
        renter_pct = round(renter_hu / total_hu * 100, 1) if total_hu else 0

        return jsonify({
            "population":       pop,
            "renter_pct":       renter_pct,
            "median_income":    income,
            "median_rent":      med_rent,
            "zip":              zip_code,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Competitive intelligence — Claude AI + web search ────────────────────────

TENANT_SEARCH_PROMPTS = {
    "nurses": (
        "travel nurse housing, furnished rooms for rent, co-living, nurse housing, short-term rentals"
    ),
    "tech": (
        "co-living, coliving, shared housing, furnished rooms for rent, remote worker housing"
    ),
    "trades": (
        "worker housing, rooms for rent, weekly rentals, shared housing, construction worker housing"
    ),
    "students": (
        "student housing, rooms for rent near university, shared student housing, off-campus housing"
    ),
    "seniors": (
        "senior living, 55+ community, assisted living, independent living, senior housing"
    ),
    "sober": (
        "sober living, recovery housing, sober house, halfway house, transitional housing"
    ),
    "workforce": (
        "rooms for rent, shared housing, co-living, affordable housing, workforce housing"
    ),
}

def _build_competitive_prompt(address, city, state, tenant_key, beds):
    search_terms = TENANT_SEARCH_PROMPTS.get(tenant_key, TENANT_SEARCH_PROMPTS["workforce"])
    is_senior  = tenant_key == "seniors"
    is_sober   = tenant_key == "sober"
    is_nurse   = tenant_key == "nurses"

    extra = ""
    if is_senior:
        extra = (
            "For senior living facilities found, list their name, address, care level "
            "(independent, assisted, memory care), and published monthly rates if available. "
            "If rates are not published, note '(no rates available)'."
        )
    elif is_sober:
        extra = (
            "For sober living or recovery homes found, list their name, address, and monthly "
            "or weekly rates if published. If rates are not found, note '(no rates available)'."
        )
    elif is_nurse:
        extra = (
            "Check Furnished Finder and similar travel nurse housing platforms for listings "
            "near this address. Note average nightly or monthly rates if visible."
        )

    return f"""You are a real estate market analyst specializing in co-living investments.

Research the co-living and rental market near {address} ({city}, {state}) for a {beds}-bedroom property targeting: {tenant_key.replace('_',' ')}.

Search for: {search_terms} near {city}, {state}.

Please provide a structured market analysis with the following sections:

1. MARKET DEMAND
   - Assess rental demand signals in {city}, {state} for this tenant type
   - Note any known employers, universities, hospitals, or demand drivers nearby
   - Describe the general supply/demand balance

2. COMPETITION
   - List named competitors (businesses, properties, or platforms) offering similar housing in {city}, {state}
   - For each: name, approximate location or neighborhood, advertised rates (per room/month), and notable amenities
   - If only a name or address is known with no rates, note "(no rates available)"
   {extra}

3. WHAT COMPETITORS DO WELL
   - Common amenities or features that appear frequently (utilities included, furnished, parking, etc.)

4. MARKET GAPS
   - What is missing or underserved in the current competition?
   - Where is there opportunity to differentiate?

5. PRICING INTELLIGENCE
   - What is the going rate per room per month in this market for this tenant type?
   - Provide a low / mid / high range based on what you find

6. RECOMMENDATION
   - Based on competition and demand, is this a favorable market for a {beds}-bed co-living property targeting {tenant_key}?
   - What positioning would give the best chance of success?

Be specific. Name actual businesses and places where possible. If you cannot find specific data for {city}, use regional or state-level context."""


@app.route("/api/competitive", methods=["POST"])
def api_competitive():
    try:
        data       = request.get_json(force=True)
        address    = data.get("address", "")
        city       = data.get("city", "")
        state      = data.get("state", "")
        tenant_key = data.get("tenant_key", "workforce")
        beds       = data.get("beds", 4)

        prompt = _build_competitive_prompt(address, city, state, tenant_key, beds)

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-opus-4-5-20251001",
            max_tokens=4096,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response (may include tool_use blocks)
        analysis = ""
        for block in response.content:
            if hasattr(block, "text"):
                analysis += block.text

        return jsonify({"analysis": analysis, "tenant_key": tenant_key, "city": city})
    except Exception as e:
        print(f"competitive error: {e}")
        return jsonify({"error": str(e)}), 500


# ── Pro data orchestrator — fast (no competitive) ────────────────────────────

@app.route("/api/pro-data-fast", methods=["POST"])
def api_pro_data_fast():
    """RentCast + WalkScore + Nearby + Demographics only. Returns in ~5-10s."""
    try:
        data       = request.get_json(force=True)
        address    = data.get("address", "")
        lat        = data.get("lat")
        lng        = data.get("lng")
        zip_code   = data.get("zip", "")
        beds       = data.get("beds", 4)
        baths      = data.get("baths", 2)

        def call_rentcast():
            r = requests.post(f"{request.host_url}api/rentcast",
                json={"address": address, "beds": beds, "baths": baths}, timeout=15)
            return "rentcast", r.json() if r.ok else {"error": r.text}

        def call_walkscore():
            r = requests.post(f"{request.host_url}api/walkscore",
                json={"address": address, "lat": lat, "lng": lng}, timeout=15)
            return "walkscore", r.json() if r.ok else {"error": r.text}

        def call_nearby():
            r = requests.post(f"{request.host_url}api/nearby",
                json={"lat": lat, "lng": lng}, timeout=15)
            return "nearby", r.json() if r.ok else {"error": r.text}

        def call_demographics():
            r = requests.post(f"{request.host_url}api/demographics",
                json={"zip": zip_code}, timeout=15)
            return "demographics", r.json() if r.ok else {"error": r.text}

        results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fn): fn.__name__
                       for fn in [call_rentcast, call_walkscore, call_nearby, call_demographics]}
            for future in as_completed(futures):
                try:
                    key, value = future.result()
                    results[key] = value
                except Exception as e:
                    results[futures[future]] = {"error": str(e)}

        return jsonify(results)
    except Exception as e:
        print(f"pro-data-fast error: {e}")
        return jsonify({"error": str(e)}), 500


# ── Pro data orchestrator — full (includes competitive) ───────────────────────

@app.route("/api/pro-data", methods=["POST"])
def api_pro_data():
    """
    Single endpoint that fans out to RentCast, WalkScore, Google Nearby,
    Census ACS, and Claude competitive analysis concurrently.
    Returns all results merged into one JSON object.
    """
    try:
        data       = request.get_json(force=True)
        address    = data.get("address", "")
        lat        = data.get("lat")
        lng        = data.get("lng")
        zip_code   = data.get("zip", "")
        beds       = data.get("beds", 4)
        baths      = data.get("baths", 2)
        city       = data.get("city", "")
        state      = data.get("state", "")
        tenant_key = data.get("tenant_key", "workforce")

        def call_rentcast():
            r = requests.post(f"{request.host_url}api/rentcast",
                json={"address": address, "beds": beds, "baths": baths}, timeout=15)
            return "rentcast", r.json() if r.ok else {"error": r.text}

        def call_walkscore():
            r = requests.post(f"{request.host_url}api/walkscore",
                json={"address": address, "lat": lat, "lng": lng}, timeout=15)
            return "walkscore", r.json() if r.ok else {"error": r.text}

        def call_nearby():
            r = requests.post(f"{request.host_url}api/nearby",
                json={"lat": lat, "lng": lng}, timeout=15)
            return "nearby", r.json() if r.ok else {"error": r.text}

        def call_demographics():
            r = requests.post(f"{request.host_url}api/demographics",
                json={"zip": zip_code}, timeout=15)
            return "demographics", r.json() if r.ok else {"error": r.text}

        def call_competitive():
            r = requests.post(f"{request.host_url}api/competitive",
                json={"address": address, "city": city, "state": state,
                      "tenant_key": tenant_key, "beds": beds}, timeout=60)
            return "competitive", r.json() if r.ok else {"error": r.text}

        results = {}
        tasks = [call_rentcast, call_walkscore, call_nearby,
                 call_demographics, call_competitive]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fn): fn.__name__ for fn in tasks}
            for future in as_completed(futures):
                try:
                    key, value = future.result()
                    results[key] = value
                except Exception as e:
                    results[futures[future]] = {"error": str(e)}

        return jsonify(results)
    except Exception as e:
        print(f"pro-data error: {e}")
        return jsonify({"error": str(e)}), 500


# ── Create Stripe Checkout session ────────────────────────────────────────────

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.get_json(force=True)
        # Store property data in Stripe metadata so we can retrieve it after payment
        # Stripe metadata values must be strings and total <500 chars per key
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": 2900,  # $29.00 in cents
                    "product_data": {
                        "name": "CoLivingScore Pro Analysis",
                        "description": "CoLivingScore Pro Analysis — Full P&L, DSCR, 5-Year Projection & PDF Report",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=BASE_URL + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=BASE_URL + "/?cancelled=true",
        )
        # Store the pro form data in server-side session cache keyed by checkout session ID
        # We use a simple file-based temp store since Render has ephemeral disk
        tmp_path = f"/tmp/cls_{session.id}.json"
        with open(tmp_path, "w") as f:
            json.dump(data, f)

        return jsonify({"url": session.url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Success page — retrieve session and pass data back to frontend ─────────────

@app.route("/success")
def success():
    session_id = request.args.get("session_id")
    if not session_id:
        return redirect("/")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != "paid":
            return redirect("/?payment_failed=true")
        # Load the stored form data
        tmp_path = f"/tmp/cls_{session_id}.json"
        if os.path.exists(tmp_path):
            with open(tmp_path, "r") as f:
                pro_data = json.load(f)
        else:
            pro_data = {}
        # Serve success page — embed the pro data as JSON for the frontend to pick up
        pro_data_json = json.dumps(pro_data).replace("</", "<\\/")
        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<script>
  window._paidProData = {pro_data_json};
  window.location.href = "/?paid=true";
</script>
</head><body>Payment confirmed. Redirecting...</body></html>"""
        return html
    except Exception as e:
        return redirect("/?payment_failed=true")


# ── Stripe webhook — confirms payment server-side ─────────────────────────────

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment confirmed: {session['id']}")

    return jsonify({"status": "ok"}), 200


# ── Local dev entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
