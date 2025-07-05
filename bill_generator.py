# --- (unchanged imports and setup) ---
import json
import os
import platform
import subprocess
import time
from tkinter import *
from tkinter import ttk, messagebox
from datetime import date
from num2words import num2words
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

items_in_bill = []
old_metal_value = 0.0

def print_pdf(path):
    try:
        abs_path = os.path.abspath(path)
        if platform.system() == "Windows":
            # Try Adobe Reader
            acroread = r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
            if os.path.exists(acroread):
                subprocess.Popen([acroread, "/t", abs_path])
            else:
                os.startfile(abs_path, "print")  # fallback to default app
        else:
            subprocess.run(["lp", abs_path])
    except Exception as e:
        messagebox.showerror("🖨️ Print Error", f"Printing failed:\n{e}")

def generate_pdf(customer_data, item_data, old_metal, filename):
    if not os.path.exists("bills"):
        os.makedirs("bills")

    try:
        with open("shop_config.json", "r") as f:
            shop = json.load(f)
    except:
        shop = {
            "shop_name": "Your Shop Name",
            "address": "Your Address",
            "owner": "Owner Name",
            "contact1": "Contact 1",
            "contact2": "Contact 2",
            "logo": ""
        }

    path = f"bills/{filename}"
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    if shop.get("logo") and os.path.exists(shop["logo"]):
        elements.append(Image(shop["logo"], width=50, height=50))
    elements.append(Paragraph(f"<b>{shop['shop_name']}</b>", styles["Title"]))
    elements.append(Paragraph(shop["address"], styles["Normal"]))
    elements.append(Paragraph(f"👤 Owner: {shop['owner']}", styles["Normal"]))
    elements.append(Paragraph(f"📞 {shop['contact1']}", styles["Normal"]))
    if shop.get("contact2"):
        elements.append(Paragraph(f"📞 {shop['contact2']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Date:</b> {customer_data['Date']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Customer:</b> {customer_data['Customer']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Phone:</b> {customer_data['Phone']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Payment Mode:</b> {customer_data['Payment']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Amount Paid:</b> ₹{customer_data['Paid']:.2f}", styles["Normal"]))
    balance_words = num2words(customer_data['Due'], lang='en').capitalize() + " rupees"
    elements.append(Paragraph(f"<b>Balance Due:</b> ₹{customer_data['Due']:.2f} ({balance_words})", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [["S.No", "Item Code", "Metal", "Tunch", "Weight", "Rate", "Making", "GST", "Total"]]
    grand_total = 0
    for idx, item in enumerate(item_data, start=1):
        row = [str(idx), item["Item Code"], item["Metal"], item["Tunch"],
               item["Weight"], item["Rate"], item["Making"], item["GST"], item["Total"]]
        table_data.append(row)
        grand_total += float(item["Total"])
    table_data.append(["", "", "", "", "", "", "", "Total ₹", f"{grand_total:.2f}"])

    tbl = Table(table_data, hAlign='LEFT')
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (-2, -1), (-2, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightyellow),
    ]))
    elements.append(tbl)

    if old_metal:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Old Metal Adjustment</b>", styles["Normal"]))
        elements.append(Paragraph(
            f"{old_metal['Type']} ({old_metal.get('Tunch', 'N/A')}) - {old_metal['Weight']} gm @ ₹{old_metal['Rate']} = ₹{old_metal['Value']:.2f}",
            styles["Normal"]
        ))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("🙏 Thank you for shopping with us!", styles["Normal"]))

    doc.build(elements)
    return path

def calculate_old_metal_value():
    global old_metal_value
    try:
        wt = float(old_metal_weight.get())
        rate = float(old_metal_rate.get())
        val = wt * rate
    except:
        val = 0.0
    old_metal_value = val
    old_adjust_label.config(text=f"♾ Adjustment: ₹{old_metal_value:.2f}")
    update_grand_total()

def update_grand_total():
    total = sum(float(item["Total"]) for item in items_in_bill)
    net = max(0.0, total - old_metal_value)
    total_label.config(text=f"📟 Grand Total: ₹{net:.2f}")
    update_balance()

def update_balance(event=None):
    try:
        paid = float(paid_entry.get())
    except:
        paid = 0.0
    net = sum(float(item["Total"]) for item in items_in_bill) - old_metal_value
    due = max(0.0, net - paid)
    balance_label.config(text=f"💰 Balance Due: ₹{due:.2f}")

def add_item():
    code = code_entry.get().strip()
    wt_txt = weight_entry.get().strip()
    tunch_txt = tunch_entry.get().strip()
    today = str(date.today())
    if not code or not wt_txt:
        result_label.config(text="❌ Code & Weight required"); return
    try: weight = float(wt_txt)
    except: result_label.config(text="❌ Invalid weight"); return

    try:
        with open("items.json", "r") as f: items = json.load(f)
        item = items[code]
        with open("rates.json", "r") as f: rates = json.load(f)
        rate = rates[today][item["metal"]][item["purity"]]
    except:
        result_label.config(text="❌ Code or Rate not found"); return

    base = rate * weight
    making = item["making_charge"] * weight
    gst = ((base + making) * item["gst_percent"]) / 100
    total = base + making + gst

    rec = {
        "Item Code": code, "Metal": item["metal"], "Tunch": tunch_txt,
        "Weight": f"{weight:.2f}", "Rate": f"{rate:.2f}",
        "Making": f"{making:.2f}", "GST": f"{gst:.2f}", "Total": f"{total:.2f}"
    }
    items_in_bill.append(rec)
    item_tree.insert("", END, values=list(rec.values()))
    result_label.config(text="✅ Item added")
    update_grand_total()

    code_entry.delete(0, END)
    weight_entry.delete(0, END)
    tunch_entry.delete(0, END)

