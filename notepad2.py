import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

DB_NAME = "tasks.db"


class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f8fafc")

        self.selected_task_id = None

        self.setup_db()
        self.build_ui()
        self.load_tasks()

    # ---------- Database ----------
    def setup_db(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT,
                due_date TEXT,
                completed INTEGER
            )
        """)
        self.conn.commit()

    # ---------- UI ----------
    def build_ui(self):
        # Sidebar
        sidebar = tk.Frame(self.root, width=260, bg="#e0e7ff")
        sidebar.pack(side="left", fill="y")

        tk.Label(
            sidebar, text="Tasks",
            font=("Segoe UI", 18, "bold"),
            bg="#e0e7ff", fg="#1e3a8a"
        ).pack(pady=(20, 10), padx=20, anchor="w")

        self.task_list = tk.Listbox(
            sidebar,
            font=("Segoe UI", 11),
            bg="white",
            fg="#1f2937",
            highlightthickness=0,
            selectbackground="#c7d2fe"
        )
        self.task_list.pack(fill="both", expand=True, padx=20, pady=10)
        self.task_list.bind("<<ListboxSelect>>", self.select_task)

        btn_frame = tk.Frame(sidebar, bg="#e0e7ff")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="New", width=10, command=self.clear_form).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", width=10, command=self.delete_task).pack(side="left", padx=5)

        # Main area
        main = tk.Frame(self.root, bg="#f8fafc")
        main.pack(side="right", fill="both", expand=True)

        tk.Label(main, text="Task Title", bg="#f8fafc").pack(anchor="w", padx=30, pady=(30, 5))
        self.title_entry = tk.Entry(main, font=("Segoe UI", 14))
        self.title_entry.pack(fill="x", padx=30)

        tk.Label(main, text="Priority", bg="#f8fafc").pack(anchor="w", padx=30, pady=(15, 5))
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = tk.OptionMenu(main, self.priority_var, "High", "Medium", "Low")
        self.priority_menu.pack(anchor="w", padx=30)

        tk.Label(main, text="Due Date (YYYY-MM-DD)", bg="#f8fafc").pack(anchor="w", padx=30, pady=(15, 5))
        self.date_entry = tk.Entry(main)
        self.date_entry.pack(anchor="w", padx=30)

        self.completed_var = tk.IntVar()
        self.completed_check = tk.Checkbutton(
            main, text="Completed",
            variable=self.completed_var,
            bg="#f8fafc"
        )
        self.completed_check.pack(anchor="w", padx=30, pady=15)

        tk.Button(
            main, text="Save Task",
            width=15, bg="#6366f1", fg="white",
            command=self.save_task
        ).pack(anchor="w", padx=30)

    # ---------- Logic ----------
    def load_tasks(self):
        self.task_list.delete(0, tk.END)
        self.cursor.execute("SELECT id, title, completed FROM tasks ORDER BY completed, id DESC")
        for task_id, title, completed in self.cursor.fetchall():
            prefix = "✔ " if completed else ""
            self.task_list.insert(tk.END, f"{prefix}{title}")

    def clear_form(self):
        self.selected_task_id = None
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.priority_var.set("Medium")
        self.completed_var.set(0)

    def select_task(self, event):
        if not self.task_list.curselection():
            return

        index = self.task_list.curselection()[0]
        self.cursor.execute("SELECT id FROM tasks ORDER BY completed, id DESC")
        task_ids = [row[0] for row in self.cursor.fetchall()]
        self.selected_task_id = task_ids[index]

        self.cursor.execute(
            "SELECT title, priority, due_date, completed FROM tasks WHERE id=?",
            (self.selected_task_id,)
        )
        title, priority, due_date, completed = self.cursor.fetchone()

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)

        self.priority_var.set(priority)
        self.date_entry.delete(0, tk.END)
        if due_date:
            self.date_entry.insert(0, due_date)

        self.completed_var.set(completed)

    def save_task(self):
        title = self.title_entry.get().strip()
        priority = self.priority_var.get()
        due_date = self.date_entry.get().strip()
        completed = self.completed_var.get()

        if not title:
            messagebox.showerror("Error", "Task title is required")
            return

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format")
                return

        if self.selected_task_id:
            self.cursor.execute("""
                UPDATE tasks SET title=?, priority=?, due_date=?, completed=?
                WHERE id=?
            """, (title, priority, due_date, completed, self.selected_task_id))
        else:
            self.cursor.execute("""
                INSERT INTO tasks (title, priority, due_date, completed)
                VALUES (?, ?, ?, ?)
            """, (title, priority, due_date, completed))

        self.conn.commit()
        self.load_tasks()
        self.clear_form()

    def delete_task(self):
        if not self.selected_task_id:
            return

        if messagebox.askyesno("Delete", "Delete this task?"):
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (self.selected_task_id,))
            self.conn.commit()
            self.load_tasks()
            self.clear_form()


# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    TaskManager(root)
    root.mainloop()
