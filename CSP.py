import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import csv
import os

class ParityGameGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("🎮 Parity Game")

        # 启动时隐藏主窗口，先弹输入窗口
        self.master.withdraw()

        # 弹出输入窗口让用户输入最大轮数
        self.ask_max_rounds()

    def ask_max_rounds(self):
        self.input_win = tk.Toplevel(self.master)
        self.input_win.title("Set rounds")
        self.input_win.grab_set()

        tk.Label(self.input_win, text="Input max rounds:", font=("Helvetica", 14)).pack(pady=10)
        self.entry = tk.Entry(self.input_win, font=("Helvetica", 14))
        self.entry.pack(pady=5)
        self.entry.focus()

        start_btn = tk.Button(self.input_win, text="Start practice", font=("Helvetica", 14), command=self.start_game)
        start_btn.pack(pady=10)

        self.input_win.bind('<Return>', lambda e: self.start_game())

    def start_game(self):
        val = self.entry.get()
        if not val.isdigit() or int(val) <= 0:
            messagebox.showerror("Input error", "input a positive number!")
            return
        self.total_rounds = int(val)
        self.input_win.destroy()

        self.master.deiconify()
        self.setup_game_ui()
        self.current_round = 0
        self.results = []
        self.next_round()

    def setup_game_ui(self):
        self.progress_label = tk.Label(self.master, text="", font=("Helvetica", 16))
        self.progress_label.pack(pady=5)

        self.timer_label = tk.Label(self.master, text="Time: 0.00 秒", font=("Helvetica", 14))
        self.timer_label.pack(pady=5)

        self.colors = ["blue", "red", "green", "orange"]
        self.fixed_order = self.colors

        self.color_rgb = {
            "blue": "#2196F3",
            "red": "#F44336",
            "green": "#4CAF50",
            "orange": "#FF9800"
        }

        self.canvas = tk.Canvas(self.master, width=400, height=150, bg="white")
        self.canvas.pack(pady=20)

        self.info = tk.Label(self.master, text="← odd / → even / Space End Game", font=("Helvetica", 14))
        self.info.pack(pady=10)

        self.master.bind("<Left>", self.key_odd)
        self.master.bind("<Right>", self.key_even)
        self.master.bind("<space>", self.end_game)

        self.timer_running = False

    def permutation_parity(self, perm):
        idx_perm = [self.fixed_order.index(color) for color in perm]
        count = 0
        for i in range(len(idx_perm)):
            for j in range(i + 1, len(idx_perm)):
                if idx_perm[i] > idx_perm[j]:
                    count += 1
        return "even" if count % 2 == 0 else "odd"

    def draw_color_blocks(self, colors):
        self.canvas.delete("all")
        block_width = 100
        spacing = 20
        start_x = 50
        y1, y2 = 40, 110
        for i, color in enumerate(colors):
            x1 = start_x + i * (block_width + spacing)
            x2 = x1 + block_width
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.color_rgb[color], outline="black", width=2)

    def update_progress(self):
        self.progress_label.config(text=f"current round: {self.current_round} / max round: {self.total_rounds}")

    def update_timer(self):
        if self.timer_running:
            elapsed = time.time() - self.start_time
            self.timer_label.config(text=f"time: {elapsed:.2f} s")
            self.master.after(50, self.update_timer)

    def next_round(self):
        if self.current_round >= self.total_rounds:
            self.end_game()
            return
        self.current_round += 1
        self.update_progress()

        selected = random.sample(self.colors, 3)
        random.shuffle(selected)
        self.current_perm = selected
        self.correct_answer = self.permutation_parity(selected)

        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

        self.draw_color_blocks(selected)
        print(f"[round {self.current_round} ] correct answer: {self.correct_answer} ({selected})")

    def record_result(self, user_input):
        self.timer_running = False
        end_time = time.time()
        time_used = round(end_time - self.start_time, 3)
        is_correct = user_input == self.correct_answer
        self.results.append({
            "round": self.current_round,
            "permutation": ",".join(self.current_perm),
            "user_input": user_input,
            "correct_answer": self.correct_answer,
            "is_correct": is_correct,
            "time_used_sec": time_used
        })
        self.next_round()

    def key_odd(self, event):
        self.record_result("odd")

    def key_even(self, event):
        self.record_result("even")

    def end_game(self, event=None):
        if not self.results:
            self.master.destroy()
            return

        self.timer_running = False
        elapsed = time.time() - self.start_time
        self.timer_label.config(text=f"time: {elapsed:.2f} s (Game over!)")

        save_dir = r"D:\CSP_parity"
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.join(save_dir, "parity_game_gui_results.tsv")

        with open(filename, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys(), delimiter='\t')
            writer.writeheader()
            for row in self.results:
                writer.writerow(row)

        self.canvas.delete("all")
        self.canvas.create_text(200, 75, text="Game over!", font=("Helvetica", 24))
        self.info.config(text=f"📁 result saved as: {filename}")

        self.master.unbind("<Left>")
        self.master.unbind("<Right>")
        self.master.unbind("<space>")

        self.show_results_window()

    def show_results_window(self):
        result_win = tk.Toplevel(self.master)
        result_win.title("Game results")

        columns = list(self.results[0].keys())

        tree = ttk.Treeview(result_win, columns=columns, show='headings')
        tree.pack(expand=True, fill='both')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        for row in self.results:
            values = [row[col] for col in columns]
            tree.insert("", "end", values=values)

        total = len(self.results)
        correct_count = sum(r["is_correct"] for r in self.results)
        avg_time_correct = (sum(r["time_used_sec"] for r in self.results if r["is_correct"]) / correct_count) if correct_count else 0

        stats_text = f"Accuracy: {correct_count}/{total} = {correct_count/total*100:.2f}%    avg(correct): {avg_time_correct:.3f} 秒"
        stats_label = tk.Label(result_win, text=stats_text, font=("Helvetica", 14))
        stats_label.pack(pady=10)

        close_btn = tk.Button(result_win, text="close", command=result_win.destroy)
        close_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParityGameGUI(root)
    root.mainloop()
