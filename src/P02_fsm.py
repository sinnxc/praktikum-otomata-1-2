"""
Tugas Praktikum #2 - Teori Bahasa & Otomata
Teknik Informatika ITS

Program FSM (Finite State Machine) yang menentukan apakah sebuah string
merupakan anggota dari bahasa:
  L = { x ∈ (0 + 1)* | karakter terakhir x adalah 1 DAN x tidak memiliki
        substring "00" }

State diagram:
  States: S (start), A, B, C (dead/trap)
  Transisi:
    S --0--> A
    S --1--> B
    A --0--> C  (dead state, substring 00 terdeteksi)
    A --1--> B
    B --0--> A
    B --1--> B
    C --0--> C  (trap)
    C --1--> C  (trap)

  Start state : S
  Accept state: B
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# FSM Definition

STATES = {"S", "A", "B", "C"}
ALPHABET = {"0", "1"}
START_STATE = "S"
ACCEPT_STATES = {"B"}

# Tiap state sesuai dengan gambar yang diberikan di PPT
TRANSITIONS = {
    ("S", "0"): "A",
    ("S", "1"): "B",
    ("A", "0"): "C",
    ("A", "1"): "B",
    ("B", "0"): "A",
    ("B", "1"): "B",
    ("C", "0"): "C",
    ("C", "1"): "C",
}

STATE_DESCRIPTIONS = {
    "S": "State awal (Start). Belum menerima input.",
    "A": "Terakhir membaca '0'. Jika membaca '0' lagi → dead state.",
    "B": "Terakhir membaca '1', tidak ada substring '00'. (Accepting)",
    "C": "Dead state. Substring '00' telah terdeteksi. String ditolak.",
}


def run_fsm(input_string: str) -> tuple[bool, list[dict]]:
    """
    Menjalankan FSM pada input_string.
    Mengembalikan (accepted, trace) di mana trace adalah list of dict
    berisi riwayat langkah-langkah transisi.
    """
    current = START_STATE
    trace = [{"step": 0, "char": "-", "from": "-", "to": current,
              "desc": "State awal"}]

    for i, ch in enumerate(input_string):
        if ch not in ALPHABET:
            trace.append({
                "step": i + 1, "char": ch, "from": current,
                "to": "ERROR", "desc": f"Karakter '{ch}' tidak valid (bukan 0/1)"
            })
            return False, trace

        prev = current
        current = TRANSITIONS.get((current, ch), "ERROR")
        desc = STATE_DESCRIPTIONS.get(current, "")
        trace.append({
            "step": i + 1, "char": ch, "from": prev,
            "to": current, "desc": desc
        })

    accepted = current in ACCEPT_STATES
    return accepted, trace


# GUI Application - menggunkana TKInter

class FSMApp:
    # Warna state
    STATE_COLORS = {
        "S": "#61afef",  # biru
        "A": "#e5c07b",  # kuning
        "B": "#98c379",  # hijau (accept)
        "C": "#e06c75",  # merah (dead)
        "ERROR": "#e06c75",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FSM Simulator - Tugas Praktikum #2 Otomata")
        self.root.geometry("1000x750")
        self.root.configure(bg="#282c34")
        self.root.minsize(800, 600)

        self._build_styles()
        self._build_ui()

        # Animasi state
        self.animation_running = False
        self.current_anim_step = 0
        self.anim_trace = []

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#282c34")
        style.configure("TLabel", background="#282c34", foreground="#abb2bf",
                         font=("Consolas", 11))
        style.configure("Title.TLabel", background="#282c34", foreground="#61afef",
                         font=("Consolas", 16, "bold"))
        style.configure("TButton", background="#3e4451", foreground="#abb2bf",
                         font=("Consolas", 10, "bold"), padding=6)
        style.map("TButton",
                  background=[("active", "#528bff")],
                  foreground=[("active", "#ffffff")])
        style.configure("Accent.TButton", background="#528bff", foreground="#ffffff")
        style.map("Accent.TButton",
                  background=[("active", "#61afef")])
        style.configure("Accept.TLabel", background="#2d3a2d", foreground="#98c379",
                         font=("Consolas", 14, "bold"), padding=10)
        style.configure("Reject.TLabel", background="#3a2d2d", foreground="#e06c75",
                         font=("Consolas", 14, "bold"), padding=10)

    def _build_ui(self):
        # ---- Header ----
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=15, pady=(15, 5))
        ttk.Label(header, text="⚙ FSM Simulator",
                  style="Title.TLabel").pack(side=tk.LEFT)

        # ---- Info bahasa ----
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=15, pady=5)
        info_text = (
            "L = { x ∈ (0+1)* | karakter terakhir x = 1  ∧  x tidak memiliki "
            "substring \"00\" }"
        )
        ttk.Label(info_frame, text=info_text,
                  font=("Consolas", 10), foreground="#c678dd").pack(anchor=tk.W)

        # ---- Input ----
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(input_frame, text="Input String (0/1):").pack(side=tk.LEFT)
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame, textvariable=self.input_var,
            font=("Consolas", 14), bg="#1e2127", fg="#abb2bf",
            insertbackground="#528bff", selectbackground="#3e4451",
            borderwidth=2, relief=tk.FLAT, width=30
        )
        self.input_entry.pack(side=tk.LEFT, padx=10, ipady=4)
        self.input_entry.bind("<Return>", lambda e: self._run())

        ttk.Button(input_frame, text="▶  Jalankan",
                   command=self._run, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(input_frame, text="🎬 Animasi",
                   command=self._animate).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_frame, text="🗑 Bersihkan",
                   command=self._clear).pack(side=tk.LEFT, padx=2)

        # ---- Contoh cepat ----
        quick_frame = ttk.Frame(self.root)
        quick_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
        ttk.Label(quick_frame, text="Contoh cepat:",
                  font=("Consolas", 9)).pack(side=tk.LEFT)

        examples = ["1", "01", "101", "10101", "0", "00", "100", "1001", "110"]
        for ex in examples:
            btn = tk.Button(
                quick_frame, text=ex, font=("Consolas", 9, "bold"),
                bg="#3e4451", fg="#abb2bf", activebackground="#528bff",
                activeforeground="#fff", borderwidth=0, padx=6, pady=2,
                command=lambda s=ex: self._quick_test(s)
            )
            btn.pack(side=tk.LEFT, padx=2)

        # ---- Canvas untuk diagram state ----
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.X, padx=15, pady=5)
        ttk.Label(canvas_frame, text="📊 Diagram State:").pack(anchor=tk.W)

        self.canvas = tk.Canvas(
            canvas_frame, bg="#1e2127", height=220,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.X, pady=(5, 0))

        # Simpan highlight state untuk redraw saat resize
        self._highlight_state = None

        # Gambar setelah layout selesai agar winfo_width() benar
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # ---- Result ----
        self.result_label = ttk.Label(self.root, text="", font=("Consolas", 13, "bold"))
        self.result_label.pack(fill=tk.X, padx=15, pady=5)

        # ---- Trace table ----
        trace_frame = ttk.Frame(self.root)
        trace_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        ttk.Label(trace_frame, text="📋 Trace Langkah:").pack(anchor=tk.W)

        columns = ("step", "char", "from_state", "to_state", "desc")
        self.trace_tree = ttk.Treeview(trace_frame, columns=columns,
                                        show="headings", height=8)
        self.trace_tree.heading("step", text="Langkah")
        self.trace_tree.heading("char", text="Input")
        self.trace_tree.heading("from_state", text="Dari State")
        self.trace_tree.heading("to_state", text="Ke State")
        self.trace_tree.heading("desc", text="Keterangan")
        self.trace_tree.column("step", width=60, anchor=tk.CENTER)
        self.trace_tree.column("char", width=60, anchor=tk.CENTER)
        self.trace_tree.column("from_state", width=80, anchor=tk.CENTER)
        self.trace_tree.column("to_state", width=80, anchor=tk.CENTER)
        self.trace_tree.column("desc", width=400)

        # Warna tag
        for state, color in self.STATE_COLORS.items():
            self.trace_tree.tag_configure(state, foreground=color)

        scroll = ttk.Scrollbar(trace_frame, orient=tk.VERTICAL,
                                command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=scroll.set)
        self.trace_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 0))
        scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(5, 0))

    # ---- State diagram drawing ----

    def _on_canvas_resize(self, event=None):
        """Redraw diagram saat canvas di-resize."""
        self._draw_state_diagram(highlight_state=self._highlight_state)

    def _draw_state_diagram(self, highlight_state=None):
        import math

        self._highlight_state = highlight_state
        self.canvas.delete("all")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        r = 30  # radius lingkaran state

        # Posisi state — sesuai layout soal:
        #   S di kiri, A di tengah-atas, B di tengah-bawah, C di kanan-atas
        positions = {
            "S": (w * 0.18, h * 0.50),
            "A": (w * 0.45, h * 0.28),
            "B": (w * 0.45, h * 0.72),
            "C": (w * 0.72, h * 0.28),
        }

        arrow_color = "#5c6370"
        label_color = "#e5c07b"
        label_font = ("Consolas", 10, "bold")

        # Helper: titik pada lingkaran di sudut tertentu (derajat)
        def point_on_circle(cx, cy, radius, angle_deg):
            a = math.radians(angle_deg)
            return cx + radius * math.cos(a), cy - radius * math.sin(a)

        # Helper: gambar panah lurus antar 2 state
        def draw_straight_arrow(from_s, to_s, label, label_offset=(0, 0)):
            x1, y1 = positions[from_s]
            x2, y2 = positions[to_s]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0:
                return
            nx, ny = dx / dist, dy / dist
            sx, sy = x1 + nx * r, y1 + ny * r
            ex, ey = x2 - nx * r, y2 - ny * r
            self.canvas.create_line(sx, sy, ex, ey,
                                     fill=arrow_color, width=2,
                                     arrow=tk.LAST, arrowshape=(10, 12, 5))
            mx = (sx + ex) / 2 + label_offset[0]
            my = (sy + ey) / 2 + label_offset[1]
            self.canvas.create_text(mx, my, text=label,
                                     fill=label_color, font=label_font)

        # Helper: gambar panah melengkung antar 2 state
        def draw_curved_arrow(from_s, to_s, label, curve_amount,
                              label_offset=(0, 0)):
            x1, y1 = positions[from_s]
            x2, y2 = positions[to_s]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist == 0:
                return
            nx, ny = dx / dist, dy / dist

            # Perpendicular direction
            px, py = -ny, nx

            # Start & end pada lingkaran, sedikit digeser ke arah curve
            angle_start = math.atan2(-(dy + px * curve_amount * 0.5),
                                      (dx + py * curve_amount * 0.5))
            angle_end = math.atan2(-(-dy + px * curve_amount * 0.5),
                                    (-dx + py * curve_amount * 0.5))

            sx = x1 + r * math.cos(angle_start)
            sy = y1 - r * math.sin(angle_start)
            ex = x2 + r * math.cos(angle_end)
            ey = y2 - r * math.sin(angle_end)

            # Control point
            cx = (sx + ex) / 2 + px * curve_amount
            cy = (sy + ey) / 2 + py * curve_amount

            # Gambar kurva via beberapa titik (smooth spline)
            points = []
            steps = 20
            for i in range(steps + 1):
                t = i / steps
                # Quadratic bezier: B(t) = (1-t)²·P0 + 2(1-t)t·P1 + t²·P2
                bx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t ** 2 * ex
                by = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t ** 2 * ey
                points.extend([bx, by])

            self.canvas.create_line(*points, fill=arrow_color, width=2,
                                     smooth=False, arrow=tk.LAST,
                                     arrowshape=(10, 12, 5))

            # Label di dekat control point
            lx = (sx + 2 * cx + ex) / 4 + label_offset[0]
            ly = (sy + 2 * cy + ey) / 4 + label_offset[1]
            self.canvas.create_text(lx, ly, text=label,
                                     fill=label_color, font=label_font)

        # Helper: gambar self-loop
        def draw_self_loop(state, label, direction="top"):
            x, y = positions[state]
            # direction menentukan ke mana loop keluar
            if direction == "top":
                # Loop keluar ke atas
                start_angle = 60   # titik keluar kanan-atas
                end_angle = 120    # titik masuk kiri-atas
                loop_height = -55
                label_dy = -50
            elif direction == "bottom":
                start_angle = -60
                end_angle = -120
                loop_height = 55
                label_dy = 50
            elif direction == "right":
                start_angle = 30
                end_angle = -30
                loop_height = 0
                label_dy = 0
            else:
                start_angle = 150
                end_angle = -150
                loop_height = 0
                label_dy = 0

            p1x, p1y = point_on_circle(x, y, r, start_angle)
            p2x, p2y = point_on_circle(x, y, r, end_angle)

            if direction in ("top", "bottom"):
                c1x = p1x + 25
                c1y = y + loop_height
                c2x = p2x - 25
                c2y = y + loop_height
            else:
                dx_off = 55 if direction == "right" else -55
                c1x = x + dx_off
                c1y = p1y - 25
                c2x = x + dx_off
                c2y = p2y + 25

            # Cubic bezier
            points = []
            steps = 24
            for i in range(steps + 1):
                t = i / steps
                bx = ((1 - t) ** 3 * p1x + 3 * (1 - t) ** 2 * t * c1x +
                      3 * (1 - t) * t ** 2 * c2x + t ** 3 * p2x)
                by = ((1 - t) ** 3 * p1y + 3 * (1 - t) ** 2 * t * c1y +
                      3 * (1 - t) * t ** 2 * c2y + t ** 3 * p2y)
                points.extend([bx, by])

            self.canvas.create_line(*points, fill=arrow_color, width=2,
                                     smooth=False, arrow=tk.LAST,
                                     arrowshape=(10, 12, 5))

            # Label
            self.canvas.create_text(x, y + label_dy, text=label,
                                     fill=label_color, font=label_font)

        # Gambar semua transisi (di belakang state circles)

        # S --0--> A  (lurus)
        draw_straight_arrow("S", "A", "0", label_offset=(0, -12))

        # S --1--> B  (lurus)
        draw_straight_arrow("S", "B", "1", label_offset=(0, 12))

        # A --0--> C  (lurus)
        draw_straight_arrow("A", "C", "0", label_offset=(0, -12))

        # A --1--> B  (melengkung ke kanan agar tidak nabrak B->A)
        draw_curved_arrow("A", "B", "1", curve_amount=30, label_offset=(12, 0))

        # B --0--> A  (melengkung ke kiri)
        draw_curved_arrow("B", "A", "0", curve_amount=30, label_offset=(-12, 0))

        # B --1--> B  (self-loop bawah)
        draw_self_loop("B", "1", direction="bottom")

        # C --0,1--> C  (self-loop atas)
        draw_self_loop("C", "0, 1", direction="top")

        # Gambar state circles (di depan panah)
        for state, (x, y) in positions.items():
            fill = "#3e4451"
            outline = self.STATE_COLORS.get(state, "#abb2bf")
            lw = 2

            if highlight_state and state == highlight_state:
                fill = outline
                outline = "#ffffff"
                lw = 3

            # Lingkaran utama
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=fill, outline=outline, width=lw
            )

            # Double circle untuk accept state
            if state in ACCEPT_STATES:
                inner = r - 5
                self.canvas.create_oval(
                    x - inner, y - inner, x + inner, y + inner,
                    outline=outline, width=1
                )

            # Label state
            text_color = ("#ffffff" if (highlight_state and state == highlight_state)
                          else outline)
            self.canvas.create_text(x, y, text=state, fill=text_color,
                                     font=("Consolas", 14, "bold"))

        # Panah start --> S
        sx, sy = positions["S"]
        self.canvas.create_line(sx - r - 45, sy, sx - r - 2, sy,
                                 fill="#528bff", width=2, arrow=tk.LAST,
                                 arrowshape=(10, 12, 5))
        self.canvas.create_text(sx - r - 48, sy, text="start",
                                 fill="#528bff", font=("Consolas", 9),
                                 anchor=tk.E)

    def _quick_test(self, s: str):
        self.input_var.set(s)
        self._run()

    def _run(self):
        self.animation_running = False
        input_str = self.input_var.get().strip()

        if not input_str:
            messagebox.showwarning("Peringatan", "Masukkan string terlebih dahulu!")
            return

        accepted, trace = run_fsm(input_str)

        # Tampilkan hasil
        if accepted:
            self.result_label.configure(
                text=f"✅ DITERIMA — String \"{input_str}\" ∈ L",
                style="Accept.TLabel"
            )
        else:
            # Tentukan alasan penolakan
            last_state = trace[-1]["to"] if trace else "?"
            reason = ""
            if last_state == "C":
                reason = " (mengandung substring '00')"
            elif last_state == "S":
                reason = " (string kosong)"
            elif last_state == "A":
                reason = " (berakhir dengan '0')"
            elif last_state == "ERROR":
                reason = " (karakter tidak valid)"

            self.result_label.configure(
                text=f"❌ DITOLAK — String \"{input_str}\" ∉ L{reason}",
                style="Reject.TLabel"
            )

        # Highlight state terakhir
        final_state = trace[-1]["to"] if trace else START_STATE
        self._draw_state_diagram(highlight_state=final_state)

        # Isi trace table
        self._fill_trace(trace)

    def _fill_trace(self, trace):
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)

        for step in trace:
            self.trace_tree.insert("", tk.END, values=(
                step["step"], step["char"], step["from"],
                step["to"], step["desc"]
            ), tags=(step["to"],))

    def _animate(self):
        input_str = self.input_var.get().strip()
        if not input_str:
            messagebox.showwarning("Peringatan", "Masukkan string terlebih dahulu!")
            return

        accepted, trace = run_fsm(input_str)
        self.anim_trace = trace
        self.current_anim_step = 0
        self.animation_running = True

        # Reset
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)
        self.result_label.configure(text="🎬 Animasi berjalan...",
                                     style="TLabel")
        self._draw_state_diagram()

        # Mulai animasi
        self._animate_step(accepted)

    def _animate_step(self, accepted):
        if not self.animation_running:
            return

        if self.current_anim_step >= len(self.anim_trace):
            # Selesai
            self.animation_running = False
            if accepted:
                self.result_label.configure(
                    text=f"✅ DITERIMA — String \"{self.input_var.get()}\" ∈ L",
                    style="Accept.TLabel"
                )
            else:
                self.result_label.configure(
                    text=f"❌ DITOLAK — String \"{self.input_var.get()}\" ∉ L",
                    style="Reject.TLabel"
                )
            return

        step = self.anim_trace[self.current_anim_step]

        # Highlight current state
        self._draw_state_diagram(highlight_state=step["to"])

        # Tambah ke trace table
        self.trace_tree.insert("", tk.END, values=(
            step["step"], step["char"], step["from"],
            step["to"], step["desc"]
        ), tags=(step["to"],))

        self.current_anim_step += 1
        self.root.after(700, lambda: self._animate_step(accepted))

    def _clear(self):
        self.animation_running = False
        self.input_var.set("")
        self.result_label.configure(text="", style="TLabel")
        for item in self.trace_tree.get_children():
            self.trace_tree.delete(item)
        self._draw_state_diagram()


# Batch testing (test awal untuk memverifikasi keabsahan FSM)

def batch_test():
    """Menjalankan batch test untuk memverifikasi FSM."""
    test_cases = [
        ("1", True),       # berakhir 1, tidak ada 00
        ("01", True),      # berakhir 1, tidak ada 00
        ("101", True),     # berakhir 1, tidak ada 00
        ("10101", True),   # berakhir 1, tidak ada 00
        ("0101", True),    # berakhir 1, tidak ada 00
        ("1011", True),    # berakhir 1, tidak ada 00
        ("0", False),      # berakhir 0
        ("10", False),     # berakhir 0
        ("00", False),     # ada 00
        ("100", False),    # ada 00
        ("001", False),    # ada 00
        ("1001", False),   # ada 00
        ("110", False),    # berakhir 0
        ("1100", False),   # ada 00, berakhir 0
    ]

    print("=" * 60)
    print("BATCH TEST FSM")
    print(f"L = {{ x ∈ (0+1)* | last(x)=1 ∧ x tidak mengandung '00' }}")
    print("=" * 60)

    passed = 0
    for input_str, expected in test_cases:
        accepted, _ = run_fsm(input_str)
        status = "✅" if accepted == expected else "❌"
        if accepted == expected:
            passed += 1
        print(f"  {status} \"{input_str}\" → {'Diterima' if accepted else 'Ditolak'}"
              f"  (expected: {'Diterima' if expected else 'Ditolak'})")

    print(f"\nHasil: {passed}/{len(test_cases)} test PASSED")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        batch_test()
    else:
        root = tk.Tk()
        app = FSMApp(root)
        root.mainloop()
