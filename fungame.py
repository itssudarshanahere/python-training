"""
🍿 Mood-Based Snack Tracker
Pure Python (tkinter) - No external dependencies required
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
import datetime
from collections import defaultdict

# ─── Data Storage ───────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.expanduser("~"), "mood_snacks.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Mood Config ────────────────────────────────────────────────────────────
MOODS = {
    "😊 Happy":     {"color": "#FFD700", "bg": "#FFF8E1", "suggestions": ["Dark chocolate", "Fresh fruit salad", "Granola bar", "Smoothie bowl", "Gummy bears"]},
    "😢 Sad":       {"color": "#6495ED", "bg": "#EEF4FF", "suggestions": ["Mac & cheese bites", "Warm cookies", "Hot cocoa", "Ice cream", "Comfort crackers"]},
    "😡 Angry":     {"color": "#FF6B6B", "bg": "#FFF0F0", "suggestions": ["Spicy chips", "Crunchy pretzels", "Wasabi peas", "Beef jerky", "Popcorn"]},
    "😰 Anxious":   {"color": "#9B59B6", "bg": "#F8F0FF", "suggestions": ["Chamomile tea + biscuits", "Almonds", "Dark chocolate", "Blueberries", "Oat crackers"]},
    "😴 Tired":     {"color": "#F39C12", "bg": "#FFFBF0", "suggestions": ["Energy balls", "Banana", "Peanut butter toast", "Trail mix", "Espresso brownie"]},
    "🤩 Excited":   {"color": "#2ECC71", "bg": "#F0FFF7", "suggestions": ["Rainbow fruit skewers", "Party mix", "Fizzy sweets", "Popcorn", "Mini cupcake"]},
    "🥱 Bored":     {"color": "#95A5A6", "bg": "#F5F6FA", "suggestions": ["Cheese & crackers", "Mixed nuts", "Veggie sticks + dip", "Chips & salsa", "Mini sandwiches"]},
    "🧘 Calm":      {"color": "#1ABC9C", "bg": "#F0FFFC", "suggestions": ["Green tea + rice cakes", "Apple slices", "Yogurt parfait", "Walnuts", "Cucumber bites"]},
}

# ─── Main App ───────────────────────────────────────────────────────────────
class MoodSnackTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🍿 Mood Snack Tracker")
        self.geometry("900x680")
        self.resizable(True, True)
        self.configure(bg="#1A1A2E")
        self.data = load_data()
        self.selected_mood = tk.StringVar()
        self.snack_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        self._build_ui()
        self._refresh_history()

    # ── UI Construction ──────────────────────────────────────────────────────
    def _build_ui(self):
        # Fonts
        title_font  = font.Font(family="Georgia", size=22, weight="bold")
        label_font  = font.Font(family="Helvetica", size=11)
        small_font  = font.Font(family="Helvetica", size=10)
        mood_font   = font.Font(family="Helvetica", size=11, weight="bold")

        # ── Header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg="#16213E", pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🍿 Mood Snack Tracker", font=title_font,
                 fg="#E2C074", bg="#16213E").pack()
        tk.Label(hdr, text="Track what you eat and how you feel",
                 font=small_font, fg="#7A8BA0", bg="#16213E").pack()

        # ── Main Content ─────────────────────────────────────────────────────
        main = tk.Frame(self, bg="#1A1A2E")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        left = tk.Frame(main, bg="#1A1A2E", width=380)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        right = tk.Frame(main, bg="#1A1A2E")
        right.pack(side="left", fill="both", expand=True)

        # ── Mood Selection ───────────────────────────────────────────────────
        tk.Label(left, text="1. How are you feeling?", font=label_font,
                 fg="#C8D8E8", bg="#1A1A2E").pack(anchor="w", pady=(8, 4))

        mood_grid = tk.Frame(left, bg="#1A1A2E")
        mood_grid.pack(fill="x")

        self.mood_btns = {}
        moods = list(MOODS.keys())
        for i, m in enumerate(moods):
            cfg = MOODS[m]
            btn = tk.Button(
                mood_grid, text=m, font=mood_font,
                bg="#0F3460", fg="#C8D8E8",
                activebackground=cfg["color"], activeforeground="#1A1A2E",
                relief="flat", bd=0, padx=8, pady=6, cursor="hand2",
                command=lambda mood=m: self._select_mood(mood)
            )
            btn.grid(row=i//2, column=i%2, padx=4, pady=4, sticky="ew")
            self.mood_btns[m] = btn
        mood_grid.columnconfigure(0, weight=1)
        mood_grid.columnconfigure(1, weight=1)

        # ── Snack Input ──────────────────────────────────────────────────────
        tk.Label(left, text="2. What did you snack on?", font=label_font,
                 fg="#C8D8E8", bg="#1A1A2E").pack(anchor="w", pady=(14, 4))

        self.snack_frame = tk.Frame(left, bg="#1A1A2E")
        self.snack_frame.pack(fill="x")

        self.suggestion_frame = tk.Frame(left, bg="#1A1A2E")
        self.suggestion_frame.pack(fill="x", pady=(4, 0))

        snack_entry = tk.Entry(self.snack_frame, textvariable=self.snack_var,
                               font=label_font, bg="#0F3460", fg="white",
                               insertbackground="white", relief="flat",
                               bd=6, width=28)
        snack_entry.pack(side="left", fill="x", expand=True)

        # ── Notes ────────────────────────────────────────────────────────────
        tk.Label(left, text="3. Any notes? (optional)", font=label_font,
                 fg="#C8D8E8", bg="#1A1A2E").pack(anchor="w", pady=(12, 4))

        notes_entry = tk.Entry(left, textvariable=self.notes_var,
                               font=small_font, bg="#0F3460", fg="#AAB8C2",
                               insertbackground="white", relief="flat", bd=6)
        notes_entry.pack(fill="x")

        # ── Log Button ───────────────────────────────────────────────────────
        log_btn = tk.Button(
            left, text="✚  Log Snack", font=font.Font(family="Helvetica", size=12, weight="bold"),
            bg="#E2C074", fg="#1A1A2E", relief="flat", bd=0,
            padx=12, pady=10, cursor="hand2", command=self._log_snack
        )
        log_btn.pack(fill="x", pady=(16, 4))

        # ── Stats ────────────────────────────────────────────────────────────
        self.stats_label = tk.Label(left, text="", font=small_font,
                                    fg="#7A8BA0", bg="#1A1A2E", justify="left")
        self.stats_label.pack(anchor="w", pady=(8, 0))

        # ── History (right panel) ────────────────────────────────────────────
        tk.Label(right, text="📋 Snack Log", font=label_font,
                 fg="#E2C074", bg="#1A1A2E").pack(anchor="w", pady=(8, 6))

        # Filter bar
        filter_frame = tk.Frame(right, bg="#1A1A2E")
        filter_frame.pack(fill="x", pady=(0, 6))

        tk.Label(filter_frame, text="Filter by mood:", font=small_font,
                 fg="#7A8BA0", bg="#1A1A2E").pack(side="left")

        self.filter_var = tk.StringVar(value="All")
        filter_opts = ["All"] + list(MOODS.keys())
        filter_menu = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=filter_opts, state="readonly",
                                   width=22, font=small_font)
        filter_menu.pack(side="left", padx=(6, 0))
        filter_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh_history())

        clear_btn = tk.Button(filter_frame, text="🗑 Clear All", font=small_font,
                              bg="#FF6B6B", fg="white", relief="flat", bd=0,
                              padx=8, pady=3, cursor="hand2",
                              command=self._clear_all)
        clear_btn.pack(side="right")

        # History listbox with scrollbar
        list_frame = tk.Frame(right, bg="#1A1A2E")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg="#0F3460")
        scrollbar.pack(side="right", fill="y")

        self.history_list = tk.Listbox(
            list_frame, font=small_font, bg="#0F3460", fg="#C8D8E8",
            selectbackground="#E2C074", selectforeground="#1A1A2E",
            relief="flat", bd=0, activestyle="none",
            yscrollcommand=scrollbar.set
        )
        self.history_list.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_list.yview)

        # Delete selected
        tk.Button(right, text="✕ Delete Selected Entry", font=small_font,
                  bg="#16213E", fg="#FF6B6B", relief="flat", bd=0,
                  padx=8, pady=4, cursor="hand2",
                  command=self._delete_selected).pack(anchor="e", pady=(4, 0))

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _select_mood(self, mood):
        self.selected_mood.set(mood)
        cfg = MOODS[mood]
        # Update button styles
        for m, btn in self.mood_btns.items():
            if m == mood:
                btn.configure(bg=cfg["color"], fg="#1A1A2E")
            else:
                btn.configure(bg="#0F3460", fg="#C8D8E8")
        # Show suggestions
        for w in self.suggestion_frame.winfo_children():
            w.destroy()
        tk.Label(self.suggestion_frame, text="💡 Suggestions:",
                 font=font.Font(family="Helvetica", size=9, slant="italic"),
                 fg="#7A8BA0", bg="#1A1A2E").pack(anchor="w")
        sug_row = tk.Frame(self.suggestion_frame, bg="#1A1A2E")
        sug_row.pack(fill="x")
        for s in cfg["suggestions"]:
            btn = tk.Button(
                sug_row, text=s,
                font=font.Font(family="Helvetica", size=9),
                bg="#16213E", fg=cfg["color"],
                relief="flat", bd=0, padx=5, pady=2, cursor="hand2",
                command=lambda sn=s: self.snack_var.set(sn)
            )
            btn.pack(side="left", padx=2, pady=2)

    def _log_snack(self):
        mood = self.selected_mood.get()
        snack = self.snack_var.get().strip()
        if not mood:
            messagebox.showwarning("Oops!", "Please select a mood first! 🎭")
            return
        if not snack:
            messagebox.showwarning("Oops!", "Please enter a snack! 🍕")
            return

        entry = {
            "mood": mood,
            "snack": snack,
            "notes": self.notes_var.get().strip(),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.data.append(entry)
        save_data(self.data)
        self.snack_var.set("")
        self.notes_var.set("")
        self._refresh_history()
        self._update_stats()
        # Flash feedback
        self._flash_success(f"Logged: {snack} while {mood.split()[1]}! 🎉")

    def _flash_success(self, msg):
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg="#2ECC71")
        x = self.winfo_x() + self.winfo_width()//2 - 200
        y = self.winfo_y() + self.winfo_height() - 100
        popup.geometry(f"400x50+{x}+{y}")
        tk.Label(popup, text=msg, font=font.Font(family="Helvetica", size=11, weight="bold"),
                 fg="white", bg="#2ECC71").pack(expand=True)
        popup.after(1800, popup.destroy)

    def _refresh_history(self):
        self.history_list.delete(0, tk.END)
        filter_mood = self.filter_var.get()
        filtered = [e for e in reversed(self.data)
                    if filter_mood == "All" or e["mood"] == filter_mood]
        for e in filtered:
            mood_icon = e["mood"].split()[0]
            note_str = f"  · {e['notes']}" if e.get("notes") else ""
            line = f"{mood_icon}  {e['timestamp']}  |  {e['snack']}{note_str}"
            self.history_list.insert(tk.END, line)
        self._update_stats()

    def _update_stats(self):
        if not self.data:
            self.stats_label.config(text="No snacks logged yet.")
            return
        mood_counts = defaultdict(int)
        for e in self.data:
            mood_counts[e["mood"]] += 1
        top_mood = max(mood_counts, key=mood_counts.get)
        self.stats_label.config(
            text=f"Total logged: {len(self.data)}  |  Most common mood: {top_mood.split()[0]} {top_mood.split()[1]}"
        )

    def _delete_selected(self):
        sel = self.history_list.curselection()
        if not sel:
            return
        idx = sel[0]
        filter_mood = self.filter_var.get()
        filtered_indices = [i for i, e in enumerate(self.data)
                            if filter_mood == "All" or e["mood"] == filter_mood]
        # Reversed list, so map back
        real_indices = list(reversed(filtered_indices))
        if idx < len(real_indices):
            del self.data[real_indices[idx]]
            save_data(self.data)
            self._refresh_history()

    def _clear_all(self):
        if messagebox.askyesno("Clear All", "Delete ALL snack entries? This cannot be undone."):
            self.data = []
            save_data(self.data)
            self._refresh_history()

# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MoodSnackTracker()
    app.mainloop()