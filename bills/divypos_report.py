# 🔄 Required Imports
import os, sys, json, csv
from tkinter import *
from tkinter import ttk, filedialog, messagebox, Scrollbar
from datetime import date

# ✅ Imports from other modules
sys.path.append(os.path.abspath(".."))
from user_auth import verify_user
from cloud_backup import upload_to_drive, restore_from_drive, set_owner_email

# 🔍 Load and Save
def load_sales_json():
    if not os.path.exists("sales.json"):
        with open("sales.json", "w", encoding="utf-8") as f:
            json.dump([], f)
    try:
        with open("sales.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "❌ sales.json is corrupted.")
        return []

def save_sales_json(data):
    with open("sales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# 📅 Daily Report Tab
def create_daily_tab(notebook):
    frame = Frame(notebook)
    notebook.add(frame, text="📅 Daily Report")

    Label(frame, text="Enter Date (YYYY-MM-DD):").pack()
    date_entry = Entry(frame)
    date_entry.insert(0, str(date.today()))
    date_entry.pack()

    cols = ["Date", "Customer", "Phone", "Item Code", "Metal", "Weight", "Total"]
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill=BOTH, expand=True)

    scrollbar = Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    total_label = Label(frame, text="💰 Total Sales: ₹0.00", font=("Arial", 10, "bold"))
    total_label.pack()
    status_label = Label(frame, text="", fg="green")
    status_label.pack()

    def load_report():
        if not verify_user("admin"): return
        d = date_entry.get().strip()
        records = [e for e in load_sales_json() if e.get("Date") == d]
        for row in tree.get_children(): tree.delete(row)
        if not records:
            status_label.config(text="❌ No records found.")
            return
        total = sum(float(e.get("Total", "0").replace("₹", "") or 0) for e in records)
        for e in records:
            tree.insert("", "end", values=(e["Date"], e["Customer"], e["Phone"], e["Item Code"], e["Metal"], e["Weight"], e["Total"].replace("₹", "")))
        total_label.config(text=f"💰 Total Sales: ₹{round(total, 2)}")
        status_label.config(text=f"✅ {len(records)} entries loaded.")

    def export_csv():
        if not verify_user("admin"): return
        if not messagebox.askyesno("Export", "Export to CSV?"): return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not file: return
        d = date_entry.get().strip()
        records = [e for e in load_sales_json() if e.get("Date") == d]
        try:
            with open(file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for e in records:
                    writer.writerow([e["Date"], e["Customer"], f"'{e['Phone']}", e["Item Code"], e["Metal"], e["Weight"], e["Total"].replace("₹", "")])
            status_label.config(text="✅ Exported successfully.")
        except Exception as err:
            status_label.config(text=f"❌ Error: {err}")

    Button(frame, text="📂 Load Report", command=load_report).pack(pady=5)
    Button(frame, text="⬇ Export CSV", command=export_csv).pack()

# 📆 Monthly Report Tab
def create_monthly_tab(notebook):
    frame = Frame(notebook)
    notebook.add(frame, text="📆 Monthly Report")

    month_var, year_var = StringVar(), StringVar()

    Label(frame, text="Select Month:").pack()
    ttk.Combobox(frame, textvariable=month_var, values=[f"{m:02d}" for m in range(1, 13)], state="readonly").pack()
    month_var.set(f"{date.today().month:02d}")

    Label(frame, text="Select Year:").pack()
    ttk.Combobox(frame, textvariable=year_var, values=[str(y) for y in range(2020, 2031)], state="readonly").pack()
    year_var.set(str(date.today().year))

    cols = ["Date", "Customer", "Phone", "Item Code", "Metal", "Weight", "Total"]
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill=BOTH, expand=True)

    scrollbar = Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    total_label = Label(frame, text="💰 Total Sales: ₹0.00", font=("Arial", 10, "bold"))
    total_label.pack()
    status_label = Label(frame, text="", fg="green")
    status_label.pack()

    def load_monthly():
        if not verify_user("admin"): return
        prefix = f"{year_var.get()}-{month_var.get()}"
        records = [e for e in load_sales_json() if e.get("Date", "").startswith(prefix)]
        for row in tree.get_children(): tree.delete(row)
        if not records:
            status_label.config(text="❌ No records found.")
            return
        total = sum(float(e.get("Total", "0").replace("₹", "") or 0) for e in records)
        for e in records:
            tree.insert("", "end", values=(e["Date"], e["Customer"], e["Phone"], e["Item Code"], e["Metal"], e["Weight"], e["Total"].replace("₹", "")))
        total_label.config(text=f"💰 Total Sales: ₹{round(total, 2)}")
        status_label.config(text=f"✅ {len(records)} entries loaded.")

    def export_csv():
        if not verify_user("admin"): return
        if not messagebox.askyesno("Export", "Export to CSV?"): return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not file: return
        prefix = f"{year_var.get()}-{month_var.get()}"
        records = [e for e in load_sales_json() if e.get("Date", "").startswith(prefix)]
        try:
            with open(file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for e in records:
                    writer.writerow([e["Date"], e["Customer"], f"'{e['Phone']}", e["Item Code"], e["Metal"], e["Weight"], e["Total"].replace("₹", "")])
            status_label.config(text="✅ Exported successfully.")
        except Exception as err:
            status_label.config(text=f"❌ Error: {err}")

    Button(frame, text="📂 Load Report", command=load_monthly).pack(pady=5)
    Button(frame, text="⬇ Export CSV", command=export_csv).pack()

# 🔍 Search, Edit, Delete
def create_search_tab(notebook):
    frame = Frame(notebook)
    notebook.add(frame, text="🔍 Search by Mobile")

    Label(frame, text="Enter Mobile Number:").pack()
    search_entry = Entry(frame)
    search_entry.pack()

    cols = ["Date", "Customer", "Phone", "Item Code", "Metal", "Weight", "Total"]
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill=BOTH, expand=True)

    scrollbar = Scrollbar(frame, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=RIGHT, fill=Y)

    result_label = Label(frame, text="", fg="green")
    result_label.pack()

    # Entry fields
    entries, selected_index = {}, [None]
    for col in cols:
        row = Frame(frame)
        Label(row, text=col + ":", width=10, anchor=W).pack(side=LEFT)
        ent = Entry(row, width=40)
        ent.pack(side=LEFT, fill=X, expand=True)
        row.pack(padx=5, pady=2)
        entries[col] = ent

    def perform_search():
        if not verify_user("staff"): return
        keyword = search_entry.get().strip()
        records = load_sales_json()
        matches = [(i, e) for i, e in enumerate(records) if keyword == e.get("Phone", "")]
        for row in tree.get_children(): tree.delete(row)
        if not matches:
            result_label.config(text="❌ No matching records.")
            return
        for i, e in matches:
            tree.insert("", "end", iid=str(i), values=(e["Date"], e["Customer"], e["Phone"], e["Item Code"], e["Metal"], e["Weight"], e["Total"].replace("₹", "")))
        result_label.config(text=f"✅ {len(matches)} match(es) found.")

    def on_row_select(event):
        selected = tree.focus()
        if not selected: return
        values = tree.item(selected, "values")
        for k, v in zip(cols, values):
            entries[k].delete(0, END)
            entries[k].insert(0, v)
        selected_index[0] = int(selected)

    def update_record():
        if selected_index[0] is None:
            messagebox.showerror("No Selection", "❌ Select a record.")
            return
        if not verify_user("admin"): return
        data = load_sales_json()
        i = selected_index[0]
        for col in cols:
            data[i][col] = entries[col].get().strip()
        save_sales_json(data)
        perform_search()
        result_label.config(text="✅ Record updated.")

    def delete_record():
        if selected_index[0] is None:
            messagebox.showerror("No Selection", "❌ Select a record.")
            return
        if not verify_user("admin"): return
        if not messagebox.askyesno("Confirm", "Delete this record?"): return
        data = load_sales_json()
        del data[selected_index[0]]
        save_sales_json(data)
        perform_search()
        result_label.config(text="✅ Record deleted.")

    tree.bind("<ButtonRelease-1>", on_row_select)
    Button(frame, text="🔎 Search", command=perform_search).pack(pady=5)
    Button(frame, text="✏️ Update Record", command=update_record, bg="#007ACC", fg="white").pack(pady=2)
    Button(frame, text="❌ Delete Record", command=delete_record, bg="#B22222", fg="white").pack(pady=2)

# ---------------- Main Window ----------------
root = Tk()
root.title("📊 DivyPOS Full Report System")
root.geometry("900x700")

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

create_daily_tab(notebook)
create_monthly_tab(notebook)
create_search_tab(notebook)

# ☁ Backup/Restore/Email
email_entry = Entry(root, width=40)
email_entry.pack(pady=5)
email_entry.insert(0, "Enter owner email (e.g. owner@example.com)")

def trigger_backup():
    if verify_user("admin"):
        try:
            upload_to_drive()
            messagebox.showinfo("Backup", "✅ sales.json backed up.")
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e))

def trigger_restore():
    if verify_user("admin"):
        if not messagebox.askyesno("Restore", "Confirm restore?"): return
        try:
            restore_from_drive()
            messagebox.showinfo("Restore", "✅ sales.json restored.")
        except Exception as e:
            messagebox.showerror("Restore Failed", str(e))

def trigger_set_email():
    if verify_user("admin"):
        email = email_entry.get().strip()
        if not email or "@" not in email:
            messagebox.showerror("Invalid", "❌ Enter valid email.")
            return
        try:
            set_owner_email(email)
            messagebox.showinfo("Email Set", f"✅ Owner email set to: {email}")
        except Exception as e:
            messagebox.showerror("Failed", str(e))

Button(root, text="☁ Backup to Drive", command=trigger_backup, bg="#007ACC", fg="white", font=("Arial", 10, "bold")).pack(pady=3)
Button(root, text="☁ Restore from Drive", command=trigger_restore, bg="#228B22", fg="white", font=("Arial", 10, "bold")).pack(pady=3)
Button(root, text="📧 Set Owner Email", command=trigger_set_email, bg="#AA336A", fg="white", font=("Arial", 10, "bold")).pack(pady=3)

root.mainloop()
