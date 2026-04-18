import os
import io
import json
import stripe
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from flask import Flask, send_from_directory, request, send_file, jsonify, redirect
from pdf.generate_report import build_pdf_from_data

app = Flask(__name__, static_folder="static")

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
BASE_URL = os.environ.get("BASE_URL", "https://colivingscore.onrender.com")
SHEET_ID = "14JS4z9w5S1Ar0oNhusxegVMz-jdf1e55dbGh1UqBXyc"
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_sheet():
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDS")
    if creds_json:
        creds_info = json.loads(creds_json)
    else:
        local_key = os.path.join(os.path.dirname(__file__), "..", "colivingscore-1e18ab77fce0.json")
        with open(local_key) as f:
            creds_info = json.load(f)
    creds = Credentials.from_service_account_info(creds_info, scopes=SHEETS_SCOPES)
    client = gspread.authorize(creds)
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


# ── Email capture → Google Sheets ────────────────────────────────────────────

@app.route("/save-email", methods=["POST"])
def save_email():
    try:
        data = request.get_json(force=True)
        email = data.get("email", "").strip()
        address = data.get("address", "").strip()
        if not email or "@" not in email:
            return jsonify({"error": "invalid email"}), 400
        sheet = _get_sheet()
        sheet.append_row([datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), email, address])
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
    return jsonify({"publishable_key": STRIPE_PUBLISHABLE_KEY})


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
