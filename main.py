import threading
import time
import tkinter as tk
import json
import os

from tkinter import ttk, messagebox, scrolledtext
from reconnect.reconnect import reconnect
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import WebDriverException, TimeoutException
from config.config import CHECK_URL, CHECK_INTERVAL, LOG_INTERVAL
from log.logger import AppLogger

logger = AppLogger()
CONFIG_PATH = os.path.join("config", "config.json")
LOG_FILE = os.path.join("logs", "cosmos.log")

def load_credentials():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"phone": "", "password": ""}

def save_credentials(phone, password):
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"phone": phone, "password": password}, f, ensure_ascii=False, indent=2)

class BrowserChecker:
    def __init__(self):
        self.driver = None
        self.browser_used = None
        for browser in ["firefox", "chrome", "edge"]:
            self.driver = self.get_webdriver(browser)
            if self.driver:
                self.browser_used = browser
                break

    def get_webdriver(self, browser):
        try:
            if browser == "firefox":
                options = FirefoxOptions()
                options.headless = True
                return webdriver.Firefox(options=options)

            elif browser == "chrome":
                options = ChromeOptions()
                options.headless = True
                return webdriver.Chrome(options=options)

            elif browser == "edge":
                options = EdgeOptions()
                options.headless = True
                return webdriver.Edge(options=options)

        except WebDriverException:
            return None

    def is_internet_available(self):
        if not self.driver:
            return False
        try:
            self.driver.set_page_load_timeout(3)
            self.driver.get(CHECK_URL)
            return True
        except (WebDriverException, TimeoutException):
            return False

    def quit(self):
        if self.driver:
            self.driver.quit()

class CosmosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cosmos_Idi_Naxyi")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2f")

        self.running = False
        self.checker = BrowserChecker()
        self.last_log_time = 0

        creds = load_credentials()

        self.title_label = tk.Label(root, text="Cosmos_Idi_Naxyi", font=("Segoe UI", 20, "bold"),
                                    bg="#1e1e2f", fg="#ffffff")
        self.title_label.pack(pady=10)

        frame_inputs = tk.Frame(root, bg="#1e1e2f")
        frame_inputs.pack(pady=10)

        tk.Label(frame_inputs, text="Телефон:", font=("Segoe UI", 12), bg="#1e1e2f", fg="#ffffff").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.phone_entry = ttk.Entry(frame_inputs, width=25)
        self.phone_entry.insert(0, creds.get("phone", ""))
        self.phone_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_inputs, text="Пароль:", font=("Segoe UI", 12), bg="#1e1e2f", fg="#ffffff").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = ttk.Entry(frame_inputs, width=25, show="*")
        self.password_entry.insert(0, creds.get("password", ""))
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.save_button = ttk.Button(frame_inputs, text="💾 Сохранить", command=self.save_credentials)
        self.save_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.status_canvas = tk.Canvas(root, width=20, height=20, bg="#1e1e2f", highlightthickness=0)
        self.status_indicator = self.status_canvas.create_oval(2, 2, 18, 18, fill="gray")
        self.status_canvas.pack(pady=10)

        self.status_label = tk.Label(root, text="Статус: Ожидание", font=("Segoe UI", 12),
                                     bg="#1e1e2f", fg="#ffffff")
        self.status_label.pack(pady=5)

        self.toggle_button = ttk.Button(root, text="Старт", command=self.toggle)
        self.toggle_button.pack(pady=10)

        self.manual_button = ttk.Button(root, text="Переподключение", command=self.manual_reconnect)
        self.manual_button.pack(pady=10)

        self.log_button = ttk.Button(root, text="📜", command=self.show_logs)
        self.log_button.pack(pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), padding=6, background="#5656ff", foreground="#ffffff")
        style.map("TButton", background=[('active', '#4141cc')])

    def save_credentials(self):
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()
        if not phone or not password:
            messagebox.showwarning("Ошибка", "Телефон и пароль не могут быть пустыми")
            return
        save_credentials(phone, password)
        messagebox.showinfo("Успех", "Данные сохранены")

    def toggle(self):
        if self.running:
            self.running = False
            self.toggle_button.config(text="Старт")
            self.set_status("Остановлено", "gray")

        else:
            self.running = True
            self.toggle_button.config(text="Стоп")
            threading.Thread(target=self.run, daemon=True).start()

    def manual_reconnect(self):
        def task():
            self.manual_button.config(text="Подключение...", state="disabled")
            self.set_status("Переподключение...", "orange")

            reconnect()

            self.set_status("Интернет восстановлен", "green")
            logger.info("Ручное переподключение выполнено")
            self.manual_button.config(text="Переподключение", state="normal")
        threading.Thread(target=task, daemon=True).start()

    def set_status(self, text, color):
        self.status_label.config(text=f"Статус: {text}")
        self.status_canvas.itemconfig(self.status_indicator, fill=color)

    def run(self):
        while self.running:
            if not self.checker.is_internet_available():
                self.set_status("Нет интернета! Переподключаем...", "red")
                reconnect()
                self.set_status("Интернет восстановлен", "green")
                logger.warning("Интернет пропал. Выполнено переподключение")

            else:
                self.set_status("Интернет работает", "green")

            if time.time() - self.last_log_time >= LOG_INTERVAL:
                logger.info("Проверка: интернет работает")
                self.last_log_time = time.time()
            time.sleep(CHECK_INTERVAL)

    def show_logs(self):
        if not os.path.exists(LOG_FILE):
            messagebox.showinfo("Логи", "Лог-файл пока пуст")
            return

        log_window = tk.Toplevel(self.root)
        log_window.title("Логи")
        log_window.geometry("600x400")

        text_area = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=("Consolas", 10))
        text_area.pack(expand=True, fill="both")
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.readlines()
        text_area.insert(tk.END, "".join(logs[-200:]))
        text_area.configure(state="disabled")

    def on_close(self):
        self.running = False
        self.checker.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CosmosApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
