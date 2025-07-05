import json
import os
import subprocess
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ----- PDF Generator -----
def generate_pdf(entry):
    try:
        with open("shop_config.json", "r") as f:
            shop = json.load(f)
    except:
        shop = {
            "shop_name": "Your Shop Name",
            "address": "Your Address",
            "owner": "Owner",
            "contact1": "1234567890",
            "contact2": "",
            "logo": ""
        }

    if not os.path.exists("bills"):
        os.makedirs("bills")

    customer_name = entry.get("Customer", "Unknown").replace(" ", "_")
    filename = f"{customer_name}_{entry.get('Date', 'NoDate')}_RE.pdf"
    path = os.path.join("bills", filename)

    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Logo if available
    if shop.get("logo") and os.path.exists(shop["logo"]):
        elements.append(Image(shop["logo"], width=60, height=60))

    # Shop Info
    elements.append(Paragraph(f"<b>{shop.get('shop_name')}</b>", styles["Title"]))
    elements.append(Paragraph(shop.get("address"), styles["Normal"]))
    elements.append(Paragraph(f"👤 Owner: {shop.get('owner')}", styles["Normal"]))
    elements.append(Paragraph(f"📞 {shop.get('contact1')}", styles["Normal"]))
    if shop.get("contact2"):
        elements.append(Paragraph(f"📞 {shop['contact2']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Bill Info
    elements.append(Paragraph(f"<b>Date:</b> {entry['Date']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Customer:</b> {entry['Customer']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Phone:</b> {entry['Phone']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Table
    table_data = [
        ["Item Code", "Metal", "Tunch", "Weight", "Rate", "Making", "GST", "Total"],
        [
            entry.get("Item Code", ""),
            entry.get("Metal", ""),
            entry.get("Tunch", ""),
            entry.get("Weight", ""),
            entry.get("Rate", ""),
            entry.get("Making", ""),
            entry.get("GST", ""),
            entry.get("Total", ""),
        ]
    ]

    table = Table(table_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("🙏 Thank you for shopping with us!", styles["Normal"]))

    doc.build(elements)
    return path

# ----- Actions -----
def load_sales():
    customer_query = customer_entry.get().strip().lower()
    phone_query = phone_entry.get().strip()

    try:
        with open("sales.json", "r") as f:
            data = json.load(f)
    except:
        status_label.config(text="❌ sales.json not found")
        return

    results = []
    for entry in data:
        if customer_query and customer_query not in entry.get("Customer", "").lower():
            continue
        if phone_query and phone_query not in entry.get("Phone", ""):
            continue
        results.append(entry)

    for row in tree.get_children():
        tree.delete(row)

    for e in results:
        tree.insert("", "end", values=(
            e.get("Date", ""),
            e.get("Customer", ""),
            e.get("Phone", ""),
            e.get("Item Code", ""),
            e.get("Metal", ""),
            e.get("Total", "")
        ), tags=(json.dumps(e),))

    status_label.config(text=f"✅ {len(results)} record(s) loaded.")

def regenerate_selected():
    selected = tree.selection()
    if not selected:
        status_label.config(text="❌ No row selected")
        return

    row_data = tree.item(selected[0])["tags"][0]
    entry = json.loads(row_data)

    pdf_path = generate_pdf(entry)
    status_label.config(text=f"✅ PDF generated: {pdf_path}")

    # Ask to print
    if messagebox.askyesno("Print", "Do you want to print the bill now?"):
        try:
            if os.name == 'nt':  # Windows
                try:
                    acrobat = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
                    if os.path.exists(acrobat):
                        subprocess.run([acrobat, '/N', '/T', pdf_path], shell=True)
                    else:
                        os.startfile(pdf_path, "print")
                except Exception as e:
                    messagebox.showerror("Print Error", f"❌ Could not print: {e}")
            else:
                subprocess.run(["lp", pdf_path])
        except Exception as e:
            messagebox.showerror("Print Error", f"❌ Could not print: {e}")

# ----- GUI -----
root = Tk()
root.title("📄 Re-generate Bill PDF")
root.geometry("850x520")

Label(root, text="Customer Name (optional):").pack()
customer_entry = Entry(root)
customer_entry.pack()

Label(root, text="Mobile Number (optional):").pack()
phone_entry = Entry(root)
phone_entry.pack()

Button(root, text="🔍 Search Sales", command=load_sales).pack(pady=5)

cols = ["Date", "Customer", "Phone", "Item Code", "Metal", "Total"]
tree = ttk.Treeview(root, columns=cols, show="headings", height=10)
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(fill=BOTH, expand=True, padx=10)

Button(root, text="🧾 Re-generate PDF", command=regenerate_selected).pack(pady=5)

status_label = Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
