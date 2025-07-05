import json
from tkinter import *

def save_item():
    try:
        code = code_entry.get().strip()
        name = name_entry.get().strip()
        
        if not code or not name:
            status_label.config(text="❌ Item code and name are required.")
            return

        making_charge = float(making_entry.get())
        gst_percent = float(gst_entry.get())
        stock_gm = float(stock_entry.get())
        gross_weight = float(gross_entry.get())
        net_weight = float(net_entry.get())

        item = {
            "name": name,
            "metal": metal_var.get(),
            "purity": purity_var.get(),
            "making_charge": making_charge,
            "gst_percent": gst_percent,
            "stock_gm": stock_gm,
            "gross_weight": gross_weight,
            "net_weight": net_weight
        }

        try:
            with open("items.json", "r") as f:
                items = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            items = {}

        if code in items:
            status_label.config(text=f"⚠️ Overwriting existing item: {code}")

        items[code] = item

        with open("items.json", "w") as f:
            json.dump(items, f, indent=4)

        status_label.config(text=f"✅ Saved: {code}")
    except ValueError:
        status_label.config(text="❌ Please enter valid numeric values.")

# GUI Setup
root = Tk()
root.title("🛒 Item Master Entry")
root.geometry("300x550")
root.resizable(False, False)

Label(root, text="Item Name", font=("Arial", 10)).pack(pady=(10, 0))
name_entry = Entry(root, width=30)
name_entry.pack()

Label(root, text="Item Code", font=("Arial", 10)).pack(pady=(10, 0))
code_entry = Entry(root, width=30)
code_entry.pack()

Label(root, text="Metal Type", font=("Arial", 10)).pack(pady=(10, 0))
metal_var = StringVar()
metal_var.set("Gold")
OptionMenu(root, metal_var, "Gold", "Silver", "Diamond").pack()

Label(root, text="Purity", font=("Arial", 10)).pack(pady=(10, 0))
purity_var = StringVar()
purity_var.set("22K")
OptionMenu(root, purity_var, "22K", "24K", "18K", "999").pack()

Label(root, text="Making Charge (₹/gm)", font=("Arial", 10)).pack(pady=(10, 0))
making_entry = Entry(root, width=30)
making_entry.pack()

Label(root, text="GST (%)", font=("Arial", 10)).pack(pady=(10, 0))
gst_entry = Entry(root, width=30)
gst_entry.pack()

Label(root, text="Stock Quantity (gm)", font=("Arial", 10)).pack(pady=(10, 0))
stock_entry = Entry(root, width=30)
stock_entry.pack()

Label(root, text="Gross Weight (gm)", font=("Arial", 10)).pack(pady=(10, 0))
gross_entry = Entry(root, width=30)
gross_entry.pack()

Label(root, text="Net Weight (gm)", font=("Arial", 10)).pack(pady=(10, 0))
net_entry = Entry(root, width=30)
net_entry.pack()

Button(
    root, text="💾 Save Item", command=save_item,
    bg="green", fg="white", font=("Arial", 10, "bold")
).pack(pady=15)

status_label = Label(root, text="", fg="blue", font=("Arial", 10))
status_label.pack()

root.mainloop()
