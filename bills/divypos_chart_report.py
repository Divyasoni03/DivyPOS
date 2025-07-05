import json
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# ---------- Load and Process Sales Data ----------
def load_sales_data():
    try:
        with open("sales.json", "r") as f:
            return json.load(f)
    except:
        return []

def group_sales(data, mode="customer"):
    grouped = defaultdict(float)
    for entry in data:
        name = entry.get("Customer", "Unknown") if mode == "customer" else entry.get("Date", "Unknown")
        try:
            total = float(entry.get("Total", "0").replace("₹", ""))
            grouped[name] += total
        except:
            pass
    return grouped

# ---------- Plotting ----------
def show_chart():
    mode = group_by.get()
    filter_val = filter_entry.get().strip()

    raw_data = load_sales_data()
    if not raw_data:
        status_label.config(text="❌ sales.json not found or empty")
        return

    if filter_val:
        raw_data = [r for r in raw_data if filter_val in r.get("Date", "")]

    grouped_data = group_sales(raw_data, mode)
    if not grouped_data:
        status_label.config(text="❌ No data found for given filter")
        return

    labels = list(grouped_data.keys())
    values = list(grouped_data.values())

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Customer" if mode == "customer" else "Date")
    plt.ylabel("Total Sales (₹)")
    plt.title(f"Total Sales ({'Customer-wise' if mode == 'customer' else 'Day-wise'})")
    plt.tight_layout()
    plt.show()

    status_label.config(text=f"✅ {len(labels)} entries shown.")

def save_chart():
    mode = group_by.get()
    raw_data = load_sales_data()
    filter_val = filter_entry.get().strip()
    if filter_val:
        raw_data = [r for r in raw_data if filter_val in r.get("Date", "")]
    grouped_data = group_sales(raw_data, mode)
    if not grouped_data:
        status_label.config(text="❌ No data to export")
        return

    labels = list(grouped_data.keys())
    values = list(grouped_data.values())

    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
    if not file_path:
        return

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color='green')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("Customer" if mode == "customer" else "Date")
    plt.ylabel("Total Sales (₹)")
    plt.title(f"Total Sales Chart - {mode.capitalize()}")
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    status_label.config(text=f"✅ Chart saved to {file_path}")

# ---------- GUI ----------
root = Tk()
root.title("📊 DivyPOS Chart Report")
root.geometry("600x400")

Label(root, text="🔎 Filter (YYYY-MM or leave blank):").pack()
filter_entry = Entry(root)
filter_entry.insert(0, datetime.today().strftime("%Y-%m"))
filter_entry.pack(pady=5)

Label(root, text="📂 Group By:").pack()
group_by = StringVar(value="customer")
ttk.Combobox(root, textvariable=group_by, values=["customer", "date"]).pack(pady=5)

Button(root, text="📈 Show Chart", command=show_chart).pack(pady=10)
Button(root, text="💾 Save Chart as PNG", command=save_chart).pack(pady=5)

status_label = Label(root, text="", fg="green")
status_label.pack(pady=10)

root.mainloop()
