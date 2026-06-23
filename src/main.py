"""
main.py — Entry point for TZ-Convert.

Usage
-----
python src/main.py                          # GUI (default)
python src/main.py --gui
python src/main.py --server                 # http://127.0.0.1:5000
python src/main.py --server --host 0.0.0.0 --port 8080
python src/main.py --cli Denver             # Resolve a location
python src/main.py --cli "2026-06-22 14:30" UTC "Australia/Sydney"  # Convert
"""

from __future__ import annotations

import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def _run_gui():
    try:
        from gui import run as gui_run
        gui_run()
    except ImportError as exc:
        print(f"[error] Cannot start GUI: {exc}")
        print("Install:  pip install customtkinter")
        sys.exit(1)


def _run_server(host: str, port: int, debug: bool):
    try:
        from server import run as server_run
        server_run(host=host, port=port, debug=debug)
    except ImportError as exc:
        print(f"[error] Cannot start server: {exc}")
        print("Install:  pip install flask")
        sys.exit(1)


def _run_cli(args: list[str]):
    from converter import (
        convert_time,
        format_time,
        get_current_time,
        get_utc_offset_str,
        parse_datetime,
    )
    from resolver import resolve_location

    if not args:
        print(__doc__)
        sys.exit(0)

    if len(args) == 1:
        # Resolve mode
        loc = args[0]
        iana, method = resolve_location(loc)
        now    = get_current_time(iana)
        offset = get_utc_offset_str(iana)
        print(f"\n  Input   : {loc!r}")
        print(f"  IANA    : {iana}")
        print(f"  Method  : {method}")
        print(f"  Now     : {format_time(now, '%H:%M:%S  %a, %d %b %Y')}")
        print(f"  Offset  : {offset}\n")

    elif len(args) == 3:
        # Convert mode
        time_str, from_raw, to_raw = args
        from_tz, _ = resolve_location(from_raw)
        to_tz,   _ = resolve_location(to_raw)
        try:
            naive = parse_datetime(time_str)
            conv  = convert_time(naive, from_tz, to_tz)
            offset = get_utc_offset_str(to_tz)
            print(f"\n  Input   : {time_str}  [{from_tz}]")
            print(f"  Output  : {format_time(conv, '%H:%M:%S  %a, %d %b %Y')}  [{to_tz}]")
            print(f"  Offset  : {offset}\n")
        except ValueError as exc:
            print(f"[error] {exc}")
            sys.exit(1)
    else:
        print("[error] Unexpected number of arguments. Pass 1 (location) or 3 (datetime from to).")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="tz-convert",
        description="IANA timezone resolver and converter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--gui",    action="store_true", help="Launch desktop GUI (default)")
    mode.add_argument("--server", action="store_true", help="Start Flask web server")
    mode.add_argument("--cli",    nargs="*", metavar="ARG", help="CLI mode")

    parser.add_argument("--host",  default="127.0.0.1")
    parser.add_argument("--port",  default=5000, type=int)
    parser.add_argument("--debug", action="store_true")

    parsed = parser.parse_args()

    if parsed.server:
        _run_server(parsed.host, parsed.port, parsed.debug)
    elif parsed.cli is not None:
        _run_cli(parsed.cli)
    else:
        _run_gui()


if __name__ == "__main__":
    main()
