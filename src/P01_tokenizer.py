"""
Tugas Praktikum #1 - Teori Bahasa & Otomata
Teknik Informatika ITS

Program tokenizer/lexical analyzer yang membaca inputan berupa
program komputer dan menghasilkan output berupa token-token
yang dikelompokkan sesuai sifatnya:
  a. Reserve words
  b. Simbol dan tanda baca
  c. Variabel (identifier)
  d. Kalimat matematika (persamaan, fungsi, dsb)
"""

import re
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

# ============================================================
# Definisi token
# ============================================================

# Reserved words untuk beberapa bahasa populer
RESERVED_WORDS = {
    # Python
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
    # C / C++ / Java
    "auto", "bool", "case", "catch", "char", "const", "default", "do",
    "double", "enum", "extern", "float", "goto", "int", "long", "main",
    "namespace", "new", "NULL", "operator", "private", "protected",
    "public", "register", "short", "signed", "sizeof", "static",
    "struct", "switch", "template", "this", "throw", "typedef",
    "union", "unsigned", "using", "virtual", "void", "volatile",
    # JavaScript / TypeScript
    "abstract", "arguments", "boolean", "byte", "const", "debugger",
    "delete", "eval", "export", "extends", "final", "function",
    "implements", "instanceof", "interface", "let", "native", "package",
    "super", "synchronized", "throws", "transient", "typeof", "var",
    "console", "log", "print", "println", "printf", "scanf", "input",
    "output", "read", "write", "string", "list", "dict", "set", "tuple",
    "map", "filter", "reduce", "range", "len",
    # Tambahan umum
    "include", "define", "ifdef", "ifndef", "endif", "pragma",
    "require", "module", "require_once", "echo", "foreach",
    "elseif", "endif", "endfor", "endwhile",
}

# Simbol dan tanda baca
SYMBOLS = {
    '+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', '^', '~',
    '(', ')', '{', '}', '[', ']', ';', ':', ',', '.', '?', '@', '#',
    '\\', "'", '"', '`',
    # Multi-character
    '==', '!=', '<=', '>=', '&&', '||', '++', '--', '+=', '-=',
    '*=', '/=', '%=', '**', '//', '<<', '>>', '->', '=>', '::',
    '...', '??', '?.',
}

MULTI_CHAR_SYMBOLS = sorted(
    [s for s in SYMBOLS if len(s) > 1], key=len, reverse=True
)

# Regex untuk angka (integer & float)
NUMBER_PATTERN = re.compile(
    r'^(\d+\.?\d*([eE][+-]?\d+)?|0[xX][0-9a-fA-F]+|0[bB][01]+|0[oO][0-7]+)'
)

# Regex untuk identifier (variabel)
IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*')


# ============================================================
# Tokenizer
# ============================================================

class Token:
    """Representasi sebuah token."""
    RESERVED   = "Reserve Word"
    SYMBOL     = "Simbol / Tanda Baca"
    VARIABLE   = "Variabel (Identifier)"
    NUMBER     = "Angka (Literal)"
    STRING_LIT = "String Literal"
    MATH_EXPR  = "Kalimat Matematika"
    COMMENT    = "Komentar"
    UNKNOWN    = "Tidak Dikenal"

    def __init__(self, value: str, category: str, line: int, col: int):
        self.value = value
        self.category = category
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.value!r}, {self.category}, L{self.line}:C{self.col})"