def generate_bill():
    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    pay_mode = payment_mode.get()
    try: paid = float(paid_entry.get())
    except: paid = 0.0
    if not name or not phone or not phone.isdigit() or len(phone) != 10:
        result_label.config(text="❌ Valid Name & 10-digit Phone required"); return
    if not items_in_bill:
        result_label.config(text="❌ No items"); return

    total = sum(float(item["Total"]) for item in items_in_bill)
    due = max(0.0, total - old_metal_value - paid)
    customer = {
        "Date": str(date.today()),
        "Customer": name, "Phone": phone,
        "Payment": pay_mode, "Paid": paid, "Due": due
    }
    old = None
    if old_metal_value > 0:
        old = {
            "Type": old_metal_type.get(),
            "Weight": old_metal_weight.get(),
            "Rate": old_metal_rate.get(),
            "Tunch": old_metal_tunch.get(),
            "Value": old_metal_value
        }

    fname = f"{name.replace(' ', '_')}_{customer['Date']}.pdf"
    pdf = generate_pdf(customer, items_in_bill, old, fname)

    while not os.path.exists(pdf):
        time.sleep(0.2)

    result_label.config(text=f"✅ Bill generated\n📄 Saved at: {pdf}\n🖨️ Sending to printer...")
    print_pdf(pdf)

    try:
        with open("shop_config.json", "r") as f:
            shop = json.load(f)
    except:
        shop = {"shop_name": "Our Shop"}

    message = f"Hello {name},\nThank you for shopping at {shop['shop_name']}!\nYour bill of ₹{total - old_metal_value:.2f} is generated.\nPaid: ₹{paid:.2f}, Due: ₹{due:.2f}\nHave a great day! 😊"

    try:
        root.clipboard_clear()
        root.clipboard_append(message)
        root.update()

        result_label.config(text=result_label.cget("text") + "\n📋 Message copied to clipboard.")

        if messagebox.askyesno("📲 WhatsApp", f"Message copied!\nOpen WhatsApp Web for {phone}?"):
            web_url = f"https://wa.me/91{phone}"
            if platform.system() == "Windows":
                os.startfile(web_url)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", web_url])
            else:
                subprocess.Popen(["xdg-open", web_url])
    except Exception as e:
        result_label.config(text=result_label.cget("text") + f"\n⚠️ WhatsApp error: {e}")

# GUI Setup
root = Tk()
root.title("💸 DivyPOS Billing System")
canvas = Canvas(root)
scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
content = Frame(canvas)
content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

Label(content, text="Customer Name").pack()
name_entry = Entry(content); name_entry.pack()
Label(content, text="Phone Number").pack()
phone_entry = Entry(content); phone_entry.pack()
Label(content, text="Payment Mode").pack()
payment_mode = StringVar()
cmb = ttk.Combobox(content, textvariable=payment_mode, state="readonly")
cmb['values'] = ("Cash", "UPI", "Card", "Online", "Other"); cmb.current(0); cmb.pack()
Label(content, text="Amount Paid (₹)").pack()
paid_entry = Entry(content); paid_entry.pack()
paid_entry.insert(0, "0")
paid_entry.bind("<KeyRelease>", update_balance)
Label(content, text="Item Code").pack()
code_entry = Entry(content); code_entry.pack()
Label(content, text="Weight (gm)").pack()
weight_entry = Entry(content); weight_entry.pack()
Label(content, text="Tunch (e.g., 22K)").pack()
tunch_entry = Entry(content); tunch_entry.pack()
Button(content, text="➕ Add Item", command=add_item).pack(pady=5)
cols = ["Item Code", "Metal", "Tunch", "Weight", "Rate", "Making", "GST", "Total"]
item_tree = ttk.Treeview(content, columns=cols, show="headings", height=5)
for c in cols:
    item_tree.heading(c, text=c); item_tree.column(c, width=90)
item_tree.pack(pady=10)

Label(content, text="--- Old Metal Adjustment ---", font=("Arial", 10, "bold")).pack(pady=5)
Label(content, text="Old Metal Type").pack()
old_metal_type = StringVar()
type_menu = ttk.Combobox(content, textvariable=old_metal_type, state="readonly")
type_menu['values'] = ("Gold", "Silver"); type_menu.current(0); type_menu.pack()
Label(content, text="Old Metal Weight (gm)").pack()
old_metal_weight = Entry(content); old_metal_weight.pack()
Label(content, text="Old Metal Rate (₹/gm)").pack()
old_metal_rate = Entry(content); old_metal_rate.pack()
Label(content, text="Old Metal Tunch (e.g., 22K)").pack()
old_metal_tunch = Entry(content); old_metal_tunch.pack()

old_metal_weight.bind("<KeyRelease>", lambda e: calculate_old_metal_value())
old_metal_rate.bind("<KeyRelease>", lambda e: calculate_old_metal_value())

old_adjust_label = Label(content, text="♾ Adjustment: ₹ 0.00", font=("Arial", 10)); old_adjust_label.pack(pady=5)
total_label = Label(content, text="📟 Grand Total: ₹ 0.00", font=("Arial", 12, "bold")); total_label.pack()
balance_label = Label(content, text="💰 Balance Due: ₹ 0.00", font=("Arial", 12, "bold")); balance_label.pack()
Button(content, text="📟 Generate Bill", command=generate_bill).pack(pady=10)
result_label = Label(content, text="", justify=LEFT, font=("Courier", 10)); result_label.pack()

root.mainloop()
