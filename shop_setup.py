import json
from tkinter import *
from tkinter import filedialog

def save_shop_info():
    shop_name = shop_name_entry.get().strip()
    address = address_entry.get("1.0", END).strip()
    owner = owner_entry.get().strip()
    contact1 = contact1_entry.get().strip()
    contact2 = contact2_entry.get().strip()
    logo_path = logo_path_var.get().strip()

    if not shop_name or not address or not owner or not contact1:
        status_label.config(text="❌ Please fill all required fields")
        return

    shop_data = {
        "shop_name": shop_name,
        "address": address,
        "owner": owner,
        "contact1": contact1,
        "contact2": contact2,
        "logo": logo_path
    }

    with open("shop_config.json", "w") as f:
        json.dump(shop_data, f, indent=4)

    status_label.config(text="✅ Shop information saved!")

def browse_logo():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    logo_path_var.set(file_path)

# GUI
root = Tk()
root.title("🏪 Shop Setup - DivyPOS")

Label(root, text="Shop Name *").pack()
shop_name_entry = Entry(root, width=50)
shop_name_entry.pack()

Label(root, text="Address *").pack()
address_entry = Text(root, height=3, width=50)
address_entry.pack()

Label(root, text="Owner Name *").pack()
owner_entry = Entry(root, width=50)
owner_entry.pack()

Label(root, text="Contact Number 1 *").pack()
contact1_entry = Entry(root, width=50)
contact1_entry.pack()

Label(root, text="Contact Number 2 (optional)").pack()
contact2_entry = Entry(root, width=50)
contact2_entry.pack()

Label(root, text="Logo Path (optional)").pack()
logo_path_var = StringVar()
Entry(root, textvariable=logo_path_var, width=50).pack()
Button(root, text="📁 Browse Logo", command=browse_logo).pack(pady=5)

Button(root, text="💾 Save Info", command=save_shop_info).pack(pady=10)

status_label = Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