def tokenize(source: str) -> list[Token]:
    """
    Melakukan tokenisasi terhadap source code.
    Mengembalikan list of Token.
    """
    tokens: list[Token] = []
    lines = source.split('\n')

    for line_num, line in enumerate(lines, start=1):
        i = 0
        while i < len(line):
            ch = line[i]

            # --- Lewati whitespace ---
            if ch in (' ', '\t', '\r'):
                i += 1
                continue

            # --- Komentar satu baris (// atau #) ---
            if ch == '#' or (ch == '/' and i + 1 < len(line) and line[i + 1] == '/'):
                comment = line[i:]
                tokens.append(Token(comment, Token.COMMENT, line_num, i + 1))
                break  # sisa baris adalah komentar

            # --- String literal ---
            if ch in ('"', "'", '`'):
                quote = ch
                j = i + 1
                escaped = False
                while j < len(line):
                    if escaped:
                        escaped = False
                    elif line[j] == '\\':
                        escaped = True
                    elif line[j] == quote:
                        j += 1
                        break
                    j += 1
                string_val = line[i:j]
                tokens.append(Token(string_val, Token.STRING_LIT, line_num, i + 1))
                i = j
                continue

            # --- Angka ---
            if ch.isdigit() or (ch == '.' and i + 1 < len(line) and line[i + 1].isdigit()):
                m = NUMBER_PATTERN.match(line[i:])
                if m:
                    num = m.group(0)
                    tokens.append(Token(num, Token.NUMBER, line_num, i + 1))
                    i += len(num)
                    continue

            # --- Multi-character symbols ---
            found_multi = False
            for sym in MULTI_CHAR_SYMBOLS:
                if line[i:i + len(sym)] == sym:
                    tokens.append(Token(sym, Token.SYMBOL, line_num, i + 1))
                    i += len(sym)
                    found_multi = True
                    break
            if found_multi:
                continue

            # --- Single-character symbols ---
            if ch in SYMBOLS:
                tokens.append(Token(ch, Token.SYMBOL, line_num, i + 1))
                i += 1
                continue

            # --- Identifier / Reserved word ---
            m = IDENTIFIER_PATTERN.match(line[i:])
            if m:
                word = m.group(0)
                if word in RESERVED_WORDS:
                    cat = Token.RESERVED
                else:
                    cat = Token.VARIABLE
                tokens.append(Token(word, cat, line_num, i + 1))
                i += len(word)
                continue

            # --- Karakter tidak dikenal ---
            tokens.append(Token(ch, Token.UNKNOWN, line_num, i + 1))
            i += 1

    # --- Identifikasi kalimat matematika ---
    tokens = identify_math_expressions(tokens)
    return tokens


def identify_math_expressions(tokens: list[Token]) -> list[Token]:
    """
    Mengidentifikasi rangkaian token yang membentuk kalimat matematika
    (assignment/persamaan, pemanggilan fungsi matematika, dsb).

    Strategi: jika sebuah baris mengandung operator aritmetika/assignment
    yang menghubungkan angka dan/atau variabel, maka rangkaian tersebut
    dikelompokkan sebagai 'Kalimat Matematika'.
    """
    math_operators = {'+', '-', '*', '/', '%', '**', '//', '=', '==',
                      '!=', '<=', '>=', '<', '>', '+=', '-=', '*=', '/=',
                      '%=', '++', '--'}

    # Kelompokkan token per baris
    line_groups: dict[int, list[Token]] = {}
    for t in tokens:
        line_groups.setdefault(t.line, []).append(t)

    result = []
    for line_num in sorted(line_groups.keys()):
        group = line_groups[line_num]

        # Cek apakah baris ini mengandung ekspresi matematika
        has_math_op = any(
            t.category == Token.SYMBOL and t.value in math_operators
            for t in group
        )
        has_operand = any(
            t.category in (Token.NUMBER, Token.VARIABLE)
            for t in group
        )

        if has_math_op and has_operand:
            # Tandai token yang merupakan bagian dari ekspresi matematika
            # (operand dan operator, termasuk tanda kurung)
            math_parts = []
            for t in group:
                if t.category in (Token.NUMBER, Token.VARIABLE):
                    math_parts.append(t)
                elif t.category == Token.SYMBOL and t.value in (
                    math_operators | {'(', ')', '[', ']'}
                ):
                    math_parts.append(t)
                elif t.category == Token.RESERVED:
                    # tetap reserved
                    pass

            if len(math_parts) >= 2:
                # Buat satu token gabungan untuk kalimat matematika
                expr_str = ' '.join(t.value for t in math_parts)
                first = math_parts[0]
                math_token = Token(expr_str, Token.MATH_EXPR, line_num, first.col)
                # Tambahkan token non-math secara normal, lalu math token
                added_math = False
                for t in group:
                    if t in math_parts:
                        if not added_math:
                            result.append(math_token)
                            added_math = True
                    else:
                        result.append(t)
                continue

        result.extend(group)

    return result


