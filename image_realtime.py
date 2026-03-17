#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║    Real-Time Image Modifier — WhatsApp Forensics v2.0           ║
║    Authorized Security Research Only                            ║
╚══════════════════════════════════════════════════════════════════╝

Standalone GUI module.  Launch directly:
    python3 image_realtime.py

Or programmatically:
    from image_realtime import RealTimeImageEditor
    RealTimeImageEditor().run()
"""

import os
import io
import copy
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageTk

# ─── colour palette ──────────────────────────────────────────────
BG       = "#0f0f1a"
BG2      = "#1a1a2e"
ACCENT   = "#6c63ff"
ACCENT2  = "#ff6584"
TEXT     = "#e0e0ff"
DIMTEXT  = "#6c6c9a"
SUCCESS  = "#4ade80"
WARN     = "#facc15"
PANEL    = "#16213e"
BORDER   = "#2a2a4a"

FONT_SM  = ("Segoe UI", 9)
FONT_MD  = ("Segoe UI", 10)
FONT_LG  = ("Segoe UI", 12, "bold")
FONT_XL  = ("Segoe UI", 14, "bold")


# ─── themed slider helper ───────────────────────────────────────
def make_slider(parent, label, from_, to, default, step=1,
                row=0, command=None):
    """Creates a labelled, value-displaying slider row."""
    tk.Label(parent, text=label, bg=PANEL, fg=TEXT, font=FONT_SM,
             anchor="w").grid(row=row, column=0, sticky="w", padx=(8, 4), pady=3)

    var = tk.DoubleVar(value=default)
    val_lbl = tk.Label(parent, textvariable=var, bg=PANEL, fg=ACCENT,
                       font=FONT_SM, width=5)
    val_lbl.grid(row=row, column=2, padx=(4, 8))

    def _cb(v):
        var.set(round(float(v), 2))
        if command:
            command()

    sl = ttk.Scale(parent, from_=from_, to=to, orient="horizontal",
                   variable=var, command=_cb)
    sl.grid(row=row, column=1, sticky="ew", padx=2)
    parent.columnconfigure(1, weight=1)
    return var, sl


class RealTimeImageEditor:
    """Main GUI class for real-time image modification."""

    MAX_PREVIEW = (820, 540)   # max preview canvas size

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Real-Time Image Modifier — WhatsApp Forensics v2.0")
        self.root.configure(bg=BG)
        self.root.geometry("1300x800")
        self.root.minsize(900, 620)

        # state
        self.original_img  = None    # pristine original
        self.current_img   = None    # displayed preview
        self.history       = []      # undo stack
        self.redo_stack    = []
        self.tk_photo      = None    # keep reference
        self.overlay_color = "#ff0000"
        self.tint_color    = "#000000"

        self._build_style()
        self._build_ui()
        self._update_status("No image loaded. Use  File → Open Image  to begin.")

    # ── style ─────────────────────────────────────────────────────
    def _build_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TScale", background=PANEL, troughcolor=BG2,
                         sliderlength=18, sliderrelief="flat")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG2, foreground=TEXT,
                         padding=[12, 5], font=FONT_SM)
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#ffffff")])
        style.configure("TSeparator", background=BORDER)

    # ── main layout ───────────────────────────────────────────────
    def _build_ui(self):
        # ── top toolbar ──
        toolbar = tk.Frame(self.root, bg=BG2, height=46)
        toolbar.pack(fill="x", side="top")
        self._make_toolbar(toolbar)

        # ── body: left panels + canvas ──
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        # left control panel
        ctrl_frame = tk.Frame(body, bg=BG2, width=320)
        ctrl_frame.pack(side="left", fill="y")
        ctrl_frame.pack_propagate(False)

        notebook = ttk.Notebook(ctrl_frame)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)

        self._build_adjust_tab(notebook)
        self._build_filter_tab(notebook)
        self._build_overlay_tab(notebook)
        self._build_transform_tab(notebook)
        self._build_forensics_tab(notebook)

        # ── apply / reset buttons ──
        btn_bar = tk.Frame(ctrl_frame, bg=BG2)
        btn_bar.pack(fill="x", padx=8, pady=6)
        self._btn(btn_bar, "▶  Apply & Preview", self._apply_all,
                  ACCENT).pack(side="left", fill="x", expand=True, padx=(0,3))
        self._btn(btn_bar, "↩ Reset", self._reset,
                  ACCENT2).pack(side="left", fill="x", expand=True, padx=(3,0))

        # canvas area
        canvas_frame = tk.Frame(body, bg=BG)
        canvas_frame.pack(side="left", fill="both", expand=True)
        self._build_canvas(canvas_frame)

        # status bar
        self.status_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.status_var, bg=PANEL,
                 fg=DIMTEXT, font=FONT_SM, anchor="w",
                 padx=10).pack(fill="x", side="bottom", ipady=4)

    # ── toolbar ───────────────────────────────────────────────────
    def _make_toolbar(self, tb):
        items = [
            ("📂  Open", self._open_file),
            ("💾  Save", self._save_file),
            ("↩  Undo", self._undo),
            ("↪  Redo", self._redo),
            ("|",  None),
            ("🔄  Apply All", self._apply_all),
            ("🗑  Reset",  self._reset),
        ]
        for label, cmd in items:
            if label == "|":
                tk.Frame(tb, bg=BORDER, width=2).pack(side="left",
                                                       fill="y", pady=6, padx=6)
                continue
            btn = tk.Button(tb, text=label, command=cmd, bg=BG2, fg=TEXT,
                            activebackground=ACCENT, activeforeground="white",
                            relief="flat", font=FONT_SM, padx=12, pady=8,
                            cursor="hand2", borderwidth=0)
            btn.pack(side="left")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=TEXT))

        # pricing badge (right side)
        tk.Label(tb, text="Original $530  →  Offer $230",
                 bg=BG2, fg=SUCCESS, font=("Segoe UI", 9, "bold"),
                 padx=12).pack(side="right")

    # ── canvas ────────────────────────────────────────────────────
    def _build_canvas(self, parent):
        # top info bar
        info = tk.Frame(parent, bg=PANEL, height=30)
        info.pack(fill="x")
        self.info_var = tk.StringVar(value="No image loaded")
        tk.Label(info, textvariable=self.info_var, bg=PANEL, fg=DIMTEXT,
                 font=FONT_SM, padx=10).pack(side="left", fill="y")

        # canvas with scrollbars
        cv_frame = tk.Frame(parent, bg=BG, relief="sunken", bd=2)
        cv_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.canvas = tk.Canvas(cv_frame, bg="#0d0d1a",
                                highlightthickness=0, cursor="crosshair")
        h_sb = tk.Scrollbar(cv_frame, orient="horizontal",
                             command=self.canvas.xview)
        v_sb = tk.Scrollbar(cv_frame, orient="vertical",
                             command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_sb.set,
                              yscrollcommand=v_sb.set)
        h_sb.pack(side="bottom", fill="x")
        v_sb.pack(side="right",  fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._refresh_canvas())

        # crop rectangle
        self._crop_rect  = None
        self._crop_start = None
        self.canvas.bind("<ButtonPress-1>",   self._crop_start_cb)
        self.canvas.bind("<B1-Motion>",       self._crop_drag_cb)
        self.canvas.bind("<ButtonRelease-1>", self._crop_end_cb)
        self._crop_mode = False   # toggled by a button

    # ── tab: Adjustments ─────────────────────────────────────────
    def _build_adjust_tab(self, nb):
        frm = self._tab(nb, "🎨 Adjust")
        sliders = [
            ("Brightness",   0.1, 3.0, 1.0),
            ("Contrast",     0.1, 3.0, 1.0),
            ("Saturation",   0.0, 3.0, 1.0),
            ("Sharpness",    0.0, 5.0, 1.0),
            ("Blur (px)",    0,   20,  0  ),
        ]
        self.s_bright  = None
        self.s_contrast= None
        self.s_sat     = None
        self.s_sharp   = None
        self.s_blur    = None

        attrs = ["s_bright","s_contrast","s_sat","s_sharp","s_blur"]
        for i, (lbl, lo, hi, dflt) in enumerate(sliders):
            var, _ = make_slider(frm, lbl, lo, hi, dflt,
                                 row=i, command=self._live_preview)
            setattr(self, attrs[i], var)

    # ── tab: Filters ──────────────────────────────────────────────
    def _build_filter_tab(self, nb):
        frm = self._tab(nb, "✨ Filters")

        self.filter_var = tk.StringVar(value="None")
        filters = ["None","Grayscale","Sepia","Invert","Edge Detect",
                   "Emboss","Find Edges","Smooth","Detail",
                   "Gaussian Blur","Contour","Posterize"]
        tk.Label(frm, text="Filter", bg=PANEL, fg=TEXT,
                 font=FONT_SM).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        dd = ttk.Combobox(frm, textvariable=self.filter_var,
                          values=filters, state="readonly", width=20)
        dd.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        dd.bind("<<ComboboxSelected>>", lambda e: self._live_preview())
        frm.columnconfigure(1, weight=1)

        # tint
        tk.Label(frm, text="Colour Tint", bg=PANEL, fg=TEXT,
                 font=FONT_SM).grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.tint_var = tk.DoubleVar(value=0)
        ttk.Scale(frm, from_=0, to=1, orient="horizontal",
                  variable=self.tint_var,
                  command=lambda v: self._live_preview()
                  ).grid(row=1, column=1, sticky="ew", padx=8)
        self._btn(frm, "Pick Tint Colour", self._pick_tint, ACCENT,
                  ).grid(row=2, column=0, columnspan=2, sticky="ew",
                         padx=8, pady=4)

        self.tint_lbl = tk.Label(frm, bg=self.tint_color,
                                  width=4, relief="sunken")
        self.tint_lbl.grid(row=2, column=2, padx=4)

    # ── tab: Text Overlay ─────────────────────────────────────────
    def _build_overlay_tab(self, nb):
        frm = self._tab(nb, "✏️  Overlay")

        rows = [
            ("Text",      "text_ov",  ""),
            ("X pos (%)", "ov_x",     "10"),
            ("Y pos (%)", "ov_y",     "10"),
            ("Font size", "ov_fs",    "28"),
            ("Opacity",   "ov_alpha", "200"),
        ]
        self._ov_vars = {}
        for i, (lbl, key, dflt) in enumerate(rows):
            tk.Label(frm, text=lbl, bg=PANEL, fg=TEXT,
                     font=FONT_SM, anchor="w").grid(row=i, column=0,
                                                     sticky="w", padx=8, pady=3)
            var = tk.StringVar(value=dflt)
            e = tk.Entry(frm, textvariable=var, bg=BG2, fg=TEXT,
                         insertbackground=TEXT, font=FONT_SM, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1)
            e.grid(row=i, column=1, sticky="ew", padx=8, pady=3)
            e.bind("<KeyRelease>", lambda ev: self._live_preview())
            self._ov_vars[key] = var
        frm.columnconfigure(1, weight=1)

        self._btn(frm, "Overlay Colour", self._pick_overlay_colour,
                  ACCENT).grid(row=len(rows), column=0, columnspan=2,
                                sticky="ew", padx=8, pady=4)
        self.ov_colour_lbl = tk.Label(frm, bg=self.overlay_color,
                                       width=4, relief="sunken")
        self.ov_colour_lbl.grid(row=len(rows), column=2, padx=4)

    # ── tab: Transform ────────────────────────────────────────────
    def _build_transform_tab(self, nb):
        frm = self._tab(nb, "🔄 Transform")

        tk.Label(frm, text="Rotate (°)", bg=PANEL, fg=TEXT,
                 font=FONT_SM).grid(row=0, column=0, sticky="w", padx=8)
        self.rot_var, _ = make_slider(frm, "Rotate (°)", -180, 180, 0,
                                      row=0, command=self._live_preview)

        btn_pairs = [
            ("↔  Flip Horizontal", self._flip_h),
            ("↕  Flip Vertical",   self._flip_v),
            ("✂  Crop Mode",       self._toggle_crop),
            ("↩  Discard Crop",    self._discard_crop),
        ]
        for i, (lbl, cmd) in enumerate(btn_pairs, 2):
            self._btn(frm, lbl, cmd, ACCENT if i % 2 == 0 else PANEL
                      ).grid(row=i, column=0, columnspan=3, sticky="ew",
                              padx=8, pady=3)
        frm.columnconfigure(1, weight=1)

    # ── tab: Forensics ────────────────────────────────────────────
    def _build_forensics_tab(self, nb):
        frm = self._tab(nb, "🔍 Forensics")

        # payload embed
        tk.Label(frm, text="Hidden Payload", bg=PANEL, fg=TEXT,
                 font=FONT_SM, anchor="w").grid(row=0, column=0,
                                                 sticky="w", padx=8, pady=4)
        self.payload_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.payload_var, bg=BG2, fg=TEXT,
                 insertbackground=TEXT, font=FONT_SM, relief="flat",
                 highlightbackground=BORDER,
                 highlightthickness=1).grid(row=0, column=1, sticky="ew",
                                             padx=8, pady=4)
        self._btn(frm, "Embed Payload Into Saved File",
                  self._embed_payload, ACCENT2
                  ).grid(row=1, column=0, columnspan=2, sticky="ew",
                          padx=8, pady=2)

        ttk.Separator(frm, orient="horizontal").grid(row=2, column=0,
                                                      columnspan=2,
                                                      sticky="ew", pady=6)

        # ELA (Error Level Analysis) – forensics detection
        self._btn(frm, "📊  Error Level Analysis (ELA)",
                  self._run_ela, ACCENT
                  ).grid(row=3, column=0, columnspan=2, sticky="ew",
                          padx=8, pady=2)

        # Histogram
        self._btn(frm, "📈  Show Histogram",
                  self._show_histogram, ACCENT
                  ).grid(row=4, column=0, columnspan=2, sticky="ew",
                          padx=8, pady=2)

        # Metadata dump
        self._btn(frm, "🏷️  Read EXIF / Metadata",
                  self._read_metadata, ACCENT
                  ).grid(row=5, column=0, columnspan=2, sticky="ew",
                          padx=8, pady=2)

        frm.columnconfigure(1, weight=1)

    # ── helper builders ───────────────────────────────────────────
    def _tab(self, nb, label):
        f = tk.Frame(nb, bg=PANEL)
        nb.add(f, text=label)
        return f

    @staticmethod
    def _btn(parent, text, cmd, bg=PANEL, fg=TEXT):
        b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                      activebackground=ACCENT, activeforeground="white",
                      relief="flat", font=FONT_SM, cursor="hand2",
                      borderwidth=0, padx=6, pady=5)
        b.bind("<Enter>", lambda e: b.configure(bg=ACCENT, fg="white"))
        b.bind("<Leave>", lambda e: b.configure(bg=bg, fg=fg))
        return b

    # ── I/O ───────────────────────────────────────────────────────
    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp *.gif"),
                       ("All files", "*.*")]
        )
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA")
            self.original_img = img.copy()
            self.current_img  = img.copy()
            self.history      = []
            self.redo_stack   = []
            self._source_path = path
            self._refresh_canvas()
            self._update_info()
            self._update_status(f"Loaded: {os.path.basename(path)}")
        except Exception as ex:
            messagebox.showerror("Open Error", str(ex))

    def _save_file(self):
        if self.current_img is None:
            messagebox.showwarning("No Image", "Open an image first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Modified Image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All", "*.*")]
        )
        if not path:
            return
        try:
            out = self.current_img.convert("RGB") if path.lower().endswith(
                ('.jpg', '.jpeg')) else self.current_img
            out.save(path)
            self._update_status(f"Saved → {os.path.basename(path)}")
        except Exception as ex:
            messagebox.showerror("Save Error", str(ex))

    # ── apply transformations ─────────────────────────────────────
    def _get_adjusted(self):
        """Return a fully processed image from all current slider/control values."""
        if self.original_img is None:
            return None
        img = self.original_img.copy().convert("RGB")

        # ── Adjustments ──
        img = ImageEnhance.Brightness(img).enhance(self.s_bright.get())
        img = ImageEnhance.Contrast(img).enhance(self.s_contrast.get())
        img = ImageEnhance.Color(img).enhance(self.s_sat.get())
        img = ImageEnhance.Sharpness(img).enhance(self.s_sharp.get())

        blur_r = int(self.s_blur.get())
        if blur_r > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_r))

        # ── Filter ──
        f = self.filter_var.get()
        if f == "Grayscale":
            img = img.convert("L").convert("RGB")
        elif f == "Sepia":
            img = img.convert("L").convert("RGB")
            sepia = Image.new("RGB", img.size)
            px = img.load(); sp = sepia.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = px[x, y]
                    sp[x, y] = (
                        min(255, int(r * 0.393 + g * 0.769 + b * 0.189)),
                        min(255, int(r * 0.349 + g * 0.686 + b * 0.168)),
                        min(255, int(r * 0.272 + g * 0.534 + b * 0.131)),
                    )
            img = sepia
        elif f == "Invert":
            from PIL import ImageChops
            img = ImageChops.invert(img)
        elif f == "Edge Detect":
            img = img.filter(ImageFilter.FIND_EDGES)
        elif f == "Emboss":
            img = img.filter(ImageFilter.EMBOSS)
        elif f == "Find Edges":
            img = img.filter(ImageFilter.FIND_EDGES)
        elif f == "Smooth":
            img = img.filter(ImageFilter.SMOOTH_MORE)
        elif f == "Detail":
            img = img.filter(ImageFilter.DETAIL)
        elif f == "Gaussian Blur":
            img = img.filter(ImageFilter.GaussianBlur(5))
        elif f == "Contour":
            img = img.filter(ImageFilter.CONTOUR)
        elif f == "Posterize":
            from PIL import ImageOps
            img = ImageOps.posterize(img, 3)

        # ── Tint ──
        tint = self.tint_var.get()
        if tint > 0:
            tc   = self.tint_color.lstrip("#")
            tr, tg, tb = [int(tc[i:i+2], 16) for i in (0, 2, 4)]
            tint_layer = Image.new("RGB", img.size, (tr, tg, tb))
            img = Image.blend(img, tint_layer, tint * 0.8)

        # ── Rotation ──
        angle = self.rot_var.get()
        if angle != 0:
            img = img.rotate(angle, expand=True, fillcolor=(0, 0, 0))

        # ── Text Overlay ──
        text = self._ov_vars["text_ov"].get().strip()
        if text:
            try:
                ox  = float(self._ov_vars["ov_x"].get() or 10) / 100
                oy  = float(self._ov_vars["ov_y"].get() or 10) / 100
                fs  = int(self._ov_vars["ov_fs"].get() or 28)
                alp = int(self._ov_vars["ov_alpha"].get() or 200)
                oc  = self.overlay_color.lstrip("#")
                or_, og, ob = [int(oc[i:i+2], 16) for i in (0, 2, 4)]

                overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)
                except Exception:
                    font = ImageFont.load_default()
                x_px = int(img.width  * ox)
                y_px = int(img.height * oy)
                draw.text((x_px, y_px), text, font=font,
                          fill=(or_, og, ob, alp))
                img = Image.alpha_composite(img.convert("RGBA"),
                                            overlay).convert("RGB")
            except Exception:
                pass

        return img

    def _apply_all(self):
        """Push current state to history and refresh canvas."""
        if self.original_img is None:
            return
        if self.current_img is not None:
            self.history.append(self.current_img.copy())
            if len(self.history) > 30:
                self.history.pop(0)
        self.redo_stack.clear()
        self.current_img = self._get_adjusted()
        self.original_img = self.current_img.copy()   # bake in changes
        self._reset_sliders()
        self._refresh_canvas()
        self._update_status("Changes applied and baked in.")

    def _live_preview(self):
        """Preview without baking — does not affect history."""
        if self.original_img is None:
            return
        preview = self._get_adjusted()
        if preview:
            self._show_on_canvas(preview)

    def _reset(self):
        if not self.history:
            messagebox.showinfo("Nothing to reset", "No history to revert to.")
            return
        self.original_img = self.history[0].copy()
        self.current_img  = self.history[0].copy()
        self.history.clear()
        self.redo_stack.clear()
        self._reset_sliders()
        self._refresh_canvas()
        self._update_status("Reset to original.")

    def _reset_sliders(self):
        self.s_bright.set(1.0)
        self.s_contrast.set(1.0)
        self.s_sat.set(1.0)
        self.s_sharp.set(1.0)
        self.s_blur.set(0)
        self.rot_var.set(0)
        self.tint_var.set(0)
        self.filter_var.set("None")

    # ── undo / redo ───────────────────────────────────────────────
    def _undo(self):
        if not self.history:
            self._update_status("Nothing to undo.")
            return
        self.redo_stack.append(self.current_img.copy())
        self.current_img = self.history.pop()
        self.original_img = self.current_img.copy()
        self._refresh_canvas()
        self._update_status("Undo.")

    def _redo(self):
        if not self.redo_stack:
            self._update_status("Nothing to redo.")
            return
        self.history.append(self.current_img.copy())
        self.current_img = self.redo_stack.pop()
        self.original_img = self.current_img.copy()
        self._refresh_canvas()
        self._update_status("Redo.")

    # ── transform shortcuts ───────────────────────────────────────
    def _flip_h(self):
        if self.original_img is None:
            return
        self.history.append(self.original_img.copy())
        self.original_img = self.original_img.transpose(Image.FLIP_LEFT_RIGHT)
        self.current_img  = self.original_img.copy()
        self._refresh_canvas()
        self._update_status("Flipped horizontally.")

    def _flip_v(self):
        if self.original_img is None:
            return
        self.history.append(self.original_img.copy())
        self.original_img = self.original_img.transpose(Image.FLIP_TOP_BOTTOM)
        self.current_img  = self.original_img.copy()
        self._refresh_canvas()
        self._update_status("Flipped vertically.")

    # ── crop ──────────────────────────────────────────────────────
    def _toggle_crop(self):
        self._crop_mode = not self._crop_mode
        self._update_status(
            "🟡 Crop mode ON — drag a rectangle on the image."
            if self._crop_mode else "Crop mode OFF.")

    def _discard_crop(self):
        if self._crop_rect:
            self.canvas.delete(self._crop_rect)
            self._crop_rect = None
        self._crop_mode = False
        self._update_status("Crop discarded.")

    def _crop_start_cb(self, event):
        if not self._crop_mode or self.original_img is None:
            return
        self._crop_start = (event.x, event.y)
        if self._crop_rect:
            self.canvas.delete(self._crop_rect)

    def _crop_drag_cb(self, event):
        if not self._crop_mode or not self._crop_start:
            return
        x0, y0 = self._crop_start
        self._crop_rect = self.canvas.create_rectangle(
            x0, y0, event.x, event.y,
            outline=ACCENT2, width=2, dash=(4, 4))
        # re-draw so old one is replaced
        if hasattr(self, "_last_crop_rect"):
            self.canvas.delete(self._last_crop_rect)
        self._last_crop_rect = self._crop_rect

    def _crop_end_cb(self, event):
        if not self._crop_mode or not self._crop_start:
            return
        x0, y0 = self._crop_start
        x1, y1 = event.x, event.y

        # map canvas coords → image coords
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        img = self.original_img
        scale = min(cw / img.width, ch / img.height)
        disp_w = int(img.width  * scale)
        disp_h = int(img.height * scale)
        off_x  = (cw - disp_w) // 2
        off_y  = (ch - disp_h) // 2

        ix0 = max(0, int((min(x0, x1) - off_x) / scale))
        iy0 = max(0, int((min(y0, y1) - off_y) / scale))
        ix1 = min(img.width,  int((max(x0, x1) - off_x) / scale))
        iy1 = min(img.height, int((max(y0, y1) - off_y) / scale))

        if ix1 - ix0 > 10 and iy1 - iy0 > 10:
            self.history.append(self.original_img.copy())
            self.original_img = self.original_img.crop((ix0, iy0, ix1, iy1))
            self.current_img  = self.original_img.copy()
            self._refresh_canvas()
            self._update_status(f"Cropped to {ix1-ix0}×{iy1-iy0} px.")
        else:
            self._update_status("Crop area too small — ignored.")

        self._crop_mode = False
        if self._crop_rect:
            self.canvas.delete(self._crop_rect)

    # ── colour pickers ───────────────────────────────────────────
    def _pick_overlay_colour(self):
        c = colorchooser.askcolor(color=self.overlay_color,
                                   title="Pick Overlay Text Colour")
        if c and c[1]:
            self.overlay_color = c[1]
            self.ov_colour_lbl.configure(bg=c[1])
            self._live_preview()

    def _pick_tint(self):
        c = colorchooser.askcolor(color=self.tint_color,
                                   title="Pick Tint Colour")
        if c and c[1]:
            self.tint_color = c[1]
            self.tint_lbl.configure(bg=c[1])
            self._live_preview()

    # ── forensics features ────────────────────────────────────────
    def _embed_payload(self):
        if self.current_img is None:
            messagebox.showwarning("No Image", "Open an image first.")
            return
        payload = self.payload_var.get()
        if not payload:
            messagebox.showwarning("Empty", "Enter a payload string first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save image with embedded payload",
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if not path:
            return
        buf = io.BytesIO()
        self.current_img.convert("RGB").save(buf, format="JPEG", quality=95)
        img_bytes = buf.getvalue()
        if img_bytes[:2] == b"\xff\xd8":
            out = img_bytes[:-2] + payload.encode() + b"\xff\xd9"
        else:
            out = img_bytes + payload.encode()
        with open(path, "wb") as f:
            f.write(out)
        self._update_status(
            f"Payload ({len(payload)} bytes) embedded → {os.path.basename(path)}")
        messagebox.showinfo("Done",
                            f"Payload embedded and saved to:\n{path}")

    def _run_ela(self):
        """Error Level Analysis — compare JPEG recompression artefacts."""
        if self.original_img is None:
            messagebox.showwarning("No Image", "Open an image first.")
            return
        try:
            orig = self.original_img.convert("RGB")
            buf = io.BytesIO()
            orig.save(buf, format="JPEG", quality=90)
            buf.seek(0)
            recomp = Image.open(buf).convert("RGB")
            from PIL import ImageChops, ImageEnhance
            diff = ImageChops.difference(orig, recomp)
            diff = ImageEnhance.Brightness(diff).enhance(20)
            self._show_extra_window("Error Level Analysis (ELA)", diff)
        except Exception as ex:
            messagebox.showerror("ELA Error", str(ex))

    def _show_histogram(self):
        if self.original_img is None:
            messagebox.showwarning("No Image", "Open an image first.")
            return
        try:
            img = self.original_img.convert("RGB")
            hist_r = img.split()[0].histogram()
            hist_g = img.split()[1].histogram()
            hist_b = img.split()[2].histogram()

            win = tk.Toplevel(self.root)
            win.title("Histogram")
            win.configure(bg=BG)
            win.geometry("600x300")
            cv = tk.Canvas(win, bg="#0d0d1a", width=600, height=280,
                           highlightthickness=0)
            cv.pack(fill="both", expand=True)
            w, h = 600, 280
            mx = max(max(hist_r), max(hist_g), max(hist_b)) or 1
            bw = w / 256
            for i in range(256):
                for vals, col in [(hist_r,"#ff4444"),
                                   (hist_g,"#44ff44"),
                                   (hist_b,"#4488ff")]:
                    bh = int(vals[i] / mx * (h - 20))
                    cv.create_rectangle(
                        i * bw, h - bh, (i + 1) * bw, h,
                        fill=col, outline="", stipple="gray50")
        except Exception as ex:
            messagebox.showerror("Histogram Error", str(ex))

    def _read_metadata(self):
        if self.original_img is None:
            messagebox.showwarning("No Image", "Open an image first.")
            return
        info_dict = getattr(self.original_img, "_getexif", lambda: None)()
        exif_text = ""
        if info_dict:
            from PIL.ExifTags import TAGS
            for tag_id, val in info_dict.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_text += f"{tag}: {val}\n"
        else:
            raw = self.original_img.info
            exif_text = "\n".join(f"{k}: {v}" for k, v in raw.items()) or "No metadata found."

        win = tk.Toplevel(self.root)
        win.title("Image Metadata / EXIF")
        win.configure(bg=BG)
        win.geometry("500x400")
        txt = tk.Text(win, bg=BG2, fg=TEXT, font=FONT_SM,
                      relief="flat", padx=10, pady=10)
        txt.pack(fill="both", expand=True)
        txt.insert("end", exif_text)
        txt.configure(state="disabled")

    def _show_extra_window(self, title, img):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG)
        w, h = min(img.width, 900), min(img.height, 600)
        win.geometry(f"{w}x{h}")
        cv = tk.Canvas(win, bg="#0d0d1a", width=w, height=h,
                       highlightthickness=0)
        cv.pack(fill="both", expand=True)
        photo = ImageTk.PhotoImage(img.resize((w, h), Image.LANCZOS))
        cv.create_image(0, 0, anchor="nw", image=photo)
        cv._photo = photo   # keep reference

    # ── canvas rendering ──────────────────────────────────────────
    def _refresh_canvas(self):
        img = self.current_img if self.current_img else self.original_img
        if img is None:
            return
        self._show_on_canvas(img)

    def _show_on_canvas(self, img):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 2 or ch < 2:
            self.root.after(50, self._refresh_canvas)
            return

        scale = min(cw / img.width, ch / img.height, 1.0)
        disp_w = max(1, int(img.width  * scale))
        disp_h = max(1, int(img.height * scale))
        thumbnail = img.copy().convert("RGB").resize(
            (disp_w, disp_h), Image.LANCZOS)

        self.tk_photo = ImageTk.PhotoImage(thumbnail)
        self.canvas.delete("all")
        x = cw // 2
        y = ch // 2
        self.canvas.create_image(x, y, anchor="center",
                                  image=self.tk_photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_info(img)

    # ── status / info ─────────────────────────────────────────────
    def _update_status(self, msg):
        self.status_var.set(f"  {msg}")

    def _update_info(self, img=None):
        if img is None:
            img = self.current_img or self.original_img
        if img:
            mode = img.mode
            self.info_var.set(
                f"  {img.width} × {img.height} px  │  Mode: {mode}  │"
                f"  Zoom: fit  │  Undo stack: {len(self.history)}")

    # ── entry point ───────────────────────────────────────────────
    def run(self):
        self.root.mainloop()


# ─── standalone ─────────────────────────────────────────────────
if __name__ == "__main__":
    RealTimeImageEditor().run()
