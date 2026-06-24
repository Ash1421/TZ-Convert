"""
server.py — Flask web server for TZ-Convert.

Endpoints
---------
GET  /                 HTML frontend
GET  /api/convert      Convert a time between two IANA zones
GET  /api/resolve      Resolve a location to IANA timezone
GET  /api/current      Current time in a given timezone
GET  /api/timezones    List or search IANA timezone strings
GET  /api/world        World clock snapshot
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify

from converter import (
    convert_time,
    format_time,
    get_current_time,
    get_utc_offset_str,
    get_world_clocks,
    parse_datetime,
)
from resolver import list_timezones, resolve_location, search_timezones

app = Flask(__name__, static_folder=None)


# ---------------------------------------------------------------------------
# Serve the static site from the repo root (index.html + assets/)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    # When running from src/, go up one level to find index.html
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    from flask import send_from_directory
    return send_from_directory(repo_root, "index.html")


@app.route("/assets/<path:filename>")
def assets(filename: str):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    from flask import send_from_directory
    return send_from_directory(os.path.join(repo_root, "assets"), filename)


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.get("/api/convert")
def api_convert():
    from flask import request
    from_tz  = request.args.get("from", "").strip()
    to_tz    = request.args.get("to", "").strip()
    time_str = request.args.get("time", "").strip()

    if not all([from_tz, to_tz, time_str]):
        return jsonify({"error": "Provide 'from', 'to', and 'time' parameters."}), 400

    # Accept location strings, not just raw IANA
    from_iana, _ = resolve_location(from_tz)
    to_iana,   _ = resolve_location(to_tz)

    try:
        naive     = parse_datetime(time_str, "%Y-%m-%d %H:%M")
        converted = convert_time(naive, from_iana, to_iana)
        return jsonify({
            "from_tz":  from_iana,
            "to_tz":    to_iana,
            "input":    time_str,
            "result":   format_time(converted, "%A, %d %B %Y  %H:%M:%S"),
            "iso":      converted.isoformat(),
            "offset":   get_utc_offset_str(to_iana),
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/resolve")
def api_resolve():
    from flask import request
    location = request.args.get("location", "").strip()
    if not location:
        return jsonify({"error": "Provide a 'location' parameter."}), 400

    iana, method = resolve_location(location)
    now = get_current_time(iana)
    return jsonify({
        "input":        location,
        "iana":         iana,
        "method":       method,
        "current_time": format_time(now, "%H:%M:%S on %a, %d %b %Y"),
        "iso":          now.isoformat(),
        "offset":       get_utc_offset_str(iana),
    })


@app.get("/api/current")
def api_current():
    from flask import request
    tz = request.args.get("tz", "UTC").strip()
    try:
        now = get_current_time(tz)
        return jsonify({
            "tz":     tz,
            "time":   format_time(now, "%H:%M:%S"),
            "date":   format_time(now, "%A, %d %B %Y"),
            "iso":    now.isoformat(),
            "offset": get_utc_offset_str(tz),
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/timezones")
def api_timezones():
    from flask import request
    q      = request.args.get("q", "").strip()
    prefix = request.args.get("prefix", "").strip()
    results = search_timezones(q, limit=30) if q else list_timezones(prefix)
    return jsonify({"count": len(results), "timezones": results})


@app.get("/api/world")
def api_world():
    return jsonify(get_world_clocks())


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run(host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    print("\nTZ-Convert web server")
    print(f"  http://{host}:{port}/")
    print(f"  API: http://{host}:{port}/api/\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run(debug=True)
