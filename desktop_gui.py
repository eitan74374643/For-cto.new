import json
import re
import threading
import time
import keyword
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import requests


DEFAULT_SERVER_URL = "https://YOUR-NGROK-SUBDOMAIN.ngrok-free.app/generate"


class SnakeCoderDesktop(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Snake Coder AI (Desktop)")
        self.geometry("1000x720")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self._build_ui()

    def _build_ui(self):
        root = ctk.CTkFrame(self)
        root.pack(fill="both", expand=True, padx=12, pady=12)

        top = ctk.CTkFrame(root)
        top.pack(fill="x")

        ctk.CTkLabel(top, text="Colab Server URL:").pack(side="left", padx=(8, 6), pady=8)
        self.url_var = tk.StringVar(value=DEFAULT_SERVER_URL)
        self.url_entry = ctk.CTkEntry(top, textvariable=self.url_var, width=520)
        self.url_entry.pack(side="left", padx=(0, 8), pady=8)

        self.status_var = tk.StringVar(value="Idle")
        self.status_lbl = ctk.CTkLabel(top, textvariable=self.status_var)
        self.status_lbl.pack(side="right", padx=8, pady=8)

        mid = ctk.CTkFrame(root)
        mid.pack(fill="x", pady=(10, 10))

        ctk.CTkLabel(mid, text="Prompt:").pack(anchor="w", padx=8, pady=(8, 2))
        self.prompt_box = ctk.CTkTextbox(mid, height=110)
        self.prompt_box.pack(fill="x", padx=8, pady=(0, 8))
        self.prompt_box.insert(
            "1.0",
            "Generate a complete Python Snake game using pygame. Include scoring, pause, and clean code.",
        )

        actions = ctk.CTkFrame(root)
        actions.pack(fill="x")

        self.generate_btn = ctk.CTkButton(actions, text="Generate", command=self.on_generate)
        self.generate_btn.pack(side="left", padx=8, pady=8)

        self.copy_btn = ctk.CTkButton(actions, text="Copy Code", command=self.copy_code)
        self.copy_btn.pack(side="left", padx=8, pady=8)

        self.clear_btn = ctk.CTkButton(actions, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(side="left", padx=8, pady=8)

        ctk.CTkLabel(root, text="Generated Code:").pack(anchor="w", padx=8)

        out_frame = ctk.CTkFrame(root)
        out_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self.output_text = tk.Text(
            out_frame,
            wrap="none",
            bg="#0b0f14",
            fg="#d7dde8",
            insertbackground="#d7dde8",
            font=("Consolas", 11),
            undo=True,
        )
        self.output_text.pack(side="left", fill="both", expand=True)

        yscroll = tk.Scrollbar(out_frame, orient="vertical", command=self.output_text.yview)
        yscroll.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=yscroll.set)

        xscroll = tk.Scrollbar(root, orient="horizontal", command=self.output_text.xview)
        xscroll.pack(fill="x", padx=8)
        self.output_text.configure(xscrollcommand=xscroll.set)

        self._init_highlight_tags()

    def _init_highlight_tags(self):
        self.output_text.tag_configure("kw", foreground="#7aa2f7")
        self.output_text.tag_configure("str", foreground="#9ece6a")
        self.output_text.tag_configure("cmt", foreground="#565f89")
        self.output_text.tag_configure("num", foreground="#ff9e64")
        self.output_text.tag_configure("defcls", foreground="#bb9af7")

    def set_status(self, s: str):
        self.status_var.set(s)
        self.update_idletasks()

    def clear_output(self):
        self.output_text.delete("1.0", "end")

    def copy_code(self):
        code = self.output_text.get("1.0", "end-1c")
        if not code.strip():
            return
        self.clipboard_clear()
        self.clipboard_append(code)
        self.set_status("Copied to clipboard")

    def on_generate(self):
        prompt = self.prompt_box.get("1.0", "end-1c").strip()
        url = self.url_var.get().strip()

        if not url:
            messagebox.showerror("Missing URL", "Please set the Colab server URL.")
            return
        if not prompt:
            messagebox.showerror("Missing Prompt", "Please enter a prompt.")
            return

        self.generate_btn.configure(state="disabled")
        self.set_status("Generating...")

        def worker():
            t0 = time.time()
            try:
                resp = requests.post(
                    url,
                    json={"prompt": prompt, "max_new_tokens": 700},
                    timeout=180,
                )
                resp.raise_for_status()
                data = resp.json()
                code = data.get("code", "")
                if not isinstance(code, str):
                    code = json.dumps(code, indent=2)

                elapsed = time.time() - t0

                def ui_update():
                    self.output_text.delete("1.0", "end")
                    self.output_text.insert("1.0", code)
                    self._highlight_python()
                    self.set_status(f"Done ({elapsed:.1f}s)")

                self.after(0, ui_update)

            except Exception as e:
                def ui_err():
                    self.set_status("Error")
                    messagebox.showerror("Generation Failed", str(e))

                self.after(0, ui_err)
            finally:
                self.after(0, lambda: self.generate_btn.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def _highlight_python(self):
        txt = self.output_text.get("1.0", "end-1c")

        for tag in ("kw", "str", "cmt", "num", "defcls"):
            self.output_text.tag_remove(tag, "1.0", "end")

        for m in re.finditer(r"#.*", txt):
            self._tag_span("cmt", m.start(), m.end())

        str_pat = r"(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\'|\"[^\"\\\n]*(?:\\.[^\"\\\n]*)*\"|\'[^\'\\\n]*(?:\\.[^\'\\\n]*)*\')"
        for m in re.finditer(str_pat, txt):
            self._tag_span("str", m.start(), m.end())

        for m in re.finditer(r"\b\d+(\.\d+)?\b", txt):
            self._tag_span("num", m.start(), m.end())

        for m in re.finditer(r"\b(def|class)\s+([A-Za-z_]\w*)", txt):
            self._tag_span("defcls", m.start(2), m.end(2))

        kw_set = set(keyword.kwlist)
        for m in re.finditer(r"\b[A-Za-z_]\w*\b", txt):
            w = m.group(0)
            if w in kw_set:
                self._tag_span("kw", m.start(), m.end())

    def _tag_span(self, tag: str, start_idx: int, end_idx: int):
        start = self._index_from_offset(start_idx)
        end = self._index_from_offset(end_idx)
        self.output_text.tag_add(tag, start, end)

    def _index_from_offset(self, offset: int) -> str:
        return f"1.0+{offset}c"


if __name__ == "__main__":
    app = SnakeCoderDesktop()
    app.mainloop()
