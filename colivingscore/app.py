import os
import io
import json
from flask import Flask, send_from_directory, request, send_file, jsonify
from pdf.generate_report import build_pdf_from_data

app = Flask(__name__, static_folder="static")


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


# ── Health check (Render uses this) ──────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ── Local dev entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