# ============================================================
# Contoh program bawaan
# ============================================================

SAMPLE_PROGRAMS = {
    "Python": '''\
# Program menghitung luas lingkaran
import math

def hitung_luas(radius):
    luas = math.pi * radius ** 2
    return luas

r = float(input("Masukkan jari-jari: "))
hasil = hitung_luas(r)
print(f"Luas = {hasil:.2f}")
''',
    "C": '''\
#include <stdio.h>

int main() {
    int a = 10;
    int b = 20;
    int sum = a + b;
    float avg = (a + b) / 2.0;
    printf("Sum = %d\\n", sum);
    printf("Avg = %.2f\\n", avg);
    return 0;
}
''',
    "JavaScript": '''\
// Fungsi menghitung faktorial
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

let result = factorial(5);
console.log("5! = " + result);

const arr = [1, 2, 3, 4, 5];
let total = arr.reduce((a, b) => a + b, 0);
console.log("Total = " + total);
''',
    "Java": '''\
public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        int x = 15;
        int y = 25;
        int result = add(x, y);
        System.out.println("Result = " + result);

        double pi = 3.14159;
        double area = pi * x * x;
        System.out.println("Area = " + area);
    }
}
''',
}


# ============================================================
# GUI Application
# ============================================================

class TokenizerApp:
    # Warna untuk kategori token
    COLORS = {
        Token.RESERVED:   "#e06c75",  # merah muda
        Token.SYMBOL:     "#d19a66",  # oranye
        Token.VARIABLE:   "#61afef",  # biru
        Token.NUMBER:     "#d19a66",  # oranye
        Token.STRING_LIT: "#98c379",  # hijau
        Token.MATH_EXPR:  "#c678dd",  # ungu
        Token.COMMENT:    "#5c6370",  # abu-abu
        Token.UNKNOWN:    "#e5c07b",  # kuning
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tokenizer - Tugas Praktikum #1 Otomata")
        self.root.geometry("1100x750")
        self.root.configure(bg="#282c34")
        self.root.minsize(900, 600)

        self._build_styles()
        self._build_ui()

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

        style.configure("TCombobox", fieldbackground="#3e4451",
                         background="#3e4451", foreground="#abb2bf",
                         font=("Consolas", 10))

    def _build_ui(self):
        # ---- Header ----
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=15, pady=(15, 5))

        ttk.Label(header, text="🔍 Tokenizer / Lexical Analyzer",
                  style="Title.TLabel").pack(side=tk.LEFT)

        # ---- Toolbar ----
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=15, pady=5)

        ttk.Label(toolbar, text="Contoh Program:").pack(side=tk.LEFT, padx=(0, 5))
        self.sample_var = tk.StringVar(value="-- Pilih --")
        combo = ttk.Combobox(toolbar, textvariable=self.sample_var,
                             values=list(SAMPLE_PROGRAMS.keys()),
                             state="readonly", width=15)
        combo.pack(side=tk.LEFT, padx=(0, 10))
        combo.bind("<<ComboboxSelected>>", self._load_sample)

        ttk.Button(toolbar, text="📂 Buka File",
                   command=self._open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="▶  Analisis",
                   command=self._analyze, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑  Bersihkan",
                   command=self._clear).pack(side=tk.LEFT, padx=2)

        # ---- Panedwindow (input | output) ----
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left: source input
        left_frame = ttk.Frame(paned)
        ttk.Label(left_frame, text="📝 Source Code Input").pack(anchor=tk.W)
        self.source_text = scrolledtext.ScrolledText(
            left_frame, wrap=tk.NONE, font=("Consolas", 11),
            bg="#1e2127", fg="#abb2bf", insertbackground="#528bff",
            selectbackground="#3e4451", borderwidth=0, padx=8, pady=8
        )
        self.source_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        paned.add(left_frame, weight=1)

        # Right: results
        right_frame = ttk.Frame(paned)
        ttk.Label(right_frame, text="📊 Hasil Tokenisasi").pack(anchor=tk.W)

        # Notebook untuk tab
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Tab 1: semua token
        tab_all = ttk.Frame(self.notebook)
        self.notebook.add(tab_all, text=" Semua Token ")

        columns = ("no", "token", "kategori", "lokasi")
        self.tree = ttk.Treeview(tab_all, columns=columns, show="headings",
                                 height=20)
        self.tree.heading("no", text="No")
        self.tree.heading("token", text="Token")
        self.tree.heading("kategori", text="Kategori")
        self.tree.heading("lokasi", text="Baris:Kolom")
        self.tree.column("no", width=40, anchor=tk.CENTER)
        self.tree.column("token", width=200)
        self.tree.column("kategori", width=180)
        self.tree.column("lokasi", width=80, anchor=tk.CENTER)

        # Style tags untuk warna
        for cat, color in self.COLORS.items():
            self.tree.tag_configure(cat, foreground=color)

        scroll_tree = ttk.Scrollbar(tab_all, orient=tk.VERTICAL,
                                     command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_tree.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_tree.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 2: ringkasan per kategori
        tab_summary = ttk.Frame(self.notebook)
        self.notebook.add(tab_summary, text=" Ringkasan ")

        self.summary_text = scrolledtext.ScrolledText(
            tab_summary, wrap=tk.WORD, font=("Consolas", 11),
            bg="#1e2127", fg="#abb2bf", borderwidth=0, padx=8, pady=8,
            state=tk.DISABLED
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        paned.add(right_frame, weight=1)

        # ---- Statusbar ----
        self.status_var = tk.StringVar(value="Siap. Masukkan source code atau buka file.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                               font=("Consolas", 9), foreground="#5c6370")
        status_bar.pack(fill=tk.X, padx=15, pady=(0, 10))

    def _load_sample(self, event=None):
        name = self.sample_var.get()
        if name in SAMPLE_PROGRAMS:
            self.source_text.delete("1.0", tk.END)
            self.source_text.insert("1.0", SAMPLE_PROGRAMS[name])
            self.status_var.set(f"Contoh program '{name}' dimuat.")

    def _open_file(self):
        filetypes = [
            ("Source Code", "*.py *.c *.cpp *.java *.js *.ts *.go *.rs *.php *.rb"),
            ("Semua File", "*.*"),
        ]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                self.source_text.delete("1.0", tk.END)
                self.source_text.insert("1.0", content)
                self.status_var.set(f"File '{path}' berhasil dimuat.")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka file:\n{e}")

    def _clear(self):
        self.source_text.delete("1.0", tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.summary_text.configure(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.configure(state=tk.DISABLED)
        self.status_var.set("Dibersihkan. Siap menerima input baru.")

    def _analyze(self):
        source = self.source_text.get("1.0", tk.END).rstrip('\n')
        if not source.strip():
            messagebox.showwarning("Peringatan", "Source code kosong!")
            return

        tokens = tokenize(source)

        # Bersihkan tabel
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Isi tabel
        for idx, t in enumerate(tokens, start=1):
            display_val = t.value.replace('\n', '\\n')
            if len(display_val) > 60:
                display_val = display_val[:57] + "..."
            self.tree.insert("", tk.END, values=(
                idx, display_val, t.category, f"{t.line}:{t.col}"
            ), tags=(t.category,))

        # Buat ringkasan
        categories: dict[str, list[str]] = {}
        for t in tokens:
            categories.setdefault(t.category, []).append(t.value)

        self.summary_text.configure(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)

        self.summary_text.insert(tk.END, f"Total token: {len(tokens)}\n")
        self.summary_text.insert(tk.END, "=" * 50 + "\n\n")

        for cat in [Token.RESERVED, Token.SYMBOL, Token.VARIABLE,
                    Token.NUMBER, Token.STRING_LIT, Token.MATH_EXPR,
                    Token.COMMENT, Token.UNKNOWN]:
            if cat in categories:
                items = categories[cat]
                unique = sorted(set(items))
                self.summary_text.insert(tk.END, f"▸ {cat} ({len(items)} token)\n")
                self.summary_text.insert(tk.END, f"  Unik: {', '.join(unique)}\n\n")

        self.summary_text.configure(state=tk.DISABLED)
        self.status_var.set(f"Analisis selesai — {len(tokens)} token ditemukan.")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenizerApp(root)
    root.mainloop()
