import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
from pynput import mouse
from autoclicker import AutoClicker
import pyautogui  # tetap diperlukan (pick & future use)

BG = "#F5F5F7"
BORDER = "#D9D9DD"
ACCENT = "#3A7EEA"
ACCENT_DARK = "#2F69C2"
TEXT_MUTED = "#555"
PAD = 8

class AutoClickerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FAD - Auto Clicker Pro")
        self.root.configure(bg=BG)
        self.root.minsize(560, 270)

        self.auto = AutoClicker()

        # State
        self.hotkey = "f6"              # string kombinasi: contoh "ctrl+alt+x"
        self._hotkey_handle = None
        self.click_mode = tk.StringVar(value="current")
        self.repeat_mode = tk.StringVar(value="until")
        self.mouse_button = tk.StringVar(value="left")
        self.click_type = tk.StringVar(value="single")
        self.pick_in_progress = False
        self.mouse_listener = None
        self._animating = False
        self._anim_phase = 0

        self._init_style()
        self._build_ui()
        self._bind_hotkey()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(40, self._center)

    # ---------- Style ----------
    def _init_style(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except:
            pass
        base = ("Segoe UI", 9)
        s.configure(".", background=BG)
        s.configure("TLabel", font=base, background=BG)
        s.configure("Section.TLabelframe", background=BG, borderwidth=1, relief="solid")
        s.configure("Section.TLabelframe.Label", background=BG, font=("Segoe UI", 9, "bold"))
        s.configure("TEntry", padding=1)
        s.configure("Primary.TButton", font=base, padding=(10,4), background=ACCENT,
                    foreground="white", borderwidth=0)
        s.map("Primary.TButton",
              background=[("active", ACCENT_DARK), ("disabled", "#9cbef3")],
              foreground=[("disabled", "#E0E0E0")])
        s.configure("Outline.TButton", font=base, padding=(10,4), background="#ECECEF",
                    foreground="black", bordercolor=BORDER, relief="solid", borderwidth=1)
        s.map("Outline.TButton",
              background=[("active", "#E0E0E4"), ("disabled", "#F1F1F3")],
              foreground=[("disabled", "#999")])
        s.configure("Flat.TButton", font=base, padding=(8,4), background="#E9E9ED",
                    foreground="black", borderwidth=0)
        s.map("Flat.TButton", background=[("active", "#DCDCE0")])
        self.style = s

    # ---------- UI ----------
    def _build_ui(self):
        wrap = ttk.Frame(self.root, padding=PAD)
        wrap.pack(fill="both", expand=True)
        wrap.columnconfigure(0, weight=1)
        wrap.columnconfigure(1, weight=1)

        # Click interval
        frm_interval = ttk.LabelFrame(wrap, text=" Click interval ", style="Section.TLabelframe")
        frm_interval.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, PAD))
        for i in range(10):
            frm_interval.columnconfigure(i, weight=0)
        frm_interval.columnconfigure(9, weight=1)
        self.hours = self._spin(frm_interval, 0, "hours", 0, 0, from_=0, to=999)
        self.mins = self._spin(frm_interval, 0, "mins", 0, 2, from_=0, to=59)
        self.secs = self._spin(frm_interval, 0, "secs", 0, 4, from_=0, to=59, default=1)
        self.millis = self._spin(frm_interval, 0, "milliseconds", 0, 6, from_=0, to=999, width=6, default=0)

        # Click options
        frm_options = ttk.LabelFrame(wrap, text=" Click options ", style="Section.TLabelframe", padding=(PAD, PAD, PAD, PAD))
        frm_options.grid(row=1, column=0, sticky="ew", padx=(0, PAD), pady=(0, PAD))
        frm_options.columnconfigure(1, weight=1)
        ttk.Label(frm_options, text="Mouse button:").grid(row=0, column=0, sticky="w", pady=(0,4))
        ttk.Combobox(frm_options, values=["left","right","middle"], width=10,
                     state="readonly", textvariable=self.mouse_button).grid(row=0, column=1, sticky="w", pady=(0,4))
        ttk.Label(frm_options, text="Click type:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(frm_options, values=["single","double"], width=10,
                     state="readonly", textvariable=self.click_type).grid(row=1, column=1, sticky="w")

        # Click repeat
        frm_repeat = ttk.LabelFrame(wrap, text=" Click repeat ", style="Section.TLabelframe", padding=(PAD, PAD, PAD, PAD))
        frm_repeat.grid(row=1, column=1, sticky="ew", pady=(0, PAD))
        frm_repeat.columnconfigure(2, weight=1)
        self.repeat_times_var = tk.IntVar(value=1)
        ttk.Radiobutton(frm_repeat, text="Repeat", value="count", variable=self.repeat_mode,
                        command=self._update_repeat_state).grid(row=0, column=0, sticky="w")
        self.repeat_spin = ttk.Spinbox(frm_repeat, from_=1, to=100000, width=6,
                                       textvariable=self.repeat_times_var, state="disabled")
        self.repeat_spin.grid(row=0, column=1, padx=(4,4))
        ttk.Label(frm_repeat, text="times").grid(row=0, column=2, sticky="w")
        ttk.Radiobutton(frm_repeat, text="Repeat until stopped", value="until",
                        variable=self.repeat_mode, command=self._update_repeat_state).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4,0))

        # Cursor position
        frm_cursor = ttk.LabelFrame(wrap, text=" Cursor position ", style="Section.TLabelframe", padding=(PAD, PAD, PAD, PAD))
        frm_cursor.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, PAD))
        for i in range(10):
            frm_cursor.columnconfigure(i, weight=0)
        frm_cursor.columnconfigure(9, weight=1)
        ttk.Radiobutton(frm_cursor, text="Current location", value="current",
                        variable=self.click_mode).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Radiobutton(frm_cursor, text="", value="fixed",
                        variable=self.click_mode).grid(row=0, column=3, sticky="w")
        self.pick_btn = ttk.Button(frm_cursor, text="Pick location", style="Flat.TButton",
                                   command=self.begin_pick)
        self.pick_btn.grid(row=0, column=4, padx=(4,12))
        ttk.Label(frm_cursor, text="X").grid(row=0, column=5, sticky="e")
        self.x_entry = ttk.Entry(frm_cursor, width=7)
        self.x_entry.insert(0,"0")
        self.x_entry.grid(row=0, column=6, padx=(2,8))
        ttk.Label(frm_cursor, text="Y").grid(row=0, column=7, sticky="e")
        self.y_entry = ttk.Entry(frm_cursor, width=7)
        self.y_entry.insert(0,"0")
        self.y_entry.grid(row=0, column=8, padx=(2,4))

        # Buttons row (Hotkey left, spacer, Start/Stop right)
        btn_row = ttk.Frame(wrap)
        btn_row.grid(row=3, column=0, columnspan=2, sticky="ew")
        btn_row.columnconfigure(0, weight=0)  # hotkey
        btn_row.columnconfigure(1, weight=1)  # spacer
        btn_row.columnconfigure(2, weight=0)  # start
        btn_row.columnconfigure(3, weight=0)  # stop

        self.hotkey_btn = ttk.Button(btn_row, text="Hotkey setting", style="Flat.TButton",
                                     command=self._open_hotkey_dialog)
        self.hotkey_btn.grid(row=0, column=0, padx=(0,4), pady=(0,4), sticky="w")

        self.start_btn = ttk.Button(btn_row, text=f"Start ({self.hotkey.upper()})",
                                    style="Primary.TButton", command=self.toggle_start)
        self.start_btn.grid(row=0, column=2, padx=(4,4), pady=(0,4), sticky="e")

        self.stop_btn = ttk.Button(btn_row, text=f"Stop ({self.hotkey.upper()})",
                                   style="Outline.TButton", command=self.toggle_start, state="disabled")
        self.stop_btn.grid(row=0, column=3, padx=(4,0), pady=(0,4), sticky="e")

        # Status
        self.status_var = tk.StringVar(value=f"Ready. Press Start or hotkey ({self.hotkey.upper()}).")
        self.status_lbl = ttk.Label(wrap, textvariable=self.status_var, foreground=TEXT_MUTED, anchor="w")
        self.status_lbl.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4,0))

    # ---------- Helpers ----------
    def _spin(self, parent, row, label, rpad, col_start, from_, to, width=5, default=0):
        ttk.Label(parent, text=f"{label}").grid(row=row, column=col_start, padx=(12 if col_start==0 else 6,2),
                                                pady=6, sticky="e")
        var = tk.IntVar(value=default)
        sp = ttk.Spinbox(parent, from_=from_, to=to, width=width, textvariable=var)
        sp.grid(row=row, column=col_start+1, padx=(0,10))

        def _normalize(_e):
            if sp.get().strip() == "":
                sp.delete(0, tk.END)
                sp.insert(0, "0")
        sp.bind("<FocusOut>", _normalize)
        return sp

    def _interval_seconds(self):
        def _val(widget):
            v = widget.get().strip()
            if v == "":
                return 0
            try:
                return int(v)
            except ValueError:
                raise ValueError
        h = _val(self.hours)
        m = _val(self.mins)
        s = _val(self.secs)
        ms = _val(self.millis)
        return h*3600 + m*60 + s + ms/1000.0

    # ---------- Repeat ----------
    def _update_repeat_state(self):
        if self.repeat_mode.get() == "count":
            self.repeat_spin.configure(state="normal")
        else:
            self.repeat_spin.configure(state="disabled")

    # ---------- Hotkey ----------
    def _bind_hotkey(self):
        try:
            if self._hotkey_handle is not None:
                keyboard.remove_hotkey(self._hotkey_handle)
        except:
            pass
        try:
            self._hotkey_handle = keyboard.add_hotkey(self.hotkey, self.toggle_start)
        except:
            self.status_var.set("Cannot register hotkey (permission).")

    def _open_hotkey_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Set Hotkey")
        win.transient(self.root)
        win.resizable(False, False)
        msg = ("Press a key (you may hold Ctrl/Alt/Shift first).\n"
               "Only modifier = belum disimpan.\n"
               "BackSpace = clear, Esc = cancel.")
        ttk.Label(win, text=msg, foreground=TEXT_MUTED, justify="left").pack(padx=14, pady=(12,6))
        current = tk.StringVar(value=f"Current: {self.hotkey.upper()}")
        preview = tk.StringVar(value="New: (waiting)")
        ttk.Label(win, textvariable=current).pack(pady=(0,2))
        ttk.Label(win, textvariable=preview, font=("Segoe UI",9,"bold")).pack(pady=(0,10))
        win.grab_set()

        pressed_mods: set[str] = set()
        MOD_MAP = {
            "control_l":"ctrl","control_r":"ctrl",
            "shift_l":"shift","shift_r":"shift",
            "alt_l":"alt","alt_r":"alt"
        }

        def format_combo(mods, key):
            parts = sorted(mods)
            if key:
                parts.append(key)
            return "+".join(parts)

        def on_key_press(e):
            ks = e.keysym.lower()
            if ks == "escape":
                win.destroy(); return
            if ks == "backspace":
                pressed_mods.clear()
                preview.set("New: (waiting)")
                return
            if ks in MOD_MAP:
                pressed_mods.add(MOD_MAP[ks])
                preview.set("New: " + format_combo(pressed_mods, None))
                return
            # ignore pure Shift, Control, Alt reported generically
            if ks in ("shift","control","alt"):
                return
            combo = format_combo(pressed_mods, ks)
            if combo == "":
                return
            # apply
            self.hotkey = combo
            self._bind_hotkey()
            self.start_btn.configure(text=f"Start ({self.hotkey.upper()})")
            self.stop_btn.configure(text=f"Stop ({self.hotkey.upper()})")
            self.status_var.set(f"Hotkey set to {self.hotkey.upper()}")
            win.destroy()

        win.bind("<KeyPress>", on_key_press)

    # ---------- Pick ----------
    def begin_pick(self):
        if self.pick_in_progress:
            return
        self.pick_in_progress = True
        self.status_var.set("Pick mode: click target...")
        self.root.withdraw()
        self.mouse_listener = mouse.Listener(on_click=self._on_pick_click)
        self.mouse_listener.start()

    def _on_pick_click(self, x, y, button, pressed):
        from pynput.mouse import Button
        if pressed and button == Button.left:
            self.x_entry.delete(0, tk.END); self.y_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(x)); self.y_entry.insert(0,str(y))
            self.click_mode.set("fixed")
            self.status_var.set(f"Picked ({x},{y}).")
            self.pick_in_progress = False
            if self.mouse_listener:
                try: self.mouse_listener.stop()
                except: pass
            self.root.deiconify()
            self.root.after(60, self.root.lift)

    # ---------- Start / Stop ----------
    def toggle_start(self):
        if self.auto.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        try:
            interval = self._interval_seconds()
        except ValueError:
            messagebox.showerror("Error", "Interval contains invalid number.")
            return
        if interval <= 0:
            messagebox.showwarning("Warn", "Interval must be > 0.")
            return
        repeat = None
        if self.repeat_mode.get() == "count":
            try:
                repeat = int(self.repeat_spin.get())
                if repeat <= 0: raise ValueError
            except:
                messagebox.showerror("Error", "Invalid repeat count.")
                return
        if self.click_mode.get() == "fixed":
            try:
                x = int(self.x_entry.get() or 0); y = int(self.y_entry.get() or 0)
            except:
                messagebox.showerror("Error","Invalid coordinates.")
                return
        else:
            x = y = None

        self.auto.start(interval_seconds=interval,
                        mouse_button=self.mouse_button.get(),
                        click_type=self.click_type.get(),
                        repeat=repeat, x=x, y=y)
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.pick_btn.configure(state="disabled")
        self.status_var.set("Running... Press hotkey or Stop.")
        self._start_anim()

    def _stop(self):
        self.auto.stop()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.pick_btn.configure(state="normal")
        self.status_var.set(f"Stopped. Press Start or hotkey ({self.hotkey.upper()}).")
        self._animating = False

    # ---------- Animation ----------
    def _start_anim(self):
        if self._animating: return
        self._animating = True
        self._anim_phase = 0
        self._anim()

    def _anim(self):
        if not self._animating or not self.auto.running:
            self._animating = False
            return
        dots = "." * (self._anim_phase % 4)
        self.status_var.set(f"Running{dots} Hotkey: {self.hotkey.upper()} to stop.")
        self._anim_phase += 1
        self.root.after(400, self._anim)

    # ---------- Center ----------
    def _center(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w)//2
        y = (sh - h)//3
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ---------- Close ----------
    def _on_close(self):
        self._stop()
        try:
            if self._hotkey_handle is not None:
                keyboard.remove_hotkey(self._hotkey_handle)
        except:
            pass
        if self.mouse_listener:
            try: self.mouse_listener.stop()
            except: pass
        self.root.destroy()