import os
import zipfile
import io
import json
import re
import platform
import schedule
import time
import threading
from datetime import datetime
from tkinter import Tk, Button, Label, messagebox
from tkinter.simpledialog import askstring
from tkinter.filedialog import asksaveasfilename
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import pandas as pd

# 🔧 Configurations
JSON_KEY_FILE = "C:\\Users\\DIVYA SONI\\Downloads\\divypos-cloud-backup-b2c458d417be.json"
SALES_FILE = "sales.json"
FOLDER_ID = "1kS9urrLaDqEAv548tTMwh7qn7Pskw1rH"
OWNER_EMAIL_FILE = "owner_email.json"
ADMIN_PASSWORD = "admin@123"

# 📁 Open file after export
def open_file(filepath):
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":
            os.system(f"open \"{filepath}\"")
        else:
            os.system(f"xdg-open \"{filepath}\"")
    except Exception as e:
        print(f"❌ Could not open file:\n{e}")

# 📤 Upload to Google Drive (permanent)
def upload_to_drive():
    try:
        creds = service_account.Credentials.from_service_account_file(
            JSON_KEY_FILE, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_name = f"sales_backup_{timestamp}.zip"

        with zipfile.ZipFile(zip_name, "w") as zipf:
            zipf.write(SALES_FILE)

        file_metadata = {"name": zip_name, "parents": [FOLDER_ID]}
        media = MediaFileUpload(zip_name, mimetype="application/zip", resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        backup_info = {
            "email": get_owner_email(),
            "filename": zip_name,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        history_file = "backup_history.json"
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

        history.append(backup_info)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        messagebox.showinfo("Backup Successful", f"✅ Backup uploaded:\n{zip_name}")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Upload failed:\n{e}")

# 📥 Restore latest from Drive
def restore_from_drive():
    try:
        creds = service_account.Credentials.from_service_account_file(
            JSON_KEY_FILE, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)

        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and name contains 'sales_backup_'",
            orderBy="createdTime desc",
            fields="files(id, name)",
            pageSize=1
        ).execute()

        items = results.get("files", [])
        if not items:
            messagebox.showwarning("Not Found", "❌ No backup file found.")
            return

        file_id = items[0]["id"]
        request = service.files().get_media(fileId=file_id)
        zip_name = "latest_downloaded_backup.zip"
        fh = io.FileIO(zip_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            zip_ref.extractall(".")

        messagebox.showinfo("Restore Successful", "✅ sales.json restored successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Restore failed:\n{e}")

# 📥 Restore specific backup file
def restore_specific_backup():
    try:
        creds = service_account.Credentials.from_service_account_file(
            JSON_KEY_FILE, scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds)

        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and name contains 'sales_backup_'",
            orderBy="createdTime desc",
            fields="files(id, name, createdTime)",
            pageSize=20
        ).execute()

        files = results.get("files", [])
        if not files:
            messagebox.showinfo("No Backups", "❌ No backups found in Drive.")
            return

        options = [f"{file['name']} ({file['createdTime'][:19].replace('T', ' ')})" for file in files]
        selection = askstring("Select Backup", "Enter exact file name to restore:\n\n" + "\n".join(options[:10]))

        if not selection:
            return

        matched = next((f for f in files if f["name"] == selection.strip()), None)
        if not matched:
            messagebox.showerror("Not Found", "❌ Backup not found.")
            return

        file_id = matched["id"]
        zip_path = "selected_backup.zip"
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(zip_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(".")

        messagebox.showinfo("Restored", f"✅ Restored from:\n{matched['name']}")
    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to restore:\n{e}")

# 👤 Get Owner Email
def get_owner_email():
    try:
        with open(OWNER_EMAIL_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("email", "")
    except:
        return ""

# 📬 Email Validator
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

# 👤 GUI Email Setter
def prompt_set_owner_email(event=None):
    current = get_owner_email()
    if current and (not event or not event.state & 0x0001):
        messagebox.showinfo("Not Allowed", f"⚠️ Owner already set to:\n{current}\n\nHold Shift & click to override.")
        return

    if current:
        password = askstring("Admin Override", "Enter admin password to change:", show="*")
        if password != ADMIN_PASSWORD:
            messagebox.showerror("Access Denied", "❌ Incorrect password.")
            return

    email = askstring("Set Owner Email", "Enter new owner email:")
    if email:
        if is_valid_email(email):
            with open(OWNER_EMAIL_FILE, "w", encoding="utf-8") as f:
                json.dump({"email": email}, f, indent=2)
            messagebox.showinfo("Success", f"✅ Owner email set to: {email}")
            owner_email_var.config(text=f"👤 Owner Email: {email}")
        else:
            messagebox.showerror("Invalid", "❌ Enter a valid email address.")

# 📜 Show Backup History
def view_backup_history():
    history_file = "backup_history.json"
    if not os.path.exists(history_file):
        messagebox.showinfo("No History", "❌ No backup history found.")
        return
    with open(history_file, "r", encoding="utf-8") as f:
        history = json.load(f)
    if not history:
        messagebox.showinfo("Empty", "📭 No backup records yet.")
        return
    message = "🕒 Backup History (latest 5):\n\n"
    for entry in reversed(history[-5:]):
        message += f"📦 {entry['filename']}\n👤 {entry['email']}\n📅 {entry['datetime']}\n\n"
    messagebox.showinfo("Backup History", message)

# 🕒 Auto Backup
def auto_backup_job():
    upload_to_drive()

def run_scheduler():
    schedule.every().day.at("19:00").do(auto_backup_job)
    while True:
        schedule.run_pending()
        time.sleep(60)

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# 📄 Export to CSV
def export_to_csv():
    try:
        with open(SALES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            messagebox.showwarning("Empty", "❌ No data found in sales.json")
            return
        df = pd.DataFrame(data)

        filename = asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"sales_export_{datetime.now().strftime('%Y-%m-%d')}.csv",
            title="Save CSV File"
        )
        if filename:
            df.to_csv(filename, index=False)
            messagebox.showinfo("Exported", f"✅ Exported to:\n{filename}")
            open_file(filename)
    except Exception as e:
        messagebox.showerror("Error", f"❌ Export failed:\n{e}")

# 📊 Export to Excel
def export_to_excel():
    try:
        with open(SALES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            messagebox.showwarning("Empty", "❌ No data found in sales.json")
            return
        df = pd.DataFrame(data)

        filename = asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"sales_export_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            title="Save Excel File"
        )
        if filename:
            df.to_excel(filename, index=False)
            messagebox.showinfo("Exported", f"✅ Exported to:\n{filename}")
            open_file(filename)
    except Exception as e:
        messagebox.showerror("Error", f"❌ Export failed:\n{e}")

# ✅ ✅ ✅ Add This Function for divypos_report.py compatibility
def set_owner_email(email):
    if not is_valid_email(email):
        raise ValueError("❌ Invalid email address")
    with open(OWNER_EMAIL_FILE, "w", encoding="utf-8") as f:
        json.dump({"email": email}, f, indent=2)

# 🖥️ GUI Setup
root = Tk()
root.title("DivyPOS Cloud Backup")
root.geometry("400x500")

Label(root, text="☁ Cloud Backup System", font=("Arial", 14, "bold")).pack(pady=10)
owner_email_var = Label(root, text=f"👤 Owner Email: {get_owner_email()}", font=("Arial", 10))
owner_email_var.pack(pady=5)

Button(root, text="📤 Backup Now", command=upload_to_drive, width=25, bg="green", fg="white").pack(pady=10)
Button(root, text="🔄 Restore Latest Backup", command=restore_from_drive, width=25, bg="blue", fg="white").pack(pady=5)
Button(root, text="📂 Restore Specific Backup", command=restore_specific_backup, width=25, bg="brown", fg="white").pack(pady=5)

owner_email_button = Button(root, text="👤 Set Owner Email", bg="orange", fg="black", width=25)
owner_email_button.pack(pady=5)
owner_email_button.bind("<Button-1>", prompt_set_owner_email)

Button(root, text="📄 Export to CSV", command=export_to_csv, width=25, bg="darkgray", fg="black").pack(pady=5)
Button(root, text="📊 Export to Excel", command=export_to_excel, width=25, bg="purple", fg="white").pack(pady=5)
Button(root, text="📜 View Backup History", command=view_backup_history, width=25, bg="teal", fg="white").pack(pady=5)

Label(root, text="🕒 Auto Backup Daily at 7:00 PM", font=("Arial", 9, "italic")).pack(pady=15)

root.mainloop()
