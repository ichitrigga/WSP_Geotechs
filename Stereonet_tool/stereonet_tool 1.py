#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEREONET GENERATOR v2.4
pip install mplstereonet matplotlib pandas numpy
"""
import sys, os, math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import pandas as pd
import numpy as np
try:
    import mplstereonet
except ImportError:
    print("pip install mplstereonet"); sys.exit(1)
import matplotlib; matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

CONFIG = {
    "pole_color": "#228B22", "pole_size": 4, "pole_alpha": 0.55, "pole_marker": "o",
    "contour_cmap": "Blues", "contour_alpha": 0.45, "contour_levels": 10, "contour_sigma": 3,
    "max_cols": 4, "fig_dpi": 100, "subplot_size": 3.8,
    "title_fontsize": 11, "suptitle_fontsize": 16, "subtitle_fontsize": 12,
    "min_points_contour": 5,
    "type_labels": {"BD": "Bedding", "JT": "Joint", "FT": "Fault",
                     "VN": "Vein", "CO": "Contact", "SH": "Shear", "AP": "Aplite"},
    "auto_dip": "DIP", "auto_dipdir": "DIP DIRECTION",
    "auto_domain": "NST_ELC_ELN_Structural_Domains_Output",
    "auto_weathering": "NST_ELC_ECN_oxides_Output",
    "auto_lithology": "NST_ELC_ECN_Litho_Only_Output",
    "auto_type": "TYPE",
    "window_width": 1500, "window_height": 950, "filter_panel_w": 380,
}
NONE_LABEL = "(None)"

def _type_label(code):
    return CONFIG["type_labels"].get(str(code).strip(), str(code))

def _fix_azimuth_labels(ax):
    """Fix azimuth labels: remove defaults, place manual labels, keep grid."""
    # Remove default labels but KEEP the grid intact
    ax.set_azimuth_ticks([])
    # Place labels using correct formula (from StackOverflow)
    azimuths = np.arange(0, 360, 45)
    labx = 0.5 - 0.52 * np.cos(np.radians(azimuths + 90))
    laby = 0.5 + 0.52 * np.sin(np.radians(azimuths + 90))
    for i in range(len(azimuths)):
        ax.text(labx[i], laby[i], str(int(azimuths[i])) + "\u00b0",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=8, color="black")

def generate_stereonets(df, dip_col, dipdir_col, domain_col, domain_vals,
        weath_col, weath_vals, litho_col, litho_vals, type_col, type_vals,
        min_count=1, pole_color="#228B22", pole_size=4):
    work = df[[c for c in df.columns]].copy()
    work[dip_col] = pd.to_numeric(work[dip_col], errors="coerce")
    work[dipdir_col] = pd.to_numeric(work[dipdir_col], errors="coerce")
    work = work.dropna(subset=[dip_col, dipdir_col])
    ad = domain_col and domain_col != NONE_LABEL and domain_vals
    aw = weath_col and weath_col != NONE_LABEL and weath_vals
    al = litho_col and litho_col != NONE_LABEL and litho_vals
    at = type_col and type_col != NONE_LABEL and type_vals
    if ad: work = work[work[domain_col].isin(domain_vals)]
    if aw: work = work[work[weath_col].isin(weath_vals)]
    if al: work = work[work[litho_col].isin(litho_vals)]
    if at: work = work[work[type_col].isin(type_vals)]
    if work.empty: raise ValueError("No data after filters.")
    work = work.copy()
    work["_strike"] = (work[dipdir_col].values - 90) % 360
    # Main title = Domain
    if ad:
        if len(domain_vals) == 1: mt = str(domain_vals[0])
        else: mt = ", ".join(str(v) for v in sorted(domain_vals, key=str))
    else: mt = "All Domains"
    # Subtitle = Weathering | Lithology
    sp = []
    if aw: sp.append(" + ".join(str(v) for v in sorted(weath_vals, key=str)))
    if al: sp.append(" + ".join(str(v) for v in sorted(litho_vals, key=str)))
    subtitle = "  |  ".join(sp) if sp else ""
    # Define subplot groups
    if at:
        gk = type_col
        to = list(CONFIG["type_labels"].keys())
        gr = [g for g, s in work.groupby(type_col, sort=False) if len(s) >= min_count]
        seen = set(); groups = []
        for g in gr:
            if g not in seen: seen.add(g); groups.append(g)
        groups.sort(key=lambda t: to.index(t) if t in to else 999)
    elif ad:
        gk = domain_col
        gr = [g for g, s in work.groupby(domain_col, sort=False) if len(s) >= min_count]
        seen = set(); groups = []
        for g in gr:
            if g not in seen: seen.add(g); groups.append(g)
        groups.sort(key=str)
    else:
        work["_group"] = "All Data"; gk = "_group"; groups = ["All Data"]
    if not groups: raise ValueError("No groups found.")
    n_plots = len(groups)
    nc = min(n_plots, CONFIG["max_cols"])
    nr = math.ceil(n_plots / nc)
    fw = CONFIG["subplot_size"] * nc + 1.5
    fh = CONFIG["subplot_size"] * nr + 2.2
    fig = plt.figure(figsize=(fw, fh), dpi=CONFIG["fig_dpi"])
    fig.suptitle(mt, fontsize=CONFIG["suptitle_fontsize"], fontweight="bold", y=0.98)
    if subtitle:
        fig.text(0.5, 0.94, subtitle, ha="center", va="top",
                 fontsize=CONFIG["subtitle_fontsize"], fontstyle="italic", color="dimgray")
    for idx, grp in enumerate(groups):
        ax = fig.add_subplot(nr, nc, idx + 1, projection="stereonet")
        sub = work[work[gk] == grp]
        strikes = sub["_strike"].values.astype(float)
        dips = sub[dip_col].values.astype(float)
        n = len(strikes)
        if n >= CONFIG["min_points_contour"]:
            try:
                ax.density_contourf(strikes, dips, measurement="poles",
                    cmap=CONFIG["contour_cmap"], alpha=CONFIG["contour_alpha"],
                    levels=CONFIG["contour_levels"], sigma=CONFIG["contour_sigma"])
                ax.density_contour(strikes, dips, measurement="poles",
                    colors="steelblue", alpha=0.3, linewidths=0.5,
                    sigma=CONFIG["contour_sigma"])
            except: pass
        ax.pole(strikes, dips, CONFIG["pole_marker"], color=pole_color,
                markersize=pole_size, alpha=CONFIG["pole_alpha"], markeredgecolor="none")
        ax.grid(True, ls=":", alpha=0.6)
        _fix_azimuth_labels(ax)
        if at and gk == type_col:
            ts = _type_label(grp) + "\n(n=" + str(n) + ")"
        else:
            ts = str(grp) + "\n(n=" + str(n) + ")"
        ax.set_title(ts, fontsize=CONFIG["title_fontsize"], fontweight="bold", pad=20)
    tm = 0.87 if subtitle else 0.90
    fig.subplots_adjust(top=tm, bottom=0.03, left=0.03, right=0.97,
                        hspace=0.52, wspace=0.20)
    return fig

class FilterPanel(ttk.LabelFrame):
    def __init__(self, master, label, **kw):
        super().__init__(master, text=f"  {label}  ", padding=4, **kw)
        self._all_columns = []
        top = ttk.Frame(self); top.pack(fill="x", pady=(0, 3))
        ttk.Label(top, text="Column:").pack(side="left")
        self.col_var = tk.StringVar(value=NONE_LABEL)
        self.col_combo = ttk.Combobox(top, textvariable=self.col_var,
                                      width=35, state="readonly")
        self.col_combo.pack(side="left", fill="x", expand=True, padx=4)
        self.col_combo.bind("<<ComboboxSelected>>", self._on_col_change)
        br = ttk.Frame(self); br.pack(fill="x")
        ttk.Button(br, text="Select All", width=10,
                   command=self._select_all).pack(side="left", padx=2)
        ttk.Button(br, text="Clear", width=10,
                   command=self._clear).pack(side="left", padx=2)
        self._cv = tk.StringVar(value="")
        ttk.Label(br, textvariable=self._cv, foreground="gray").pack(side="right", padx=4)
        lf = ttk.Frame(self); lf.pack(fill="both", expand=True, pady=(3, 0))
        self.listbox = tk.Listbox(lf, selectmode="extended", height=5,
                                  exportselection=False)
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._dataframe = None

    def set_columns(self, cols):
        self._all_columns = cols
        self.col_combo["values"] = [NONE_LABEL] + cols

    def set_dataframe(self, df):
        self._dataframe = df; self._refresh()

    def auto_select_column(self, cn):
        if cn in self._all_columns:
            self.col_var.set(cn); self._refresh()

    def get_column(self): return self.col_var.get()

    def get_selected_values(self):
        return [self.listbox.get(i) for i in self.listbox.curselection()]

    def _on_col_change(self, e=None): self._refresh()

    def _refresh(self):
        self.listbox.delete(0, "end")
        c = self.col_var.get()
        if c == NONE_LABEL or self._dataframe is None:
            self._cv.set(""); return
        if c not in self._dataframe.columns:
            self._cv.set(""); return
        vs = sorted(self._dataframe[c].dropna().unique(), key=str)
        for v in vs: self.listbox.insert("end", str(v))
        self.listbox.select_set(0, "end")
        self._cv.set(f"{len(vs)} values")

    def _select_all(self): self.listbox.select_set(0, "end")

    def _clear(self): self.listbox.selection_clear(0, "end")

class StereonetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stereonet Generator v2.4")
        self.root.geometry(f"{CONFIG['window_width']}x{CONFIG['window_height']}")
        self.root.minsize(1000, 700)
        self.df = None
        self.current_fig = None
        self._pole_color = CONFIG["pole_color"]
        self._build_gui()

    def _build_gui(self):
        # File selection
        ff = ttk.LabelFrame(self.root, text="  Input File  ", padding=6)
        ff.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(ff, text="CSV:").pack(side="left")
        self.file_var = tk.StringVar()
        ttk.Entry(ff, textvariable=self.file_var, width=90).pack(
            side="left", fill="x", expand=True, padx=4)
        ttk.Button(ff, text="Browse...", command=self._browse).pack(side="left", padx=2)
        ttk.Button(ff, text="Load", command=self._load).pack(side="left", padx=2)

        # Main paned window
        pw = ttk.PanedWindow(self.root, orient="horizontal")
        pw.pack(fill="both", expand=True, padx=8, pady=4)
        left = ttk.Frame(pw, width=CONFIG["filter_panel_w"])
        pw.add(left, weight=0)

        # Orientation selectors
        ori = ttk.LabelFrame(left, text="  Orientation  ", padding=4)
        ori.pack(fill="x", pady=(0, 4))
        r0 = ttk.Frame(ori); r0.pack(fill="x", pady=1)
        ttk.Label(r0, text="DIP:").pack(side="left")
        self.dip_var = tk.StringVar()
        self.dip_combo = ttk.Combobox(r0, textvariable=self.dip_var,
                                      width=32, state="readonly")
        self.dip_combo.pack(side="left", padx=4)
        r1 = ttk.Frame(ori); r1.pack(fill="x", pady=1)
        ttk.Label(r1, text="DIP DIR:").pack(side="left")
        self.dipdir_var = tk.StringVar()
        self.dipdir_combo = ttk.Combobox(r1, textvariable=self.dipdir_var,
                                         width=32, state="readonly")
        self.dipdir_combo.pack(side="left", padx=4)
        r2 = ttk.Frame(ori); r2.pack(fill="x", pady=1)
        ttk.Label(r2, text="Min Count:").pack(side="left")
        self.mincount_var = tk.IntVar(value=3)
        ttk.Spinbox(r2, from_=1, to=5000, textvariable=self.mincount_var,
                    width=6).pack(side="left", padx=4)

        # Pole style controls
        sf = ttk.LabelFrame(left, text="  Pole Style  ", padding=4)
        sf.pack(fill="x", pady=(0, 4))
        cr = ttk.Frame(sf); cr.pack(fill="x", pady=2)
        ttk.Label(cr, text="Color:").pack(side="left")
        self._cprev = tk.Label(cr, text="    ", width=4,
                               bg=self._pole_color, relief="sunken")
        self._cprev.pack(side="left", padx=4)
        ttk.Button(cr, text="Choose...", command=self._pick_color).pack(
            side="left", padx=4)
        self._chex = tk.StringVar(value=self._pole_color)
        ttk.Label(cr, textvariable=self._chex, foreground="gray").pack(
            side="left", padx=4)
        sr = ttk.Frame(sf); sr.pack(fill="x", pady=2)
        ttk.Label(sr, text="Size:").pack(side="left")
        self.pole_size_var = tk.IntVar(value=CONFIG["pole_size"])
        ttk.Spinbox(sr, from_=1, to=15, textvariable=self.pole_size_var,
                    width=4).pack(side="left", padx=4)
        ttk.Label(sr, text="(1-15)", foreground="gray").pack(side="left")

        # Four filter panels
        self.fp_domain = FilterPanel(left, "Domain")
        self.fp_domain.pack(fill="both", expand=True, pady=2)
        self.fp_weath = FilterPanel(left, "Weathering")
        self.fp_weath.pack(fill="both", expand=True, pady=2)
        self.fp_litho = FilterPanel(left, "Lithology")
        self.fp_litho.pack(fill="both", expand=True, pady=2)
        self.fp_type = FilterPanel(left, "Type")
        self.fp_type.pack(fill="both", expand=True, pady=2)

        # Right side - viewer
        right = ttk.Frame(pw); pw.add(right, weight=1)
        bb = ttk.Frame(right); bb.pack(fill="x", pady=(0, 4))
        self.btn_gen = ttk.Button(bb, text="Generate Stereonets",
                                  command=self._generate, state="disabled")
        self.btn_gen.pack(side="left", padx=4)
        self.btn_png = ttk.Button(bb, text="Save PNG",
                                  command=lambda: self._save("png"), state="disabled")
        self.btn_png.pack(side="left", padx=4)
        self.btn_pdf = ttk.Button(bb, text="Save PDF",
                                  command=lambda: self._save("pdf"), state="disabled")
        self.btn_pdf.pack(side="left", padx=4)
        self.status_var = tk.StringVar(value="Ready - load a CSV.")
        ttk.Label(bb, textvariable=self.status_var,
                  foreground="gray").pack(side="right", padx=8)

        # Canvas
        self.canvas_frame = ttk.Frame(right)
        self.canvas_frame.pack(fill="both", expand=True)
        self.fig = Figure(figsize=(10, 6), dpi=CONFIG["fig_dpi"])
        self.fig.text(0.5, 0.5, "Load CSV and Generate",
                      ha="center", va="center", fontsize=14, color="gray")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar_frame = ttk.Frame(right)
        self.toolbar_frame.pack(fill="x")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def _pick_color(self):
        r = colorchooser.askcolor(initialcolor=self._pole_color, title="Pole Color")
        if r and r[1]:
            self._pole_color = r[1]
            self._cprev.configure(bg=r[1])
            self._chex.set(r[1])

    def _browse(self):
        p = filedialog.askopenfilename(
            filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if p: self.file_var.set(p)

    def _load(self):
        fp = self.file_var.get().strip()
        if not fp or not os.path.isfile(fp):
            messagebox.showerror("Error", "Select valid CSV.")
            return
        try:
            self.df = pd.read_csv(fp)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        cols = list(self.df.columns)
        self.dip_combo["values"] = cols
        self.dipdir_combo["values"] = cols
        for c in cols:
            cu = c.strip().upper()
            if cu == "DIP": self.dip_var.set(c)
            elif cu in ("DIP DIRECTION", "DIPDIRECTION", "DIP_DIRECTION"):
                self.dipdir_var.set(c)
        for fp_w in (self.fp_domain, self.fp_weath, self.fp_litho, self.fp_type):
            fp_w.set_columns(cols)
            fp_w.set_dataframe(self.df)
        self.fp_domain.auto_select_column(CONFIG["auto_domain"])
        self.fp_weath.auto_select_column(CONFIG["auto_weathering"])
        self.fp_litho.auto_select_column(CONFIG["auto_lithology"])
        self.fp_type.auto_select_column(CONFIG["auto_type"])
        self.btn_gen["state"] = "normal"
        self.status_var.set(
            f"Loaded: {os.path.basename(fp)} | {len(self.df)} rows")

    def _generate(self):
        if self.df is None: return
        dip = self.dip_var.get()
        dd = self.dipdir_var.get()
        if not dip or not dd:
            messagebox.showwarning("Warning", "Select DIP and DIP DIR.")
            return
        self.status_var.set("Generating...")
        self.root.update_idletasks()
        try:
            fig = generate_stereonets(
                self.df, dip, dd,
                self.fp_domain.get_column(), self.fp_domain.get_selected_values(),
                self.fp_weath.get_column(), self.fp_weath.get_selected_values(),
                self.fp_litho.get_column(), self.fp_litho.get_selected_values(),
                self.fp_type.get_column(), self.fp_type.get_selected_values(),
                self.mincount_var.get(), self._pole_color,
                self.pole_size_var.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error.")
            return
        self.canvas.get_tk_widget().destroy()
        self.toolbar.destroy()
        self.current_fig = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        self.btn_png["state"] = "normal"
        self.btn_pdf["state"] = "normal"
        self.status_var.set("Done.")

    def _save(self, ext):
        if not self.current_fig: return
        fp = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[(ext.upper(), f"*.{ext}")])
        if fp:
            self.current_fig.savefig(fp, dpi=200, bbox_inches="tight",
                                     facecolor="white")
            self.status_var.set(f"Saved: {os.path.basename(fp)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StereonetApp(root)
    root.mainloop()
