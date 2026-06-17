from flask import Blueprint, jsonify, request, send_from_directory, current_app
import os

from .census import get_demographics
from .fips import STATE_FIPS, FIPS_STATE, is_valid_state_fips, is_valid_county_fips, get_counties
from .il_costs import get_il_cost

blueprint = Blueprint("silver_living", __name__)


@blueprint.route("/silver-living")
def dashboard() -> object:
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "silver-living.html"
    )


@blueprint.route("/api/silver-living/counties")
def counties() -> object:
    state_abbr = request.args.get("state", "").upper()
    state_fips = STATE_FIPS.get(state_abbr)
    if not state_fips:
        return jsonify({"error": "Invalid state"}), 400
    county_list = get_counties(state_fips)
    return jsonify({"counties": county_list})


@blueprint.route("/api/silver-living/lookup")
def lookup() -> object:
    state_fips = request.args.get("state", "").strip()
    county_fips = request.args.get("county", "").strip()

    if not is_valid_state_fips(state_fips):
        return jsonify({"error": "Invalid state FIPS"}), 400

    if not is_valid_county_fips(state_fips, county_fips):
        return jsonify({"error": "Invalid county FIPS"}), 400

    try:
        demo = get_demographics(state_fips, county_fips)
    except Exception as e:
        current_app.logger.error(f"Census API error: {e}")
        return jsonify({"error": "Census data unavailable"}), 502

    state_abbr = FIPS_STATE.get(state_fips, "")
    il = get_il_cost(state_abbr) or {"range": "Not available", "source": "", "state": ""}

    return jsonify({**demo, "il_cost": il})
