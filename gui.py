import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
from pynput import mouse
from autoclicker import AutoClicker

# ---------- Konstanta UI ----------
PAD_X = 8
PAD_Y = 6
BG_COLOR = "#F2F2F4"
ACCENT = "#3A7EEA"
ACCENT_DARK = "#2F69C2"
BORDER = "#D2D2D6"
TEXT_MUTED = "#555"

class AutoClickerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.minsize(520, 210)
        self.root.resizable(True, False)
        self.root.configure(bg=BG_COLOR)

        # Core
        self.auto_clicker = AutoClicker()
        self.click_mode = tk.StringVar(value="current")
        self.pick_in_progress = False
        self.mouse_listener = None
        self._animating = False
        self._anim_phase = 0
        self._hotkey_id = None

        # Style
        self.style = ttk.Style()
        self._init_style()

        # Build UI
        self._build_layout()

        # Hotkey
        self._register_hotkey()

        # Events
        self.root.bind("<Return>", lambda _e: self.start_clicking())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Configure>", self._on_resize)

        self.root.after(10, self._center_window)

    # ---------- Style ----------
    def _init_style(self):
        try:
            self.style.theme_use("clam")
        except:
            pass
        self.style.configure(".", background=BG_COLOR)
        base = ("Segoe UI", 9)
        self.style.configure("TLabel", font=base, background=BG_COLOR)
        self.style.configure("TRadiobutton", font=base, background=BG_COLOR)
        self.style.configure("TLabelframe", background=BG_COLOR, borderwidth=1, relief="solid")
        self.style.configure("TLabelframe.Label", background=BG_COLOR, font=("Segoe UI", 9, "bold"))
        self.style.configure("TEntry", padding=1)
        # Buttons
        self.style.configure("Primary.TButton", font=base, padding=(12,4),
                             background=ACCENT, foreground="white", borderwidth=0)
        self.style.map("Primary.TButton",
                       background=[("active", ACCENT_DARK), ("disabled", "#9cbef3")],
                       foreground=[("disabled", "#E8E8E8")])
        self.style.configure("Flat.TButton", font=base, padding=(12,4),
                             background="#E1E1E4", foreground="black", borderwidth=0)
        self.style.map("Flat.TButton",
                       background=[("active", "#D2D2D6")])
        self.style.configure("Outline.TButton", font=base, padding=(12,4),
                             background=BG_COLOR, foreground="black",
                             bordercolor=BORDER, relief="solid", borderwidth=1)
        self.style.map("Outline.TButton",
                       background=[("active", "#E6E6E9")])

    # ---------- Build Layout ----------
    def _build_layout(self):
        container = ttk.Frame(self.root, padding=(PAD_X, PAD_Y, PAD_X, PAD_Y))
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)

        # Pengaturan Klik
        self.frm_top = ttk.Labelframe(container, text=" Pengaturan Klik ")
        self.frm_top.grid(row=0, column=0, sticky="ew", pady=(0, PAD_Y))
        for c in range(11):
            self.frm_top.columnconfigure(c, weight=0)
        self.frm_top.columnconfigure(10, weight=1)

        r0y = 6
        self._add_labeled_entry(self.frm_top, "Jam", 0, 0, width=4, default="0", pady=r0y)
        self._add_labeled_entry(self.frm_top, "Menit", 0, 2, width=4, default="0", pady=r0y)
        self._add_labeled_entry(self.frm_top, "Detik", 0, 4, width=4, default="1", pady=r0y)
        self._add_labeled_entry(self.frm_top, "Ms", 0, 6, width=5, default="0", pady=r0y)

        ttk.Separator(self.frm_top, orient="vertical").grid(row=0, column=7, sticky="ns", padx=6, pady=(4,4))

        ttk.Label(self.frm_top, text="Tipe Klik").grid(row=0, column=8, padx=(0,4), sticky="e")
        self.click_type = ttk.Combobox(self.frm_top, values=["left", "right", "double"],
                                       width=10, state="readonly")
        self.click_type.current(0)
        self.click_type.grid(row=0, column=9, sticky="w", padx=(0,4))

        # Target
        self.frm_target = ttk.Labelframe(container, text=" Target ")
        self.frm_target.grid(row=1, column=0, sticky="ew", pady=(0, PAD_Y))
        for c in range(9):
            self.frm_target.columnconfigure(c, weight=0)
        self.frm_target.columnconfigure(8, weight=1)

        ttk.Radiobutton(self.frm_target, text="Kursor Saat Ini", value="current",
                        variable=self.click_mode).grid(row=0, column=0, columnspan=4, sticky="w",
                                                       padx=(PAD_X, 0), pady=(6,2))
        ttk.Radiobutton(self.frm_target, text="Koordinat (Pick)", value="pick",
                        variable=self.click_mode).grid(row=0, column=4, columnspan=4, sticky="w",
                                                       padx=(PAD_X, 0), pady=(6,2))

        ttk.Label(self.frm_target, text="X").grid(row=1, column=0, padx=(PAD_X,2), sticky="e")
        self.x_coord = ttk.Entry(self.frm_target, width=7)
        self.x_coord.grid(row=1, column=1, padx=(0,10), pady=(0,8), sticky="w")
        ttk.Label(self.frm_target, text="Y").grid(row=1, column=2, padx=(0,2), sticky="e")
        self.y_coord = ttk.Entry(self.frm_target, width=7)
        self.y_coord.grid(row=1, column=3, padx=(0,10), pady=(0,8), sticky="w")

        self.pick_button = ttk.Button(self.frm_target, text="Pick (Klik Kiri)",
                                      command=self.begin_pick, style="Flat.TButton")
        self.pick_button.grid(row=1, column=4, padx=(0, PAD_X), pady=(0,8), sticky="w")

        # Tombol Aksi
        self.buttons_row = ttk.Frame(container)
        self.buttons_row.grid(row=2, column=0, sticky="ew", pady=(0, PAD_Y))
        for c in range(5):
            self.buttons_row.columnconfigure(c, weight=1)

        self.start_button = ttk.Button(self.buttons_row, text="Start",
                                       command=self.start_clicking, style="Primary.TButton", width=14)
        self.stop_button = ttk.Button(self.buttons_row, text="Stop (F6)",
                                      command=self.stop_clicking, style="Outline.TButton", width=14)
        self.start_button.grid(row=0, column=1, padx=6, pady=2)
        self.stop_button.grid(row=0, column=3, padx=6, pady=2)

        # Status
        self.status_frame = ttk.Frame(container)
        self.status_frame.grid(row=3, column=0, sticky="ew")
        self.status_frame.columnconfigure(0, weight=1)
        self.info_var = tk.StringVar(value="Atur interval + tipe > pilih target/pick > Start. Stop: F6 / Stop.")
        self.info_label = ttk.Label(self.status_frame, textvariable=self.info_var,
                                    foreground=TEXT_MUTED, anchor="w", wraplength=760)
        self.info_label.grid(row=0, column=0, sticky="ew", padx=(2,2), pady=(0,2))

        # Hover effects
        for btn in (self.start_button, self.stop_button, self.pick_button):
            btn.bind("<Enter>", self._on_btn_hover)
            btn.bind("<Leave>", self._on_btn_leave)

    # Helper to add label+entry
    def _add_labeled_entry(self, parent, text, row, col, width, default="", pady=0):
        ttk.Label(parent, text=text).grid(row=row, column=col, padx=(PAD_X if col == 0 else 0,2),
                                          pady=(pady,0), sticky="e")
        entry = ttk.Entry(parent, width=width)
        entry.insert(0, default)
        entry.grid(row=row, column=col+1, padx=(0,10), pady=(pady,0))
        if text == "Jam": self.hours = entry
        if text == "Menit": self.minutes = entry
        if text == "Detik": self.seconds = entry
        if text == "Ms": self.milliseconds = entry

    # ---------- Hover ----------
    def _on_btn_hover(self, e):
        widget = e.widget
        if "Primary" in widget.winfo_class() or widget.cget("style") == "Primary.TButton":
            widget.configure(style="Primary.TButton")
        elif widget.cget("style") == "Outline.TButton":
            widget.configure(style="Outline.TButton")
        else:
            widget.configure(style="Flat.TButton")

    def _on_btn_leave(self, e):
        # Reset (style map already handles active)
        pass

    # ---------- Responsive ----------
    def _on_resize(self, _e):
        wrap = max(400, self.root.winfo_width() - 60)
        self.info_label.configure(wraplength=wrap)

    # ---------- Window Center ----------
    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - w)//2, (sh - h)//3
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ---------- Pick Koordinat ----------
    def begin_pick(self):
        if self.pick_in_progress:
            return
        self.pick_in_progress = True
        self.info_var.set("Mode Pick: klik kiri di posisi target...")
        self.root.withdraw()
        self.mouse_listener = mouse.Listener(on_click=self._on_global_click)
        self.mouse_listener.start()

    def _on_global_click(self, x, y, button, pressed):
        from pynput.mouse import Button
        if pressed and button == Button.left:
            self.x_coord.delete(0, tk.END); self.y_coord.delete(0, tk.END)
            self.x_coord.insert(0, str(x)); self.y_coord.insert(0, str(y))
            self.click_mode.set("pick")
            self.info_var.set(f"Koordinat: ({x},{y}). Tekan Start. Stop (F6).")
            self.pick_in_progress = False
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            self.root.deiconify()
            self.root.after(60, self.root.lift)

    # ---------- Start / Stop ----------
    def start_clicking(self):
        try:
            h = int(self.hours.get() or 0)
            m = int(self.minutes.get() or 0)
            s = int(self.seconds.get() or 0)
            ms = int(self.milliseconds.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Interval tidak valid.")
            return
        if h == m == s == ms == 0:
            messagebox.showwarning("Peringatan", "Interval tidak boleh 0.")
            return
        button = self.click_type.get()
        if self.click_mode.get() == "current":
            x = y = None
        else:
            try:
                x = int(self.x_coord.get()) if self.x_coord.get() else None
                y = int(self.y_coord.get()) if self.y_coord.get() else None
            except ValueError:
                messagebox.showerror("Error", "Koordinat tidak valid.")
                return

        self.auto_clicker.start(h, m, s, ms, button, x, y)
        self.info_var.set("Berjalan... Stop: F6 / Stop.")
        self.start_button.config(state="disabled")
        self.pick_button.config(state="disabled")
        self._start_status_animation()

    def stop_clicking(self):
        self.auto_clicker.stop()
        self.info_var.set("Dihentikan. Ubah parameter lalu Start lagi.")
        self.start_button.config(state="normal")
        self.pick_button.config(state="normal")
        self._animating = False

    # ---------- Animasi Status ----------
    def _start_status_animation(self):
        if self._animating:
            return
        self._animating = True
        self._anim_phase = 0
        self._animate_status()

    def _animate_status(self):
        if not self._animating or not self.auto_clicker.running:
            self._animating = False
            return
        dots = "." * ((self._anim_phase % 3) + 1)
        self.info_var.set(f"Berjalan{dots} Stop: F6 / Stop.")
        self._anim_phase += 1
        self.root.after(500, self._animate_status)

    # ---------- Hotkey ----------
    def _register_hotkey(self):
        try:
            keyboard.add_hotkey("f6", self.stop_clicking)
        except Exception:
            pass  # Jika gagal (izin OS)

    # ---------- Close ----------
    def _on_close(self):
        self.stop_clicking()
        try:
            keyboard.remove_hotkey("f6")
        except Exception:
            pass
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
        self.root.destroy()
