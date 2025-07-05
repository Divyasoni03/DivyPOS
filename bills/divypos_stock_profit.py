import os, json, csv
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

# -------- Load Data --------
def load_stock_data():
    try:
        with open("items.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    except:
        status_label.config(text="❌ items.json not found")
        return

    try:
        with open("sales.json", "r", encoding="utf-8") as f:
            sales = json.load(f)
    except:
        sales = []

    for row in tree.get_children():
        tree.delete(row)

    global data_for_pdf
    data_for_pdf = []
    total_profit = 0

    for code, item in items.items():
        metal = item.get("metal", "")
        purity = item.get("purity", "")
        rate = item.get("rate", 0)
        making_charge = item.get("making_charge", 0)
        gst_percent = item.get("gst_percent", 0)
        stock = item.get("stock", 0)

        sold = sum(
            float(entry.get("Weight", "0").replace(" gm", ""))
            for entry in sales if entry.get("Item Code") == code
        )

        remaining = max(stock - sold, 0)
        base = rate * sold
        making = making_charge * sold
        gst = ((base + making) * gst_percent) / 100
        profit = making  # Simplified profit = Making only
        total_profit += profit

        row = [code, metal, purity, stock, round(sold, 2), round(remaining, 2), f"₹{profit:.2f}"]
        data_for_pdf.append(row)
        tree.insert("", "end", values=row)

    profit_label.config(text=f"💰 Total Estimated Profit: ₹{round(total_profit, 2)}")
    status_label.config(text="✅ Stock and Profit Report Loaded")

# -------- PDF Export --------
def export_to_pdf():
    file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file:
        return

    try:
        doc = SimpleDocTemplate(file, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Optional: Add logo
        if os.path.exists("logo.png"):
            elements.append(Image("logo.png", width=80, height=60))

        # Shop Name + Address
        elements.append(Paragraph("<b>DivyPOS Jewellers</b>", styles['Title']))
        elements.append(Paragraph("Main Bazaar, Charkhi Dadri, Haryana", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Table
        table_data = [["Item Code", "Metal", "Purity", "Opening", "Sold", "Remaining", "Profit"]] + data_for_pdf

        # Calculate total profit
        total_profit = sum(float(row[6].replace("₹", "")) for row in data_for_pdf)
        table_data.append(["", "", "", "", "", "Total Profit", f"₹{round(total_profit, 2)}"])

        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gold),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(t)
        doc.build(elements)
        messagebox.showinfo("Export", "✅ PDF exported successfully.")
    except Exception as e:
        messagebox.showerror("PDF Error", str(e))

# -------- GUI --------
root = Tk()
root.title("📊 DivyPOS Stock & Profit Report")
root.geometry("800x500")

Button(root, text="🔄 Load Stock Report", command=load_stock_data).pack(pady=5)
Button(root, text="⬇ Export to PDF", command=export_to_pdf).pack(pady=2)

cols = ["Item Code", "Metal", "Purity", "Opening Stock", "Sold", "Remaining", "Profit"]
tree = ttk.Treeview(root, columns=cols, show="headings")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(pady=10, fill=BOTH, expand=True)

profit_label = Label(root, text="💰 Total Estimated Profit: ₹0.00", font=("Arial", 10, "bold"))
profit_label.pack()

status_label = Label(root, text="", fg="green")
status_label.pack()

data_for_pdf = []  # global to hold latest loaded data
root.mainloop()
