import json
from tkinter import *
from datetime import date, datetime

def save_rate():
    try:
        today = date_entry.get().strip()
        
        # Validate date format
        try:
            datetime.strptime(today, "%Y-%m-%d")
        except ValueError:
            status_label.config(text="❌ Invalid date format. Use YYYY-MM-DD.")
            return

        metal = metal_var.get()
        purity = purity_var.get()

        try:
            rate = float(rate_entry.get())
        except ValueError:
            status_label.config(text="❌ Enter a valid numeric rate.")
            return

        try:
            with open("rates.json", "r") as f:
                all_rates = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_rates = {}

        if today not in all_rates:
            all_rates[today] = {}
        if metal not in all_rates[today]:
            all_rates[today][metal] = {}

        all_rates[today][metal][purity] = rate

        with open("rates.json", "w") as f:
            json.dump(all_rates, f, indent=4)

        status_label.config(text=f"✅ Saved {metal} - {purity} rate for {today}")
    except Exception as e:
        status_label.config(text=f"❌ Error: {str(e)}")

# GUI
root = Tk()
root.title("💰 Daily Metal Rate Entry")
root.geometry("300x300")
root.resizable(False, False)

Label(root, text="Date (YYYY-MM-DD)", font=("Arial", 10)).pack(pady=(10, 0))
date_entry = Entry(root, width=30)
date_entry.insert(0, str(date.today()))
date_entry.pack()

Label(root, text="Metal Type", font=("Arial", 10)).pack(pady=(10, 0))
metal_var = StringVar()
metal_var.set("Gold")
OptionMenu(root, metal_var, "Gold", "Silver").pack()

Label(root, text="Purity", font=("Arial", 10)).pack(pady=(10, 0))
purity_var = StringVar()
purity_var.set("22K")
OptionMenu(root, purity_var, "22K", "24K", "18K", "999").pack()

Label(root, text="Rate (₹/gm)", font=("Arial", 10)).pack(pady=(10, 0))
rate_entry = Entry(root, width=30)
rate_entry.pack()

Button(root, text="💾 Save Rate", command=save_rate, bg="green", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

status_label = Label(root, text="", font=("Arial", 10), fg="blue")
status_label.pack()

root.mainloop()
