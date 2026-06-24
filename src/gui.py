"""
gui.py — Dark purple desktop GUI for TZ-Convert.

Requires: customtkinter >= 5.2  (pip install customtkinter)
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(__file__))

try:
    import customtkinter as ctk
except ImportError:
    print("customtkinter not found — run: pip install customtkinter")
    sys.exit(1)

from converter import (
    convert_time,
    format_time,
    get_current_time,
    get_utc_offset_str,
    get_world_clocks,
    parse_datetime,
)
from resolver import resolve_location, search_timezones

# ---------------------------------------------------------------------------
# Theme — Midnight-Ash purple palette
# ---------------------------------------------------------------------------
BG         = "#0a0a0a"
CARD       = "#1c1917"
CARD2      = "#231f1d"
ACCENT     = "#6829B1"
ACCENT_H   = "#7B32CC"
ACCENT_DIM = "#3D1870"
TEXT       = "#e2e8f0"
TEXT_DIM   = "#94a3b8"
TEXT_MUT   = "#64748b"
BORDER     = "#2d2926"
GREEN      = "#4ade80"
RED        = "#f87171"
FONT       = "Inter"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------

class Card(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=CARD, corner_radius=12,
                         border_width=1, border_color=BORDER, **kw)


class Lbl(ctk.CTkLabel):
    def __init__(self, master, text, size=13, bold=False, color=TEXT, **kw):
        super().__init__(master, text=text, font=(FONT, size, "bold" if bold else "normal"),
                         text_color=color, **kw)


class AccentBtn(ctk.CTkButton):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=ACCENT, hover_color=ACCENT_H,
                         text_color=TEXT, corner_radius=8, font=(FONT, 13, "bold"), **kw)


class GhostBtn(ctk.CTkButton):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", hover_color=CARD2,
                         text_color=TEXT_DIM, border_width=1, border_color=BORDER,
                         corner_radius=8, font=(FONT, 12), **kw)


class SearchEntry(ctk.CTkFrame):
    """Text entry with live autocomplete dropdown."""

    def __init__(self, master, width=300, placeholder="Search timezone…", **kw):
        super().__init__(master, fg_color="transparent", width=width, **kw)
        self._var = ctk.StringVar()
        self._entry = ctk.CTkEntry(
            self, textvariable=self._var, width=width,
            fg_color=CARD2, border_color=BORDER, text_color=TEXT,
            placeholder_text=placeholder, font=(FONT, 12), corner_radius=8,
        )
        self._entry.pack(fill="x")
        self._var.trace_add("write", self._on_type)
        self._popup: tk.Toplevel | None = None
        self._entry.bind("<FocusOut>", lambda _: self.after(150, self._close))
        self._entry.bind("<Return>", lambda _: self._close())

    def _on_type(self, *_):
        q = self._var.get()
        results = search_timezones(q, limit=10) if q else []
        if results:
            self._show(results)
        else:
            self._close()

    def _show(self, items: list[str]):
        self._close()
        x = self._entry.winfo_rootx()
        y = self._entry.winfo_rooty() + self._entry.winfo_height() + 2
        w = self._entry.winfo_width()
        h = min(len(items) * 32, 200) + 4

        self._popup = tk.Toplevel(self)
        self._popup.wm_overrideredirect(True)
        self._popup.geometry(f"{w}x{h}+{x}+{y}")
        self._popup.configure(bg=CARD)

        frame = ctk.CTkScrollableFrame(self._popup, fg_color=CARD,
                                       scrollbar_button_color=ACCENT_DIM,
                                       corner_radius=8)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        for item in items:
            ctk.CTkButton(
                frame, text=item, anchor="w", fg_color="transparent",
                hover_color=CARD2, text_color=TEXT, font=(FONT, 11), height=28,
                command=lambda v=item: self._pick(v),
            ).pack(fill="x", pady=1)

    def _pick(self, value: str):
        self._var.set(value)
        self._close()

    def _close(self):
        if self._popup:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None

    def get(self) -> str:
        return self._var.get().strip()

    def set(self, value: str):
        self._var.set(value)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TZ-Convert")
        self.geometry("940x700")
        self.minsize(820, 580)
        self.configure(fg_color=BG)
        self._build()
        self.after(1000, self._tick)

    # ── Layout ────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        hdr.pack(fill="x")
        Lbl(hdr, "TZ-Convert", size=18, bold=True).pack(side="left", padx=20, pady=14)
        self._clock_lbl = Lbl(hdr, "", size=12, color=TEXT_MUT)
        self._clock_lbl.pack(side="right", padx=20)

        # Tab bar
        tab_bar = ctk.CTkFrame(self, fg_color=CARD2, corner_radius=0, height=44)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        self._tab_btns: list[ctk.CTkButton] = []
        for label, key in [("Converter", "conv"), ("Resolver", "res"), ("World Clocks", "world")]:
            b = ctk.CTkButton(
                tab_bar, text=label, width=140,
                fg_color="transparent", hover_color=CARD, text_color=TEXT_DIM,
                corner_radius=0, font=(FONT, 13),
                command=lambda k=key: self._switch(k),
            )
            b.pack(side="left", padx=2, pady=4)
            b._key = key  # type: ignore[attr-defined]
            self._tab_btns.append(b)

        # Content
        self._area = ctk.CTkFrame(self, fg_color=BG)
        self._area.pack(fill="both", expand=True, padx=16, pady=12)

        self._panels = {
            "conv":  self._build_conv(),
            "res":   self._build_res(),
            "world": self._build_world(),
        }
        self._switch("conv")

    def _switch(self, key: str):
        for p in self._panels.values():
            p.pack_forget()
        self._panels[key].pack(fill="both", expand=True)
        for b in self._tab_btns:
            if b._key == key:  # type: ignore[attr-defined]
                b.configure(text_color=ACCENT, fg_color=CARD)
            else:
                b.configure(text_color=TEXT_DIM, fg_color="transparent")

    # ── Converter tab ──────────────────────────────────────────

    def _build_conv(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self._area, fg_color="transparent")
        card = Card(f)
        card.pack(fill="both", expand=True)

        Lbl(card, "Convert Time Between Zones", size=15, bold=True).pack(anchor="w", padx=20, pady=(18, 2))
        Lbl(card, "DST handled automatically via the IANA timezone database.", size=11, color=TEXT_MUT).pack(anchor="w", padx=20, pady=(0, 16))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=4)

        Lbl(row, "FROM TIMEZONE", size=10, color=TEXT_DIM).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._from = SearchEntry(row, width=310, placeholder="e.g. UTC, America/Denver, PST")
        self._from.set("UTC")
        self._from.grid(row=1, column=0)

        AccentBtn(row, text="⇄", width=48, height=36,
                  command=self._swap).grid(row=1, column=1, padx=14)

        Lbl(row, "TO TIMEZONE", size=10, color=TEXT_DIM).grid(row=0, column=2, sticky="w", pady=(0, 4))
        self._to = SearchEntry(row, width=310, placeholder="e.g. Australia/Sydney, NZST")
        self._to.set("Australia/Sydney")
        self._to.grid(row=1, column=2)

        row.columnconfigure(0, weight=1)
        row.columnconfigure(2, weight=1)

        dt_row = ctk.CTkFrame(card, fg_color="transparent")
        dt_row.pack(fill="x", padx=20, pady=(16, 8))

        Lbl(dt_row, "DATE & TIME  (YYYY-MM-DD HH:MM)", size=10, color=TEXT_DIM).pack(anchor="w", pady=(0, 4))
        inp_row = ctk.CTkFrame(dt_row, fg_color="transparent")
        inp_row.pack(fill="x")

        self._dt = ctk.CTkEntry(
            inp_row, placeholder_text="e.g. 2026-06-22 14:30", width=280,
            fg_color=CARD2, border_color=BORDER, text_color=TEXT,
            font=(FONT, 13), corner_radius=8,
        )
        self._dt.pack(side="left")
        GhostBtn(inp_row, text="Use Now", width=90, command=self._fill_now).pack(side="left", padx=10)
        AccentBtn(inp_row, text="Convert", width=100, command=self._do_conv).pack(side="left")

        self._conv_result = ctk.CTkFrame(card, fg_color=CARD2, corner_radius=10)
        self._conv_result.pack(fill="x", padx=20, pady=(14, 20))
        self._conv_lbl = Lbl(self._conv_result,
                             "Enter a time above and press Convert.",
                             size=13, color=TEXT_MUT)
        self._conv_lbl.pack(padx=20, pady=16)
        return f

    def _fill_now(self):
        now = datetime.now()
        self._dt.delete(0, "end")
        self._dt.insert(0, now.strftime("%Y-%m-%d %H:%M"))

    def _swap(self):
        a, b = self._from.get(), self._to.get()
        self._from.set(b)
        self._to.set(a)

    def _do_conv(self):
        from_raw = self._from.get()
        to_raw   = self._to.get()
        raw_dt   = self._dt.get().strip()

        if not raw_dt:
            self._set_conv("Enter a date and time.", RED)
            return
        if not from_raw:
            self._set_conv("Enter a source timezone.", RED)
            return
        if not to_raw:
            self._set_conv("Enter a target timezone.", RED)
            return

        from_tz, _ = resolve_location(from_raw)
        to_tz,   _ = resolve_location(to_raw)

        try:
            naive = parse_datetime(raw_dt)
            conv  = convert_time(naive, from_tz, to_tz)
            result_str = format_time(conv, "%A, %d %B %Y  %H:%M:%S")
            offset_str = get_utc_offset_str(to_tz)
            self._set_conv(f"{result_str}\n{to_tz}  ({offset_str})", GREEN)
        except ValueError as exc:
            self._set_conv(str(exc), RED)

    def _set_conv(self, text: str, color: str = TEXT):
        self._conv_lbl.configure(text=text, text_color=color)

    # ── Resolver tab ───────────────────────────────────────────

    def _build_res(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self._area, fg_color="transparent")
        card = Card(f)
        card.pack(fill="both", expand=True)

        Lbl(card, "Location to IANA Timezone", size=15, bold=True).pack(anchor="w", padx=20, pady=(18, 2))
        Lbl(card, "City, state, country, or abbreviation — get back a correct IANA string.",
            size=11, color=TEXT_MUT).pack(anchor="w", padx=20, pady=(0, 16))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=4)

        self._loc = ctk.CTkEntry(
            row, placeholder_text='e.g. "Denver", "Kansas", "PST", "Australia"',
            height=40, fg_color=CARD2, border_color=BORDER, text_color=TEXT,
            font=(FONT, 13), corner_radius=8,
        )
        self._loc.pack(side="left", fill="x", expand=True)
        self._loc.bind("<Return>", lambda _: self._do_res())
        AccentBtn(row, text="Resolve", width=100, command=self._do_res).pack(side="left", padx=(10, 0))

        # Quick examples
        eg = ctk.CTkFrame(card, fg_color="transparent")
        eg.pack(fill="x", padx=20, pady=(8, 0))
        Lbl(eg, "Examples:", size=11, color=TEXT_MUT).pack(side="left", padx=(0, 8))
        for ex in ["Denver", "Goodland, KS", "PST", "Australia", "Auckland"]:
            GhostBtn(eg, text=ex, width=120, height=26,
                     command=lambda e=ex: self._set_example(e)).pack(side="left", padx=3)

        self._res_frame = ctk.CTkScrollableFrame(card, fg_color="transparent", corner_radius=0)
        self._res_frame.pack(fill="both", expand=True, padx=20, pady=12)
        Lbl(self._res_frame,
            "Enter a location above to resolve its timezone.", size=13, color=TEXT_MUT).pack(pady=30)
        return f

    def _set_example(self, ex: str):
        self._loc.delete(0, "end")
        self._loc.insert(0, ex)
        self._do_res()

    def _do_res(self):
        loc = self._loc.get().strip()
        if not loc:
            return
        for w in self._res_frame.winfo_children():
            w.destroy()

        iana, method = resolve_location(loc)
        now    = get_current_time(iana)
        offset = get_utc_offset_str(iana)

        res_card = ctk.CTkFrame(self._res_frame, fg_color=CARD2, corner_radius=10)
        res_card.pack(fill="x", pady=4)

        Lbl(res_card, "RESOLVED TIMEZONE", size=10, color=TEXT_DIM).pack(anchor="w", padx=16, pady=(12, 2))
        Lbl(res_card, iana, size=20, bold=True, color=ACCENT).pack(anchor="w", padx=16)

        for label, value in [
            ("Current time", format_time(now, "%H:%M:%S  %a, %d %b %Y")),
            ("UTC offset",   offset),
            ("Method",       method.replace("~", " → ")),
        ]:
            r = ctk.CTkFrame(res_card, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=2)
            Lbl(r, f"{label}:", size=12, color=TEXT_DIM).pack(side="left", padx=(0, 8))
            Lbl(r, value, size=12).pack(side="left")

        AccentBtn(res_card, text="Copy IANA string", width=170,
                  command=lambda: self._copy(iana)).pack(anchor="w", padx=16, pady=(8, 14))

    def _copy(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", f'"{text}" copied to clipboard.')

    # ── World Clocks tab ───────────────────────────────────────

    def _build_world(self) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self._area, fg_color="transparent")
        Lbl(f, "World Clocks", size=15, bold=True).pack(anchor="w", pady=(0, 12))
        self._world_grid = ctk.CTkScrollableFrame(f, fg_color="transparent", corner_radius=0)
        self._world_grid.pack(fill="both", expand=True)
        self._world_card_refs: list[dict] = []
        self._build_world_cards()
        return f

    def _build_world_cards(self):
        for w in self._world_grid.winfo_children():
            w.destroy()
        self._world_card_refs.clear()

        clocks = get_world_clocks()
        cols = 2
        for i, clock in enumerate(clocks):
            row, col = divmod(i, cols)
            card = Card(self._world_grid)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self._world_grid.columnconfigure(col, weight=1)

            Lbl(card, clock["label"], size=14, bold=True).pack(anchor="w", padx=16, pady=(14, 0))
            Lbl(card, clock["tz"], size=10, color=TEXT_MUT).pack(anchor="w", padx=16)

            t_lbl = Lbl(card, clock["time"], size=26, bold=True, color=ACCENT)
            t_lbl.pack(anchor="w", padx=16, pady=(4, 0))

            d_lbl = Lbl(card, clock["date"], size=11, color=TEXT_DIM)
            d_lbl.pack(anchor="w", padx=16)

            o_lbl = Lbl(card, clock["offset"], size=11, color=TEXT_MUT)
            o_lbl.pack(anchor="w", padx=16, pady=(0, 14))

            self._world_card_refs.append({"tz": clock["tz"], "t": t_lbl, "d": d_lbl, "o": o_lbl})

    # ── Ticker ─────────────────────────────────────────────────

    def _tick(self):
        try:
            utc = get_current_time("UTC")
            self._clock_lbl.configure(text=format_time(utc, "UTC  %H:%M:%S  ·  %d %b %Y"))

            for ref in self._world_card_refs:
                now = get_current_time(ref["tz"])
                ref["t"].configure(text=format_time(now, "%H:%M:%S"))
                ref["d"].configure(text=format_time(now, "%a, %d %b %Y"))
        except Exception:
            pass
        self.after(1000, self._tick)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run():
    App().mainloop()


if __name__ == "__main__":
    run()
