import os
import tkinter as tk
from tkinter import scrolledtext
import time
import requests
import shutil
import subprocess

class SelfImprovingAgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nazorat Ostidagi Agent")

        # Agent taklifi
        self.proposal_label = tk.Label(root, text="Agent taklifi:")
        self.proposal_label.pack()

        self.proposal_text = tk.Text(root, height=4, width=60, wrap=tk.WORD)
        self.proposal_text.pack()

        # Tugmalar
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.approve_button = tk.Button(button_frame, text="✅ Ruxsat berish", command=self.approve_action)
        self.approve_button.pack(side=tk.LEFT, padx=5)

        self.deny_button = tk.Button(button_frame, text="❌ Rad etish", command=self.deny_action)
        self.deny_button.pack(side=tk.LEFT, padx=5)

        # Loglar oynasi
        self.log_area = scrolledtext.ScrolledText(root, height=12, width=70)
        self.log_area.pack(pady=10)

        # Tahlil navbati
        self.analysis_steps = [
            self.analyze_temp_files,
            self.check_for_update,
            self.check_network_info,
            self.suggest_backup,
            self.suggest_code_update
        ]
        self.current_step = 0

        self.next_analysis()

    def next_analysis(self):
        if self.current_step >= len(self.analysis_steps):
            self.log("✅ Barcha takliflar tugadi.")
            return
        self.current_proposal, self.current_action = self.analysis_steps[self.current_step]()
        self.current_step += 1
        self.proposal_text.delete("1.0", tk.END)
        self.proposal_text.insert(tk.END, self.current_proposal)

    def analyze_temp_files(self):
        path = os.getcwd()
        files = os.listdir(path)
        target_files = [f for f in files if f.endswith(".tmp") or f.startswith("temp")]
        proposal = f"{len(target_files)} ta '.tmp' yoki 'temp*' fayl topildi. O'chirilsinmi?"
        if len(target_files) > 5:
            return proposal, lambda: self.auto_approve_temp_delete(path, target_files)
        return proposal, lambda: self.delete_files(path, target_files)

    def auto_approve_temp_delete(self, path, file_list):
        self.log("📌 Qoidaga binoan avtomatik ruxsat berildi.")
        self.delete_files(path, file_list)

    def delete_files(self, path, file_list):
        deleted = 0
        for f in file_list:
            try:
                os.remove(os.path.join(path, f))
                deleted += 1
            except Exception as e:
                self.log(f"⚠️ {f} faylini o'chirishda xatolik: {e}")
        self.log(f"🧹 {deleted} ta fayl o'chirildi.")
        self.log_action("DELETE_TEMP_FILES", True)

    def check_for_update(self):
        proposal = "Agent GitHub'dan yangi versiyasini tekshirsinmi?"
        return proposal, self.fetch_update

    def fetch_update(self):
        self.log("🌐 Yangi versiyalar tekshirilmoqda...")
        try:
            response = requests.get("https://example.com")
            self.log(f"🔗 So'rov bajarildi. Status: {response.status_code}")
            self.log_action("CHECK_UPDATE", True)
        except Exception as e:
            self.log(f"⚠️ Xatolik yuz berdi: {e}")
            self.log_action("CHECK_UPDATE", False)

    def check_network_info(self):
        proposal = "Tarmoq konfiguratsiyasi aniqlansinmi (ipconfig)?"
        return proposal, self.get_network_info

    def get_network_info(self):
        try:
            result = subprocess.check_output("ipconfig", shell=True).decode()
            self.log("\n" + result[:500] + "...")
            self.log_action("NETWORK_INFO", True)
        except Exception as e:
            self.log(f"⚠️ Tarmoqni aniqlashda xatolik: {e}")
            self.log_action("NETWORK_INFO", False)

    def suggest_backup(self):
        files = os.listdir(os.getcwd())
        if not files:
            return "Papkada hech qanday fayl yo'q. Backup o'tkazilsinmi?", lambda: self.log("⛔ Fayllar topilmadi.")
        proposal = f"{len(files)} ta fayl zaxira (backup) qilib 'backup/' papkaga ko'chirilsinmi?"
        return proposal, lambda: self.backup_files(files)

    def backup_files(self, files):
        os.makedirs("backup", exist_ok=True)
        copied = 0
        for file in files:
            try:
                if os.path.isfile(file):
                    shutil.copy2(file, "backup")
                    copied += 1
            except Exception as e:
                self.log(f"⚠️ {file} ko'chirishda xatolik: {e}")
        self.log(f"📦 {copied} ta fayl backup qilindi.")
        self.log_action("BACKUP_FILES", True)

    def suggest_code_update(self):
        proposal = "Kodni GitHub'dan yangilashga ruxsat berasizmi?"
        url = "https://raw.githubusercontent.com/AsliddinAbdimuminov/ZEAS_AI/refs/heads/main/main.py"  # bu yerga haqiqiy linkni yozing
        return proposal, lambda: self.fetch_and_replace_code(url)

    def fetch_and_replace_code(self, url):
        try:
            response = requests.get(url)
            with open(__file__, 'w', encoding='utf-8') as f:
                f.write(response.text)
            self.log("✅ Kod yangilandi. Dastur qayta ishga tushirilishi kerak.")
            self.log_action("SELF_UPDATE", True)
        except Exception as e:
            self.log(f"❌ Yangilashda xatolik: {e}")
            self.log_action("SELF_UPDATE", False)

    def approve_action(self):
        self.log("✅ Ruxsat berildi. Agent harakatni bajaryapti...")
        self.current_action()
        self.next_analysis()

    def deny_action(self):
        self.log("❌ Ruxsat berilmadi. Keyingi taklif kutilmoqda.")
        self.log_action("ACTION_DENIED", False)
        self.next_analysis()

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_area.insert(tk.END, timestamp + message + "\n")
        self.log_area.see(tk.END)

    def log_action(self, action, approved):
        with open("agent_log.txt", "a") as log:
            log.write(f"{time.ctime()} | {action} | Approved: {approved}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SelfImprovingAgentApp(root)
    root.mainloop()