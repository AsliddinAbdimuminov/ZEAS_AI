import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
import requests
import shutil
import subprocess
from openai import OpenAI


client = OpenAI(api_key="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")  # <-- Bu yerga API kalitingizni kiriting

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
        self.log_area = scrolledtext.ScrolledText(root, height=10, width=70)
        self.log_area.pack(pady=10)

        # ChatGPT agent taklifi oynasi
        self.gpt_frame = tk.LabelFrame(root, text="💬 ChatGPT Taklifi")
        self.gpt_frame.pack(fill="both", expand="yes", padx=10, pady=5)

        self.gpt_input = tk.Text(self.gpt_frame, height=3, width=60)
        self.gpt_input.pack(padx=5, pady=5)

        self.gpt_send = tk.Button(self.gpt_frame, text="➤ So'rov yuborish", command=self.ask_chatgpt)
        self.gpt_send.pack(pady=5)

        self.gpt_code_area = scrolledtext.ScrolledText(self.gpt_frame, height=10, width=70)
        self.gpt_code_area.pack(pady=5)

        self.insert_code_btn = tk.Button(self.gpt_frame, text="✅ Kodni joylashtirish", command=self.insert_gpt_code)
        self.insert_code_btn.pack(pady=5)

        # AutoFix paneli
        self.fix_frame = tk.LabelFrame(root, text="🔧 AutoFix (Kod tuzatish)")
        self.fix_frame.pack(fill="both", expand="yes", padx=10, pady=5)

        self.fix_target_label = tk.Label(self.fix_frame, text="Tuzatiladigan fayl nomi (masalan, agent.py):")
        self.fix_target_label.pack()

        self.fix_target_entry = tk.Entry(self.fix_frame, width=50)
        self.fix_target_entry.insert(0, "gpt_module.py")
        self.fix_target_entry.pack(padx=5, pady=5)

        self.fix_button = tk.Button(self.fix_frame, text="🔍 AutoFix so‘rovi yuborish", command=self.analyze_and_fix)
        self.fix_button.pack(pady=5)

        self.apply_fix_button = tk.Button(self.fix_frame, text="✅ Tuzatmani qabul qilish", command=self.insert_fixed_code)
        self.apply_fix_button.pack(pady=5)

        self.fixed_code_area = scrolledtext.ScrolledText(self.fix_frame, height=10, width=70)
        self.fixed_code_area.pack(pady=5)

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
        url = "https://raw.githubusercontent.com/username/repo/main/agent.py"
        return proposal, lambda: self.fetch_and_replace_code(url)

    def fetch_and_replace_code(self, url):
        try:
            response = requests.get(url)
            with open(__file__, ' 'w', encoding='utf-8') as f:
                f.write(response.text)
            self.log("✅ Kod yangilandi. Dastur qayta ishga tushirilishi kerak.")
            self.log_action("SELF_UPDATE", True)
        except Exception as e:
            self.log(f"❌ Yangilashda xatolik: {e}")
            self.log_action("SELF_UPDATE", False)

    def ask_chatgpt(self):
        prompt = self.gpt_input.get("1.0", tk.END).strip()
        if not prompt:
            self.log("⚠️ So‘rov bo‘sh.")
            return
        self.log("🧠 ChatGPT bilan aloqa o‘rnatilmoqda...")
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            self.gpt_code_area.delete("1.0", tk.END)
            self.gpt_code_area.insert(tk.END, content)
            self.log("✅ ChatGPT'dan javob olindi.")
        except Exception as e:
            self.log(f"❌ ChatGPT xatosi: {e}")

    def insert_gpt_code(self):
        new_code = self.gpt_code_area.get("1.0", tk.END).strip()
        if not new_code:
            self.log("⚠️ Kod mavjud emas.")
            return
        file_path = "gpt_module.py"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("""# ==== GPT tomonidan taklif qilingan kod ====\n""" + new_code + "\n# ==== /GPT kod yakuni ====\n")
        self.log(f"✅ Kod '{file_path}' fayliga saqlandi.")
        messagebox.showinfo("Kodni qo‘shish", f"Yangi kod '{file_path}' faylida saqlandi. Qo‘lda chaqirilishi mumkin.")
        self.log_action("GPT_CODE_INSERTED", True)

    def analyze_and_fix(self):
        file_name = self.fix_target_entry.get().strip()
        if not os.path.isfile(file_name):
            self.log("❌ Fayl topilmadi.")
            return
        with open(file_name, 'r', encoding='utf-8') as f:
            code = f.read()
        prompt = f"Iltimos, quyidagi Python kodni tahlil qilib xatoliklarni tuzating va yangilangan kodni qaytaring:\n\n{code}"
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            fixed = response.choices[0].message.content
            self.fixed_code_area.delete("1.0", tk.END)
            self.fixed_code_area.insert(tk.END, fixed)
            self.log("🧰 Tuzatilgan kod tayyor.")
        except Exception as e:
            self.log(f"❌ AutoFix xatosi: {e}")

    def insert_fixed_code(self):
        file_name = self.fix_target_entry.get().strip()
        fixed_code = self.fixed_code_area.get("1.0", tk.END).strip()
        if not fixed_code:
            self.log("⚠️ Tuzatmani kiritish uchun kod yo'q.")
            return
        try:
            shutil.copy2(file_name, file_name + ".bak")
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            self.log(f"✅ '{file_name}' yangilandi. '.bak' nusxa saqlandi.")
            self.log_action("AUTOFIX_APPLIED", True)
        except Exception as e:
            self.log(f"❌ Faylni yangilashda xatolik: {e}")
            self.log_action("AUTOFIX_FAILED", False)

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
